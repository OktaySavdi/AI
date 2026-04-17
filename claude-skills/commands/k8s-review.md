Review the following Kubernetes manifest for security, correctness, and production-readiness. Use the kubernetes-expert and infrastructure-security skills.

Check:
1. Security context (runAsNonRoot, allowPrivilegeEscalation, readOnlyRootFilesystem, capabilities)
2. Resource requests/limits on all containers
3. Liveness + readiness probes
4. Image tag (no :latest)
5. Labels (app, app.kubernetes.io/name)
6. HA: replicas ≥ 2, podAntiAffinity or topologySpreadConstraints
7. RBAC: ServiceAccount, automountServiceAccountToken

For each issue: state severity (Critical/High/Medium/Low), explain risk, provide fixed YAML snippet.

Manifest to review:
$ARGUMENTS
