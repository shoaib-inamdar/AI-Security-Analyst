# Architecture — AI Security Analyst & Remediation Platform

> **Version:** 2.0 | **Last Updated:** 2026-08
> This document is the authoritative reference for system design decisions.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Layers](#2-architecture-layers)
3. [Component Responsibilities](#3-component-responsibilities)
4. [Data Flow — End to End](#4-data-flow--end-to-end)
5. [Agent Architecture](#5-agent-architecture)
6. [Database Schema Overview](#6-database-schema-overview)
7. [Security Architecture](#7-security-architecture)
8. [Key Design Decisions](#8-key-design-decisions)

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  Next.js 15 Dashboard  │  GitHub App Webhook  │  REST API      │
└────────────────────────┬───────────────────────┬────────────────┘
                         │                       │
┌────────────────────────▼───────────────────────▼────────────────┐
│                    API GATEWAY (FastAPI)                        │
│        Auth Middleware · Rate Limiting · Request Logging        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
        ┌─────────────────────────┼──────────────────────┐
        ▼                         ▼                      ▼
┌──────────────┐        ┌──────────────────┐   ┌──────────────────┐
│ Scan Service │        │ Analysis Service │   │Remediation Service│
│              │        │                  │   │                  │
│ Orchestrates │        │ LangGraph Agent  │   │ LangGraph Agent  │
│ scanners via │        │ Evidence Verify  │   │ Sandbox + Rescan │
│ Celery tasks │        │ (deterministic)  │   │ Fix Certificate  │
└──────┬───────┘        └──────────────────┘   └──────────────────┘
       │
┌──────▼────────────────────────────────────────────────────────┐
│                   WORKER LAYER (Celery + Redis)                │
│                                                               │
│  Semgrep Worker │ Bandit Worker │ pip-audit │ npm-audit       │
│  Trivy Worker   │ detect-secrets│ AI Worker │ Fix Worker      │
└──────┬────────────────────────────────────────────────────────┘
       │
┌──────▼────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
│  PostgreSQL 16 (primary) │ Redis 7 (queue+cache) │ MinIO (S3) │
└───────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Layers

### 2.1 Client Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Dashboard | Next.js 15, TypeScript, Tailwind | Primary user interface |
| GitHub App | GitHub API | Webhook receiver, PR comments |
| External API | REST/JSON | Programmatic access for CI/CD |

### 2.2 API Gateway Layer

**Technology:** Python, FastAPI, Uvicorn

Responsibilities:
- JWT authentication and session validation
- Role-based authorization (ADMIN, SECURITY_LEAD, DEVELOPER, VIEWER)
- Request validation via Pydantic schemas
- Rate limiting (per user, per endpoint)
- Structured request/response logging
- GitHub webhook HMAC-SHA256 signature verification

### 2.3 Core Services Layer

**Scan Service** — orchestrates the scanner pipeline:
1. Clone or update repository
2. Detect languages present
3. Select applicable scanners
4. Dispatch Celery tasks for each scanner
5. Collect SARIF results
6. Trigger normalization + deduplication
7. Trigger AI analysis queue

**Analysis Service** — AI-powered finding analysis:
1. Receive normalized finding
2. Invoke Analysis Agent (LangGraph)
3. Run deterministic evidence verifier
4. Apply confidence adjustments
5. Route low-confidence findings to human review queue
6. Persist structured analysis

**Remediation Service** — fix proposal and verification:
1. Receive approved finding for remediation
2. Invoke Fix Verification Agent (LangGraph)
3. Sandbox setup → apply fix → rescan → test
4. Issue verification certificate
5. Notify approvers

### 2.4 Worker Layer

**Technology:** Celery 5, Redis 7

Each scanner runs as an independent Celery task, enabling:
- Parallel execution (all scanners run simultaneously)
- Per-scanner timeout enforcement (90 seconds max)
- Graceful failure (one scanner failing does not stop others)
- Result storage even from partial scans

Task queues:
- `scan_queue` — scanner tasks (high throughput, short duration)
- `ai_queue` — AI analysis tasks (rate-limited, longer duration)
- `fix_queue` — fix verification tasks (isolated, sandbox required)

### 2.5 Data Layer

| Store | Technology | Data |
|-------|-----------|------|
| Primary DB | PostgreSQL 16 | All structured data |
| Queue/Cache | Redis 7 | Celery broker + result backend |
| Object Storage | MinIO (S3-compatible) | SARIF files, scan artifacts, compliance PDFs |

---

## 3. Component Responsibilities

### 3.1 Scanner Runners

Each scanner runner implements the `BaseScanner` abstract interface:

```
BaseScanner
├── run(repo_path: Path) → ScannerResult
├── output_format: "sarif" | "json" | "text"
└── to_sarif(raw_output: dict) → dict   # only if output_format != "sarif"
```

| Runner | Output | Conversion Needed |
|--------|--------|------------------|
| `semgrep_runner.py` | Native SARIF | No |
| `bandit_runner.py` | JSON | Yes → SARIF |
| `pip_audit_runner.py` | JSON | Yes → SARIF |
| `npm_audit_runner.py` | JSON | Yes → SARIF |
| `trivy_runner.py` | Native SARIF | No |
| `detect_secrets_runner.py` | JSON | Yes → SARIF |

### 3.2 SARIF Normalizer (Deterministic)

Converts all SARIF output to `NormalizedFinding`:

```
SARIF result → extract location → extract rule → map CWE
    → generate fingerprint → create NormalizedFinding
```

Fingerprint algorithm (deterministic, reproducible):
```python
fingerprint = sha256(f"{file_path}:{line}:{vuln_category}").hexdigest()[:16]
```

### 3.3 Deduplicator (Deterministic)

Merges findings with the same fingerprint from multiple scanners:

```
findings: [A(semgrep), B(bandit), C(semgrep)]
A.fingerprint == B.fingerprint  →  merge: A gets bandit source added
confidence = min(0.6 + (num_sources - 1) * 0.15, 0.95)
```

### 3.4 Evidence Verifier (Deterministic — Never Agentic)

Validates every AI-cited line number against the actual source file:

```python
for citation in analysis.evidence_citations:
    actual_line = read_file(repo_path, citation.line_number)
    similarity = compute_similarity(actual_line, citation.code_snippet)
    citation.verified = similarity > 0.70
    if not citation.verified:
        analysis.confidence_score -= 0.15
```

This component is **deterministic by design**. It must never be replaced by an LLM-based verifier.

### 3.5 LLM Factory

Returns a `BaseChatModel` instance based on configuration. All agent code depends only on `BaseChatModel`, never on a specific provider class. Provider selection is a configuration concern.

---

## 4. Data Flow — End to End

### 4.1 Scan Triggered (via webhook or dashboard)

```
1. HTTP POST /api/scans  (or GitHub webhook)
2. FastAPI validates auth + request
3. Scan record created in PostgreSQL (status: QUEUED)
4. Celery task dispatched: run_scan(scan_id, repo_url)
5. HTTP 202 Accepted returned immediately
```

### 4.2 Scanner Pipeline (Celery Worker)

```
6.  Clone repository to temp directory
7.  Detect languages (file extensions analysis)
8.  Select applicable scanners
9.  Dispatch parallel Celery sub-tasks per scanner
10. Each scanner: run → SARIF output → store artifact in MinIO
11. All scanner tasks complete (or timeout)
12. Scan status updated: SCANNING → NORMALIZING
```

### 4.3 Normalization & Deduplication

```
13. Load all SARIF artifacts from MinIO
14. SARIF Normalizer: each result → NormalizedFinding
15. Deduplicator: merge same fingerprints, update confidence
16. Findings persisted to PostgreSQL
17. Scan status: NORMALIZING → ANALYZING
```

### 4.4 AI Analysis (per finding, parallel)

```
18. Each finding dispatched to ai_queue
19. Analysis Agent (LangGraph) invoked
20. Agent gathers context (Tree-sitter, call graph, FP history)
21. Agent produces FindingAnalysis (structured output)
22. Evidence Verifier runs (deterministic)
23. Confidence adjusted based on verification
24. If confidence < 0.7: finding routed to human review queue
25. Analysis persisted to PostgreSQL
26. Scan status: ANALYZING → COMPLETE
```

### 4.5 Fix Verification (on demand or automatic)

```
27. Fix Verification Agent invoked
28. Sandbox created (isolated directory copy)
29. Fix applied to sandbox
30. Scanner re-run on modified file
31. If original finding eliminated: run test suite
32. If tests pass: issue FixVerificationRecord
33. If finding not eliminated: critique + retry (max 3)
34. After max retries: mark UNVERIFIABLE
35. Clean up sandbox
```

### 4.6 Approval Workflow

```
36. Security lead reviews finding in dashboard
37. Lead approves / rejects / marks FP
38. Approval event written to audit log (append-only)
39. If approved: developer receives notification
40. Developer applies fix to real repository
41. New scan triggered on changed files
42. Original finding confirmed resolved
```

---

## 5. Agent Architecture

### 5.1 Analysis Agent

**Framework:** LangGraph  
**Purpose:** Multi-step context gathering and vulnerability reasoning

```
Nodes:
  gather_context     → Extract code, callers, callees via Tree-sitter
  initial_analysis   → LLM call: produce draft FindingAnalysis
  check_confidence   → Evaluate if confidence threshold met
  enrich_context     → Gather additional context (tool call)
  produce_output     → Final structured FindingAnalysis
  evidence_verifier  → Deterministic line-number verification

Edges:
  gather_context     → initial_analysis
  initial_analysis   → check_confidence
  check_confidence   → enrich_context   (if confidence < 0.6 and iterations < 2)
  check_confidence   → produce_output   (if confidence >= 0.6 or iterations >= 2)
  enrich_context     → initial_analysis
  produce_output     → evidence_verifier
  evidence_verifier  → END
```

**Human-in-the-loop:** `interrupt()` after `evidence_verifier` if confidence < 0.7.

### 5.2 Fix Verification Agent

**Framework:** LangGraph  
**Purpose:** Iterative fix improvement with sandbox re-scanning

```
Nodes:
  generate_fix       → LLM: propose code fix for finding
  apply_sandbox      → Deterministic: apply diff to sandbox copy
  rescan_file        → Deterministic: run scanner on changed file
  check_eliminated   → Deterministic: original finding present?
  run_tests          → Deterministic: execute test suite in sandbox
  critique_fix       → LLM: analyze why fix failed, suggest improvement
  store_certificate  → Deterministic: write FixVerificationRecord
  mark_unverifiable  → Deterministic: mark as UNVERIFIABLE

Edges:
  generate_fix       → apply_sandbox
  apply_sandbox      → rescan_file
  rescan_file        → check_eliminated
  check_eliminated   → critique_fix         (if finding still present)
  check_eliminated   → run_tests            (if finding eliminated)
  critique_fix       → generate_fix         (if iterations < 3)
  critique_fix       → mark_unverifiable    (if iterations >= 3)
  run_tests          → store_certificate    (if tests pass)
  run_tests          → store_certificate    (if tests fail, with regression warning)
```

---

## 6. Database Schema Overview

### Core Tables

| Table | Primary Key | Key Columns |
|-------|------------|-------------|
| `organizations` | `id` (UUID) | `name`, `slug`, `created_at` |
| `users` | `id` (UUID) | `email`, `password_hash`, `role`, `org_id` |
| `repositories` | `id` (UUID) | `url`, `name`, `language`, `org_id` |
| `scans` | `id` (UUID) | `repo_id`, `status`, `triggered_by`, `started_at`, `completed_at` |
| `scanner_results` | `id` (UUID) | `scan_id`, `scanner`, `sarif_artifact_path`, `duration_ms` |
| `findings` | `id` (UUID) | `scan_id`, `fingerprint`, `file_path`, `line_start`, `severity`, `cwe_ids`, `scanner_sources`, `confidence` |
| `ai_analyses` | `id` (UUID) | `finding_id`, `explanation`, `data_flow`, `confidence_score`, `model_provider`, `model_name` |
| `evidence_citations` | `id` (UUID) | `analysis_id`, `line_number`, `code_snippet`, `role`, `verified` |
| `fix_verification_records` | `id` (UUID) | `finding_id`, `fix_diff`, `verified`, `iterations`, `scanner_output_before`, `scanner_output_after`, `verified_at` |
| `approvals` | `id` (UUID) | `finding_id`, `reviewer_id`, `decision`, `reason`, `decided_at` |
| `audit_events` | `id` (UUID) | `actor_id`, `action`, `resource_type`, `resource_id`, `timestamp_utc`, `ip_address`, `evidence_json` |
| `false_positive_history` | `id` (UUID) | `org_id`, `rule_id`, `file_pattern`, `reason`, `marked_by`, `marked_at` |

### Key Constraints

- `audit_events`: No UPDATE or DELETE permissions for application user. Append-only enforced at PostgreSQL row-security level.
- `findings.fingerprint`: Unique index per `scan_id` for fast deduplication lookup.
- `fix_verification_records`: `verified_at` is immutable once set.

---

## 7. Security Architecture

### Authentication
- JWT access tokens (15-minute expiry)
- Refresh tokens (7-day expiry, rotated on use)
- Passwords hashed with bcrypt (cost factor 12)
- No plaintext secrets stored anywhere

### Authorization
- RBAC enforced at FastAPI dependency level
- Every endpoint declares required role
- Organization isolation: users can only access their org's data
- Multi-tenant query filter applied at ORM layer

### API Security
- Rate limiting: 100 req/min per user, 20 req/min for scan triggers
- Input validation: all inputs validated by Pydantic before processing
- GitHub webhook: HMAC-SHA256 signature verified before processing
- SQL injection: impossible via SQLAlchemy ORM parameterized queries

### Secret Management
- All secrets in environment variables (never in code or logs)
- `.env` excluded from Git via `.gitignore`
- Production: secrets via Docker secrets or a secrets manager

### Sandbox Security
- Fix verification runs in isolated directory copy
- No network access from sandbox
- Temporary files cleaned up in `finally` block (always)
- Scanner processes run with limited permissions

---

## 8. Key Design Decisions

### Decision 1: Why SARIF as the internal format?

SARIF (Static Analysis Results Interchange Format) is an OASIS standard supported by GitHub, Azure DevOps, and most major SAST tools. Using SARIF as the internal normalization target means:
- New scanners only need to produce SARIF (often already do)
- Normalized findings from any scanner are structurally identical
- Deduplication works across all scanners with a single algorithm

**Alternative considered:** Custom internal format. Rejected because it would require a custom converter for every scanner and would not interoperate with external tools.

### Decision 2: Why LangGraph over plain LangChain?

Plain LangChain chains are linear. Security analysis requires cycles:
- "Analyze → insufficient confidence → gather more context → analyze again"
- "Propose fix → apply → rescan → fix failed → critique → propose again"

LangGraph's directed graph model with conditional edges and cycle support is the correct abstraction. LangGraph also provides first-class `interrupt()` for human-in-the-loop gates, which maps directly to the approval workflow requirement.

### Decision 3: Why keep evidence verification deterministic?

The evidence verifier checks whether AI-cited line numbers exist in the actual file and contain what the AI claims. This is a simple string comparison. Making it agentic would:
- Introduce non-determinism into a compliance-critical step
- Make it impossible to explain exactly why a citation was accepted or rejected
- Potentially allow the agent to rationalize accepting a bad citation

**The rule:** If a step can be done deterministically, it must be done deterministically.

### Decision 4: Why uv over pip?

`uv` produces a `uv.lock` file that guarantees identical dependency trees across all environments. For a security tool, reproducible builds are not optional — you must be able to prove that the scanner you ran in development is identical to the one in CI and production. Additionally, `uv` resolves and installs dependencies 100× faster, which matters for CI/CD pipelines.

### Decision 5: Why provider-agnostic LLM?

Anthropic Claude is the best model for code security analysis but requires payment from the first token. A provider-agnostic design allows:
- Development with Google Gemini (free, 1,500 req/day)
- High-speed testing with Groq (free, Llama 3.1 70B)
- Fully offline work with Ollama (local models, no API key)
- Production switch to Claude with one config change

This also protects the project from vendor lock-in.
