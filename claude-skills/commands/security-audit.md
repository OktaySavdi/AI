Using the infrastructure-security skill, perform a security audit of the following infrastructure code.

Identify:
1. Hardcoded secrets or credentials
2. Overly permissive IAM/RBAC roles
3. Missing encryption (at rest, in transit)
4. Network exposure risks
5. Missing audit logging
6. Supply chain risks (unpinned images/modules)
7. OWASP Top 10 relevant issues

Output format:
- CRITICAL findings first
- Each finding: [Severity] Description | File:Line | Remediation

Code to audit:
$ARGUMENTS
