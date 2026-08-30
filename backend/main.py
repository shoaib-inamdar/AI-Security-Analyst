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
