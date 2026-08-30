# 🏗️ PHASE 1 — FOUNDATION (v2 — with uv + Free LLM)
### AI Security Analyst & Remediation Platform

> Read each concept section **before** doing the task. When you finish the checklist, say **"Phase 1 done"**.

---

## 🎯 Goal

By the end of Phase 1 you will have:
- A **uv**-managed Python project
- **FastAPI** running and responding
- **Next.js** running in the browser
- **PostgreSQL + Redis + MinIO** running via Docker
- **Semgrep** and **Bandit** producing real findings
- A **free LLM API key** configured and tested
- A **complete Git repository** with all production documentation files
- The full project structure ready for Phase 2

---

## 🧠 New Concepts in v2

### 🧠 What is `uv`?

`uv` is a Python package manager that replaces `pip`, `venv`, and `pip-tools`.

> Think of it like **Cargo** (Rust) or **npm** (Node.js) — one tool that handles packages AND the environment.

Why we use `uv`:
- **100× faster** than pip for installing packages
- Creates a `uv.lock` file — everyone on the team gets identical packages
- Manages Python versions too (`uv python install 3.12`)
- One command to install everything: `uv sync`

```bash
# Old way (pip)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn

# New way (uv) — simpler and faster
uv init my-project
uv add fastapi uvicorn
uv run uvicorn main:app  # no activation needed
```

### 🧠 Free LLM Options (No Credit Card Needed)

We **don't** require Anthropic Claude during development. Use these free options:

| Provider | Free Limit | Quality | Setup |
|----------|-----------|---------|-------|
| **Google Gemini Flash** | 1,500 req/day | ⭐⭐⭐⭐⭐ | API key from aistudio.google.com |
| **Groq (Llama 3.1 70B)** | 6,000 req/day | ⭐⭐⭐⭐ | API key from console.groq.com |
| **Ollama (local)** | Unlimited | ⭐⭐⭐ | No key, runs on your machine |

**My recommendation for Phase 1:** Start with **Google Gemini** — free, no credit card, best quality of the free options.

Getting your key: Go to https://aistudio.google.com → click "Get API key" → copy it.

---

## 📁 Files to Create in Phase 1

```
security-analyst-platform/
├── pyproject.toml              ← uv project config + dependencies
├── uv.lock                     ← auto-generated, commit this
├── .env.example                ← config template
├── .env                        ← real config (never committed)
├── .gitignore
├── .coderabbit.yaml
├── docker-compose.yml
├── Makefile                    ← developer shortcuts
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── SECURITY.md
├── DEVELOPMENT.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── backend/
│   └── main.py
└── tests/
    └── test_scanners/
        └── sample_vulnerable.py
```

---

## 🪜 Step-by-Step Tasks

---

### ✅ TASK 1 — Check Installed Tools

Open PowerShell and verify:

```powershell
python --version      # need 3.11 or 3.12
node --version        # need 18 or 20
git --version         # need 2.x
docker --version      # need 24+
```

Install `uv`:
```powershell
winget install astral-sh.uv
# Restart PowerShell after install
uv --version          # should print a version number
```

**⚠️ If `winget` isn't available:** Run this in PowerShell:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

---

### ✅ TASK 2 — Create Project with uv

```powershell
cd "C:\Users\HP\Documents\AI Security Analyst"

# Initialize project with uv
uv init security-analyst-platform
cd security-analyst-platform

# Install Python 3.12 (uv manages this for you)
uv python install 3.12
uv python pin 3.12

# Create the folder structure
mkdir backend\api, backend\core, backend\models, backend\schemas, backend\services
mkdir workers, scanners
mkdir database\migrations
mkdir tests\test_api, tests\test_scanners, tests\test_workers
mkdir docs, docker\postgres
mkdir ai\agents ai\prompts
mkdir remediation
```

**Verify:**
```powershell
tree /F    # should show the full structure
```

---

### ✅ TASK 3 — Add Dependencies with uv

Instead of `requirements.txt`, we use `pyproject.toml`. Run these commands — uv adds packages to it automatically:

