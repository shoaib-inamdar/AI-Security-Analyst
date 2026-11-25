# Benchmark Dataset

This dataset contains labeled vulnerable code samples used to evaluate the
AI Security Analyst Platform's detection accuracy.

## Metrics Definitions

- **Recall (Detection Rate)**: % of real vulnerabilities that were detected
  - Formula: True Positives / (True Positives + False Negatives)
  - Target: > 80%

- **False Positive Rate**: % of safe-code findings that are NOT real vulnerabilities
  - Formula: False Positives / (False Positives + True Negatives)
  - Target: < 15%

## Sample Categories

| Category | Count | CWE |
|----------|-------|-----|
| SQL Injection | 2 | CWE-89 |
| Hardcoded Credentials | 1 | CWE-798 |
| Weak Cryptography | 1 | CWE-327 |
| Path Traversal | 1 | CWE-22 |
| Command Injection | 1 | CWE-78 |
| False Positive Tests | 1 | N/A |

## Adding New Samples

1. Create the vulnerable file in `samples/`
2. Add its label entry to `labels.json`
3. Run `uv run python -m benchmark.runner` to re-run the benchmark
