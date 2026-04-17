---
name: "security-review"
description: >
  Security review checklist for code, infrastructure, and pipelines. Covers OWASP Top 10,
  container security, secrets management, and dependency scanning. Activate for any security
  audit or review.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: security
---

# Security Review Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/security-audit` | Full security audit |

## OWASP Top 10 Checks

### A01: Broken Access Control
- [ ] All endpoints require authentication unless explicitly public
- [ ] Authorization checked on every request (not just at login)
- [ ] IDOR prevented — verify user owns the resource before returning
- [ ] RBAC applied with least privilege

### A02: Cryptographic Failures
- [ ] Sensitive data encrypted at rest and in transit
- [ ] No MD5/SHA1 for passwords — use bcrypt/argon2
- [ ] TLS 1.2+ enforced, TLS 1.0/1.1 disabled
- [ ] Secrets in Key Vault, not code or config files

### A03: Injection
- [ ] Parameterised queries for all SQL
- [ ] No `shell=True` with user input
- [ ] No `eval()` with untrusted input
- [ ] Input validated at system boundaries

### A05: Security Misconfiguration
- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Verbose error messages suppressed in production
- [ ] Security headers set (CSP, HSTS, X-Frame-Options)

### A06: Vulnerable Components
- [ ] Dependencies scanned for CVEs (`pip-audit`, `npm audit`, `trivy`)
- [ ] No components with known critical CVEs
- [ ] Pinned versions in lockfiles

### A07: Auth Failures
- [ ] Session tokens expire
- [ ] Password reset tokens are single-use and expire
- [ ] Rate limiting on auth endpoints
- [ ] MFA available for privileged accounts

## Container/K8s Security

See `infrastructure-security` skill for full K8s checklist.

Quick checks:
- `runAsNonRoot: true`
- `readOnlyRootFilesystem: true`
- No `:latest` tags
- `capabilities: drop: [ALL]`

## Pipeline Security

- [ ] Secrets in vault/variable groups, not in YAML
- [ ] `failOnStandardError: true` on all steps
- [ ] Image scanning in CI before deployment
- [ ] Approval gate required for production

## Report Format

```
## Security Review

### CRITICAL (fix before any deployment)
### HIGH (fix this sprint)
### MEDIUM (fix next sprint)
### LOW (track in backlog)
### INFO (no action required)
```
