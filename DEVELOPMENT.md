# Development Guide

This guide covers everything needed to run the platform locally for development.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Environment Variables](#environment-variables)
- [Running Services](#running-services)
- [Common Workflows](#common-workflows)
- [Database](#database)
- [Testing](#testing)
- [Debugging](#debugging)

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12+ | Managed by uv |
| uv | latest | Python package manager |
| Node.js | 20 LTS | For frontend |
| Docker Desktop | 24+ | PostgreSQL, Redis, MinIO |
| Git | 2.x | Version control |

### Install uv

```bash
# Windows (PowerShell)
winget install astral-sh.uv

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Initial Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/security-analyst-platform.git
cd security-analyst-platform

# Install Python 3.12
uv python install 3.12

# Install all dependencies (creates .venv automatically)
uv sync --all-extras

# Copy environment config
cp .env.example .env

# Edit .env — minimum for local dev:
# LLM_PROVIDER=gemini
# GOOGLE_API_KEY=<your-free-key-from-aistudio.google.com>

# Start Docker services
docker compose up -d

# Apply database migrations
uv run alembic upgrade head

# Verify everything works
uv run pytest tests/unit/ -v
```

---

## Environment Variables

### Getting a Free LLM API Key

**Google Gemini (recommended for development):**
1. Go to https://aistudio.google.com
2. Click "Get API key"
3. Create a key — no credit card required
4. Set `GOOGLE_API_KEY=<your-key>` in `.env`

**Groq (alternative — very fast):**
1. Go to https://console.groq.com
2. Sign up free
3. Create API key
4. Set `GROQ_API_KEY=<your-key>` and `LLM_PROVIDER=groq` in `.env`

**Ollama (fully offline):**
```bash
# Windows
winget install Ollama.Ollama

# Pull a model (one-time download)
ollama pull llama3.2          # 2GB, general purpose
ollama pull qwen2.5-coder     # 4GB, better for code

# Set in .env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

### Key Environment Variables

```env
# --- LLM Configuration ---
LLM_PROVIDER=gemini          # gemini | groq | ollama | anthropic
LLM_MODEL=gemini-2.0-flash

# Provider-specific keys (only set the one you use)
GOOGLE_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# --- Application ---
APP_ENV=development
SECRET_KEY=dev-secret-change-in-production
DEBUG=true

# --- Database ---
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/security_analyst

# --- Redis ---
REDIS_URL=redis://localhost:6379/0

# --- Storage ---
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# --- LangSmith (optional, for agent tracing) ---
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=security-analyst-dev
```

---

## Running Services

### Start All Infrastructure (Docker)

```bash
docker compose up -d
```

Services started:
- PostgreSQL 16 on port `5432`
- Redis 7 on port `6379`
- MinIO on ports `9000` (API) and `9001` (Console UI)

### Check Service Health

```bash
docker compose ps
# All services should show: healthy or running

# MinIO console: http://localhost:9001 (admin / minioadmin)
```

### Start Backend API

```bash
uv run uvicorn backend.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

### Start Celery Workers

```bash
# Scan worker (scanner tasks)
uv run celery -A workers.celeryconfig worker -Q scan_queue --loglevel=info

# AI analysis worker (separate terminal)
uv run celery -A workers.celeryconfig worker -Q ai_queue --loglevel=info

# Optional: Celery Flower (task monitoring UI)
uv run celery -A workers.celeryconfig flower --port=5555
# http://localhost:5555
```

### Start Frontend

```bash
cd frontend
npm install       # first time only
npm run dev
# http://localhost:3000
```

### Stop Everything

```bash
# Stop Docker services (keeps data)
docker compose stop

# Stop and remove containers + volumes (clean slate)
docker compose down -v
```

---

## Common Workflows

### Run a Scan on a Test Repository

```bash
# Start all services first, then:
curl -X POST http://localhost:8000/api/scans \
  -H "Authorization: Bearer <your-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/WebGoat/WebGoat", "branch": "main"}'
```

### Add a New Dependency

```bash
# Runtime dependency
uv add <package-name>

# Development-only dependency
uv add --dev <package-name>

# Commit the updated pyproject.toml and uv.lock
git add pyproject.toml uv.lock
git commit -m "chore(deps): add <package-name>"
```

### Update All Dependencies

```bash
uv sync --upgrade
# Review changes in uv.lock before committing
```

### Create a Database Migration

```bash
# After modifying a SQLAlchemy model:
uv run alembic revision --autogenerate -m "add false positive history table"
# Review the generated migration in database/migrations/versions/
uv run alembic upgrade head
```

### Manually Run a Scanner

```bash
# Semgrep on a file
uv run semgrep --config p/python tests/test_scanners/sample_vulnerable.py

# Bandit on a file
uv run bandit tests/test_scanners/sample_vulnerable.py

# With SARIF output
uv run semgrep --config p/python --sarif tests/test_scanners/sample_vulnerable.py
```

---

## Database

### Connect to PostgreSQL

```bash
docker exec -it security_analyst_postgres psql -U postgres -d security_analyst
```

### Useful Queries

```sql
-- List all findings from latest scan
SELECT f.id, f.file_path, f.line_start, f.severity, f.confidence
FROM findings f
ORDER BY f.created_at DESC
LIMIT 20;

-- Check audit log
SELECT actor_id, action, resource_type, timestamp_utc
FROM audit_events
ORDER BY timestamp_utc DESC
LIMIT 50;
```

### Reset Database (Development Only)

```bash
docker compose down -v   # removes volumes
docker compose up -d     # fresh start
uv run alembic upgrade head
```

---

## Testing

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test Suite

```bash
uv run pytest tests/unit/ -v              # unit tests only
uv run pytest tests/test_scanners/ -v     # scanner tests
uv run pytest tests/integration/ -v       # integration (needs Docker)
uv run pytest tests/ -k "deduplicator"   # tests matching keyword
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=backend --cov=scanners --cov-report=html
# Open htmlcov/index.html in browser
```

### Test the Intentionally Vulnerable File

```bash
uv run pytest tests/test_scanners/test_semgrep_runner.py -v
# Should find: SQL injection, weak hash, hardcoded secret
```

---

## Debugging

### FastAPI Debugging

With `--reload` enabled, FastAPI restarts on file changes. For a debugger:

```bash
# VS Code: use the Python debugger with uvicorn
# Add to .vscode/launch.json:
{
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["backend.main:app", "--reload", "--port", "8000"]
}
```

### Celery Task Debugging

```bash
# Watch task output in real time
uv run celery -A workers.celeryconfig worker -Q scan_queue --loglevel=debug

# Check task status
uv run celery -A workers.celeryconfig inspect active
uv run celery -A workers.celeryconfig inspect reserved
```

### LangGraph Agent Debugging

Enable LangSmith tracing (free tier available at https://smith.langchain.com):

```env
# In .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-langsmith-key>
LANGCHAIN_PROJECT=security-analyst-dev
```

All agent runs will appear in the LangSmith UI with full step-by-step traces.

### Common Issues

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `Connection refused` on port 5432 | PostgreSQL not running | `docker compose up -d` |
| `ModuleNotFoundError` | venv not active or dep not installed | `uv sync` |
| `uvicorn backend.main:app` fails | Wrong working directory | Run from project root |
| Semgrep rules download slow | First run downloads rules | Wait, or pre-download: `semgrep --update-check` |
| Celery task stuck in PENDING | Redis not running | `docker compose up -d redis` |
| LLM returning errors | Missing or invalid API key | Check `.env` API key |
