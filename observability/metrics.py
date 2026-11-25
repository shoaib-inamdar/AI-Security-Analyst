"""
Custom Prometheus metrics for the AI Security Analyst Platform.
Exposed at GET /metrics for Prometheus to scrape.
"""

from prometheus_client import Counter, Gauge,Histogram

scans_total=Counter(
    "security_scans_total",
    "Total number of security scans initiated",
    ["status"],
)

scan_duration_seconds=Histogram(
    "security_scan_duration_seconds",
    "Time in seconds for a complete scan to run",
    buckets=[5,10,30,60,120,300,600],
)

active_scans=Gauge(
    "security_active_scans",
    "Number of scans currently in progress",
)

ai_calls_total=Counter(
    "security_ai_calls_total",
    "Total LLM API calls made",
    ["provider","status"],
)

ai_call_duration_seconds=Histogram(
    "security_ai_call_duration_seconds",
    "LLM API call latency in seconds",
    buckets=[0.5,1,2,5,10,30],
)

findings_total=Counter(
    "security_findings_total",
    "Total findings detected across all scans",
    ["severity","scanner"],
)

fix_verification_total=Counter(
    "security_fix_verification_total",
    "Total fix verification run",
    ["result"]
)