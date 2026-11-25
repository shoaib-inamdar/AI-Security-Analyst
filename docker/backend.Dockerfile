# Production image for the AI Security Analyst backend

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (cache optimization)
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev tools in production)
RUN uv sync --frozen --no-dev

# Copy application source code
COPY backend/ ./backend/
COPY observability/ ./observability/

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start with 4 workers for production throughput
CMD ["uv", "run", "uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]