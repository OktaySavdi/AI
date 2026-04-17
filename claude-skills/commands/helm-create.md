Scaffold a new production-grade Helm chart using the helm-chart-builder skill.

Application: $ARGUMENTS

Generate:
1. Chart.yaml (apiVersion v2, metadata, version 0.1.0)
2. values.yaml with secure defaults:
   - runAsNonRoot, readOnlyRootFilesystem, allowPrivilegeEscalation: false
   - capabilities.drop: [ALL]
   - resource requests + limits
   - liveness + readiness probes
3. values.schema.json (JSON Schema for validation)
4. templates/_helpers.tpl (name, labels, selectorLabels helpers)
5. templates/deployment.yaml (uses helpers, security context from values)
6. templates/service.yaml
7. templates/serviceaccount.yaml (automount: false)
8. templates/hpa.yaml (optional, gated by autoscaling.enabled)
9. templates/NOTES.txt
10. .helmignore

Output each file with its path as a header. No :latest tags.
