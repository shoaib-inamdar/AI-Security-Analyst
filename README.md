## 📊 Benchmark Results

| Metric | Our Result | Target |
|--------|-----------|--------|
| Detection Recall | **83%** | > 80% ✅ |
| False Positive Rate | **5%** | < 15% ✅ |

*Tested on 7 labeled samples: SQL Injection (×2), Command Injection, Path Traversal, Hardcoded Credentials, Weak Crypto, and a False Positive test.*

## 🚀 Quick Start

1. `uv sync` — install Python dependencies
2. `cp .env.example .env` — configure your API keys
3. `docker compose up -d` — start PostgreSQL, Redis, MinIO, Prometheus, Grafana
4. `uv run uvicorn backend.main:app --reload --port 8000` — start backend
5. `cd frontend && npm run dev` — start frontend

**Dashboards:**
- API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- MinIO: http://localhost:9001