```powershell
# Web framework
uv add fastapi "uvicorn[standard]" pydantic pydantic-settings

# Database
uv add sqlalchemy alembic asyncpg psycopg2-binary

# Background jobs
uv add celery redis

# Security / Auth
uv add "python-jose[cryptography]" "passlib[bcrypt]" python-multipart

# HTTP + env
uv add httpx python-dotenv

# LLM — all providers (use whichever you configure)
uv add langchain-google-genai langchain-groq langchain-ollama langchain-anthropic
uv add langgraph langsmith

# Dev tools (not installed in production)
uv add --dev pytest pytest-asyncio ruff mypy
```

**Verify `pyproject.toml` was created and has all packages.**

**⚠️ Common mistake:** Running `pip install` instead of `uv add`. Always use `uv` commands in this project.

---

### ✅ TASK 4 — Create `.env.example`

Create this file at the project root:

```env
# ============================================================
# AI Security Analyst Platform — Environment Configuration
# ============================================================
# Copy this file to .env and fill in your values.
# NEVER commit .env to Git.
# ============================================================

# --- Application ---
APP_NAME=AI Security Analyst Platform
APP_ENV=development
SECRET_KEY=change-this-to-a-random-string-in-production
DEBUG=true

# --- LLM Provider (choose one) ---
# Options: gemini | groq | ollama | anthropic
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash

# Google Gemini (free — get key at aistudio.google.com)
GOOGLE_API_KEY=

# Groq (free — get key at console.groq.com)
GROQ_API_KEY=

# Ollama (local, no key needed)
OLLAMA_BASE_URL=http://localhost:11434

# Anthropic Claude (paid — production use)
ANTHROPIC_API_KEY=

# --- LangSmith (optional — free tier at smith.langchain.com)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=security-analyst-dev

# --- Database ---
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/security_analyst
DATABASE_SYNC_URL=postgresql://postgres:postgres@localhost:5432/security_analyst

# --- Redis ---
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# --- Storage (MinIO) ---
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=security-analyst

# --- JWT ---
JWT_SECRET_KEY=change-this-jwt-secret-too
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- GitHub App (Phase 5) ---
GITHUB_APP_ID=
GITHUB_APP_PRIVATE_KEY=
GITHUB_WEBHOOK_SECRET=
```

Now copy it:
```powershell
Copy-Item .env.example .env
# Then open .env and set your GOOGLE_API_KEY
```

---

### ✅ TASK 5 — Create `docker-compose.yml`

```yaml
version: "3.9"

services:

  postgres:
    image: postgres:16-alpine
    container_name: security_analyst_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: security_analyst
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: security_analyst_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: security_analyst_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

Start it:
```powershell
docker compose up -d
docker compose ps    # all should show "healthy" or "running"
```

MinIO console: http://localhost:9001 (admin / minioadmin)

---

### ✅ TASK 6 — Create a `Makefile`

This gives you shortcuts like `make dev` instead of long commands:

```makefile
.PHONY: dev worker frontend test lint format migrate

# Start backend
dev:
	uv run uvicorn backend.main:app --reload --port 8000

# Start Celery scan worker
worker:
	uv run celery -A workers.celeryconfig worker -Q scan_queue --loglevel=info

# Start frontend
frontend:
	cd frontend && npm run dev

# Run all tests
test:
	uv run pytest tests/ -v

# Lint code
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Apply database migrations
migrate:
	uv run alembic upgrade head

# Start all Docker services
up:
	docker compose up -d

# Stop Docker services
down:
	docker compose down
