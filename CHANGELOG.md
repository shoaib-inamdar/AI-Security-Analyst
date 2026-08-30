# CHANGELOG

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Initial project structure
- FastAPI backend skeleton
- Next.js 15 frontend scaffold
- Docker Compose setup (PostgreSQL 16, Redis 7, MinIO)
- Semgrep runner with native SARIF output
- Bandit runner with SARIF conversion
- SARIF normalizer and deduplicator
- Provider-agnostic LLM factory (Gemini, Groq, Ollama, Anthropic)
- Deterministic evidence verifier
- uv as package manager (replaced pip + venv)
- LangGraph dependency added (agents in Phase 2)

### Architecture
- Phase 1 (single-shot LLM baseline) complete design
- Phase 2 (LangGraph Analysis Agent) design complete
- Phase 3 (Fix Verification Agent) design complete

---

## [0.1.0] — TBD

_Initial release — Phase 1 MVP baseline_

---

<!-- Links will be added as releases are tagged -->
