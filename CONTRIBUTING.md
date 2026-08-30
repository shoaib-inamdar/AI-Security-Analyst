# Contributing to AI Security Analyst & Remediation Platform

Thank you for your interest in contributing. This document covers everything you need to know to make a contribution.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Security Contributions](#security-contributions)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to uphold these standards.

---

## Development Setup

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | https://python.org |
| uv | latest | `winget install astral-sh.uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20 LTS | https://nodejs.org |
| Docker Desktop | 24+ | https://docker.com/products/docker-desktop |
| Git | 2.x | https://git-scm.com |

### First-Time Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/security-analyst-platform.git
cd security-analyst-platform

# 2. Install Python 3.12 via uv (if not already installed)
uv python install 3.12

# 3. Install all dependencies (creates .venv automatically)
uv sync --all-extras

# 4. Copy environment config
cp .env.example .env
# Edit .env — minimum required for development:
#   LLM_PROVIDER=gemini
#   GOOGLE_API_KEY=your-free-key-from-aistudio.google.com

# 5. Start infrastructure
docker compose up -d

# 6. Run database migrations
uv run alembic upgrade head

# 7. Start backend
uv run uvicorn backend.main:app --reload --port 8000

# 8. Start frontend (new terminal)
cd frontend && npm install && npm run dev
```

### Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Run tests
uv run pytest tests/ -v

# Check code style
uv run ruff check .
uv run ruff format --check .
```

---

## Branching Strategy

We use a simple **feature-branch workflow**.

```
main           ← always deployable, protected
  └── feature/phase-2-analysis-agent
  └── fix/evidence-verifier-line-count-bug
  └── docs/update-architecture-diagram
  └── test/add-deduplicator-edge-cases
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<short-description>` | `feature/analysis-agent` |
| Bug fix | `fix/<short-description>` | `fix/sarif-parser-null-region` |
| Documentation | `docs/<short-description>` | `docs/architecture-agent-section` |
| Test | `test/<short-description>` | `test/deduplicator-cross-scanner` |
| Refactor | `refactor/<short-description>` | `refactor/llm-factory` |

### Rules

- Never commit directly to `main`
- One logical change per branch
- Keep branches short-lived (merge within a week if possible)
- Delete branch after merging

---

## Commit Conventions

We follow **Conventional Commits** (https://conventionalcommits.org).

### Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code change that is not a feature or fix |
| `chore` | Build process, dependency update |
| `perf` | Performance improvement |
| `ci` | CI/CD configuration |

### Examples

```
feat(scanners): add pip-audit runner with SARIF conversion
fix(evidence-verifier): handle empty file edge case
docs(architecture): add Fix Verification Agent graph diagram
test(deduplicator): add cross-scanner fingerprint collision test
chore(deps): update langgraph to 0.2.0
```

### Rules

- Subject line: max 72 characters, imperative mood, no period at end
- Body: explain **why**, not what (the diff shows what)
- Reference issues: `Closes #42` or `Fixes #17` in footer

---

## Pull Request Process

### Before Opening a PR

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] Code formatted: `uv run ruff format .`
- [ ] Type hints valid: `uv run mypy backend/`
- [ ] New code has tests (see Testing Requirements)
- [ ] Documentation updated if behavior changed

### PR Description Template

When opening a PR, use this template:

```markdown
## What

Brief description of what this PR does.

## Why

Why is this change needed? Link to issue if applicable.

## How

Key implementation decisions made.

## Testing

How was this tested? What edge cases were covered?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or breaking change noted below)
```

### Review Process

1. Open PR targeting `main`
2. CodeRabbit will automatically review within minutes
3. Address CodeRabbit comments
4. At least one human review required before merge
5. Squash-merge preferred for clean history

---

## Code Style

### Python

We use **Ruff** for both linting and formatting (replaces flake8, isort, black).

```bash
# Check
uv run ruff check .

# Fix automatically
uv run ruff check . --fix

# Format
uv run ruff format .
```

Configuration in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "S", "B", "A", "C4", "PT"]
```

### Python Conventions

- Type hints required on all public functions
- Docstrings required on all public classes and functions
- Async functions preferred for I/O operations
- No `print()` statements — use `logging` or `structlog`
- Constants in `UPPER_CASE`
- Private methods prefixed with `_`

### TypeScript / Next.js

- ESLint + Prettier enforced
- TypeScript strict mode enabled
- No `any` types without explicit justification in comment
- Components in PascalCase, utilities in camelCase

```bash
cd frontend
npm run lint
npm run format
```

---

## Testing Requirements

Every code change must include appropriate tests.

### Coverage Requirements

| Component | Minimum Coverage |
|-----------|----------------|
| Scanner runners | 90% |
| SARIF normalizer | 95% |
| Deduplicator | 90% |
| Evidence verifier | 95% |
| API endpoints | 85% |
| Agent tools | 80% |

### Test Types

**Unit tests** — test a single function/class in isolation, mock all external dependencies:
```bash
uv run pytest tests/unit/ -v
```

**Integration tests** — test multiple components together, use real Docker services:
```bash
uv run pytest tests/integration/ -v --docker
```

**Scanner tests** — run against the intentionally vulnerable sample file:
```bash
uv run pytest tests/test_scanners/ -v
```

### Test File Naming

```
tests/
├── unit/
│   ├── test_sarif_normalizer.py
│   ├── test_deduplicator.py
│   └── test_evidence_verifier.py
├── integration/
│   ├── test_scan_pipeline.py
│   └── test_analysis_agent.py
└── test_scanners/
    ├── sample_vulnerable.py   ← intentionally vulnerable fixture
    ├── test_semgrep_runner.py
    └── test_bandit_runner.py
```

### Mocking LLM Calls

Never make real LLM API calls in tests. Use LangChain's `FakeListChatModel`:

```python
from langchain_core.language_models.fake import FakeListChatModel

@pytest.fixture
def mock_llm():
    return FakeListChatModel(responses=["...your expected response..."])
```

---

## Security Contributions

### Reporting Vulnerabilities

**Do not open a public GitHub issue for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

### Security-Sensitive Code Areas

Extra care is required when modifying:

| Area | Risk | Required Review |
|------|------|----------------|
| `backend/core/security.py` | JWT forgery, auth bypass | Security lead sign-off |
| `backend/api/webhooks.py` | Webhook signature bypass | Security lead sign-off |
| `remediation/sandbox.py` | Sandbox escape | Security lead sign-off |
| `backend/models/audit_log.py` | Audit log integrity | Security lead sign-off |
| Any authentication flow | Auth bypass | Security lead sign-off |

### What Makes a Good Security Contribution

- Principle of least privilege: request only what you need
- Defense in depth: don't rely on a single control
- Fail safe: errors should deny access, not grant it
- All user inputs validated before processing
- No secrets in logs or error messages