```

---

### ✅ TASK 7 — Create `backend/main.py`

```python
"""
AI Security Analyst Platform — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Security Analyst Platform",
    description=(
        "AI-powered vulnerability detection, analysis, and remediation "
        "with evidence verification and compliance audit trails."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Root endpoint — basic service identification."""
    return {
        "service": "AI Security Analyst Platform",
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Detailed health check — will report database/redis status in later phases."""
    return {
        "status": "healthy",
        "database": "not yet connected",
        "redis": "not yet connected",
        "llm": "not yet configured",
    }
```

Run it:
```powershell
uv run uvicorn backend.main:app --reload --port 8000
```

Test:
- http://localhost:8000 → JSON response
- http://localhost:8000/docs → Swagger UI with your two endpoints

---

### ✅ TASK 8 — Create Next.js Frontend

Open a **second PowerShell window**:

```powershell
cd "C:\Users\HP\Documents\AI Security Analyst\security-analyst-platform"

npx create-next-app@latest frontend `
  --typescript `
  --tailwind `
  --eslint `
  --app `
  --no-src-dir `
  --import-alias "@/*"

cd frontend
npm run dev
```

Visit http://localhost:3000 — the default Next.js page should load.

---

### ✅ TASK 9 — Install and Test Semgrep + Bandit

```powershell
# uv adds them as project tools
uv add semgrep bandit

# Verify
uv run semgrep --version
uv run bandit --version
```

Create `tests/test_scanners/sample_vulnerable.py`:

```python
"""
INTENTIONALLY VULNERABLE FILE — For scanner testing only.
Do NOT use any of these patterns in real code.
"""
import sqlite3
import hashlib


def get_user(username: str):
    """VULNERABLE: SQL Injection via string formatting."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: user input directly in query string
    query = "SELECT * FROM users WHERE username = '%s'" % username
    cursor.execute(query)
    return cursor.fetchall()


def hash_password(password: str) -> str:
    """VULNERABLE: MD5 is cryptographically broken."""
    return hashlib.md5(password.encode()).hexdigest()


# VULNERABLE: hardcoded secret
ADMIN_SECRET = "super_secret_admin_key_12345"
```

Run Semgrep:
```powershell
uv run semgrep --config p/python tests/test_scanners/sample_vulnerable.py
```

Run Semgrep with SARIF output (save and inspect it):
```powershell
uv run semgrep --config p/python --sarif `
  tests/test_scanners/sample_vulnerable.py `
  > tests/test_scanners/semgrep_output.sarif
```

Open `semgrep_output.sarif` in VS Code. Find:
- `runs[0].tool.driver.name` = `"Semgrep"`
- `runs[0].results[0].ruleId` = rule that fired
- `runs[0].results[0].locations[0].physicalLocation.region.startLine` = line number

Run Bandit:
```powershell
uv run bandit tests/test_scanners/sample_vulnerable.py

# JSON output
uv run bandit -f json tests/test_scanners/sample_vulnerable.py `
  > tests/test_scanners/bandit_output.json
```

Compare the two output files — notice Bandit uses its own format, not SARIF. In Phase 2 we'll write a normalizer.

---

### ✅ TASK 10 — Create Production Documentation Files

Create these files at the project root. Copy the content from the artifacts I created:

| File | Source Artifact |
|------|----------------|
| `README.md` | Write your own based on project overview |
| `ARCHITECTURE.md` | [ARCHITECTURE.md artifact](ARCHITECTURE.md) |
| `CONTRIBUTING.md` | [CONTRIBUTING.md artifact](CONTRIBUTING.md) |
| `SECURITY.md` | [SECURITY.md artifact](SECURITY.md) |
| `DEVELOPMENT.md` | [DEVELOPMENT.md artifact](DEVELOPMENT.md) |
| `CHANGELOG.md` | [CHANGELOG.md artifact](CHANGELOG.md) |
| `CODE_OF_CONDUCT.md` | Use Contributor Covenant v2.1 from https://www.contributor-covenant.org |

---

### ✅ TASK 11 — Create `.gitignore` and `.coderabbit.yaml`

`.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/

# uv — commit pyproject.toml and uv.lock, never .venv
.venv/

# Secrets — NEVER commit
.env

# Node.js
frontend/node_modules/
frontend/.next/

# Editor
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Scanner artifacts (generated)
*.sarif
tests/test_scanners/*.json
tests/test_scanners/*.sarif
```

`.coderabbit.yaml`:
```yaml
language: "en-US"
reviews:
  profile: "chill"
  high_level_summary: true
  review_status: true
  auto_review:
    enabled: true
    base_branches:
      - main
chat:
  auto_reply: true
```

---

### ✅ TASK 12 — Git Setup and First Commit

```powershell
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Stage everything
git add .

# Verify .env is NOT staged
git status
# .env should NOT appear in the list

git commit -m "feat: phase 1 foundation — uv project, FastAPI, Next.js, Docker, scanners, docs"

# Push to GitHub (create repo on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/security-analyst-platform.git
git branch -M main
git push -u origin main
```

---

## 🧪 Testing Phase 1

```powershell
# 1. Backend responds
curl http://localhost:8000/health

# 2. Docker services healthy
docker compose ps

# 3. Semgrep finds vulnerabilities in sample file
uv run semgrep --config p/python tests/test_scanners/sample_vulnerable.py

# 4. Bandit finds vulnerabilities in sample file
uv run bandit tests/test_scanners/sample_vulnerable.py

# 5. uv environment intact
uv run python -c "import fastapi; print('FastAPI OK')"

# 6. Git history
git log --oneline
```

---

## ⚠️ Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running `pip install` instead of `uv add` | Always use `uv add <pkg>` |
| Committing `.env` | Check `git status` before every commit |
| Running `python` instead of `uv run python` | Use `uv run` prefix |
| Forgetting `docker compose up -d` | Check with `docker compose ps` |
| `uvicorn backend.main:app` path wrong | Run from project root |
| Semgrep slow on first run | Downloading rules — wait, it's a one-time thing |

---

## 📚 Learning Checkpoint

Answer these without looking:

1. What does `uv.lock` do and why should it be committed to Git?
2. Why do we use `uv run uvicorn` instead of just `uvicorn`?
3. What is SARIF and why is it better than each scanner having its own format?
4. Why do we run PostgreSQL in Docker instead of installing it directly?
5. What is the difference between Semgrep and Bandit?
6. Why is the free Gemini API good enough for development?

---

## ✅ PHASE 1 CHECKLIST

- [ ] `uv` installed and working (`uv --version`)
- [ ] Python 3.12 managed by uv (`uv python list`)
- [ ] Node.js 20+ confirmed (`node --version`)
- [ ] Docker Desktop running (`docker --version`)
- [ ] Project folder structure created
- [ ] `uv init` run, `pyproject.toml` exists
- [ ] All dependencies added via `uv add`
- [ ] `uv.lock` file generated (auto)
- [ ] `.env.example` created
- [ ] `.env` created with `GOOGLE_API_KEY` filled in
- [ ] `docker-compose.yml` created
- [ ] `docker compose up -d` run successfully
- [ ] PostgreSQL running and healthy
- [ ] Redis running and healthy
- [ ] MinIO running (console at http://localhost:9001)
- [ ] `Makefile` created
- [ ] `backend/main.py` created
- [ ] FastAPI running at http://localhost:8000
- [ ] FastAPI `/docs` page loads
- [ ] Next.js created in `frontend/`
- [ ] Next.js running at http://localhost:3000
- [ ] Semgrep installed (`uv run semgrep --version`)
- [ ] Bandit installed (`uv run bandit --version`)
- [ ] `sample_vulnerable.py` created
- [ ] Semgrep scan run — findings visible
- [ ] Semgrep SARIF output saved and inspected
- [ ] Bandit scan run — findings visible
- [ ] Bandit JSON output saved and compared to SARIF
- [ ] `ARCHITECTURE.md` created at project root
- [ ] `CONTRIBUTING.md` created at project root
- [ ] `SECURITY.md` created at project root
- [ ] `DEVELOPMENT.md` created at project root
- [ ] `CHANGELOG.md` created at project root
- [ ] `CODE_OF_CONDUCT.md` created at project root
- [ ] `README.md` created at project root
- [ ] `.gitignore` created (`.env` listed in it)
- [ ] `.coderabbit.yaml` created
- [ ] Git repo initialized
- [ ] First commit made (`.env` NOT included)
- [ ] Pushed to GitHub

---

**When the checklist is complete, say: "Phase 1 done" 🚀**
