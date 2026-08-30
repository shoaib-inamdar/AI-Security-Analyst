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
