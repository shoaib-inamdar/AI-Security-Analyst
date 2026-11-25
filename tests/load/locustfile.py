"""
Load test for the AI Security Analyst Platform API.
Simulates concurrent users using the platform.

Run with:
    uv run locust -f tests/load/locustfile.py --host http://localhost:8000

Then open http://localhost:8089 to control the test.
"""

from locust import HttpUser,between, task

class SecurityAnalystUser(HttpUser):
    """Simulates a developer using the platform."""

    wait_time=between(1,3)

    @task(3)
    def check_health(self):
        """Lightest request — health check."""
        self.client.get("/health",name="GET /health")
    
    @task(2)
    def get_root(self):
        """Root endpoint."""
        self.client.get("/",name="GET /")

    @task(1)
    def view_api_docs(self):
        """API documentation page."""
        self.client.get("/docs",name="GET /docs")
    
class SecurityEngineerUser(HttpUser):
    """Simulates a security engineer doning heavier work"""

    wait_time=between(2,5)

    @task(5)
    def check_health(self):
        self.client.get("/health",name="GET /health [engineer]")

    @task(1)
    def check_metrics(self):
        """Check Prometheus metrics endpoint"""
        self.client.get("/metrics",name="GET /metrics")