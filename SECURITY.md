# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ Active development |
| Tagged releases | ✅ Latest minor release |
| Older releases | ❌ No security patches |

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

### Preferred Method

Open a [GitHub Security Advisory](https://github.com/YOUR_USERNAME/security-analyst-platform/security/advisories/new) (private, not visible to the public).

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected component(s)
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

| Step | Target Time |
|------|------------|
| Initial acknowledgement | 48 hours |
| Severity assessment | 5 business days |
| Fix development | Depends on severity (see below) |
| Public disclosure | After fix is released |

### Severity Response Times

| Severity | Response | Fix Target |
|----------|----------|-----------|
| Critical (CVSS 9.0+) | 24 hours | 7 days |
| High (CVSS 7.0–8.9) | 48 hours | 14 days |
| Medium (CVSS 4.0–6.9) | 5 days | 30 days |
| Low (CVSS < 4.0) | 10 days | Next release |

---

## Scope

### In Scope

- Authentication and authorization bypass
- SQL injection or other injection vulnerabilities
- Sandbox escape in the fix verification component
- JWT token forgery or session hijacking
- Webhook signature bypass (GitHub webhook handler)
- Audit log tampering (audit log must be append-only)
- Secrets exposed in logs, error messages, or API responses
- Cross-tenant data access (organization isolation bypass)
- Remote code execution via scanner runner
- Path traversal in repository handling

### Out of Scope

- Vulnerabilities in intentionally vulnerable sample files (`tests/test_scanners/sample_vulnerable.py`)
- Security issues in third-party dependencies (report to the dependency maintainer)
- Social engineering attacks
- Physical attacks
- Denial of service via large repository scans (covered by rate limiting)

---

## Security Design Principles

This platform is a security tool and is held to a higher security standard than typical applications.

1. **No plaintext secrets** — All secrets in environment variables. Never in code, logs, or API responses.
2. **Audit log integrity** — The `audit_events` table is append-only at the database level. No application code can UPDATE or DELETE audit records.
3. **Sandbox isolation** — Fix verification runs in isolated containers/directories. No network access. Temporary files always cleaned up.
4. **Evidence first** — No AI-generated content is displayed to users unless evidence citations are verified against actual source code.
5. **Least privilege** — Database user has only required permissions. Sandbox processes run with minimal OS permissions.

---

## Responsible Disclosure

We follow coordinated disclosure. We ask that you:

1. Give us reasonable time to fix before public disclosure
2. Not exploit the vulnerability beyond what is necessary to demonstrate it
3. Not access, modify, or delete data that is not yours

In return we will:

1. Acknowledge your report promptly
2. Keep you informed of our progress
3. Credit you in the security advisory when the fix is released (unless you prefer anonymity)
