---
name: "helm-chart-builder"
description: >
  Helm chart authoring specialist for Kubernetes applications. Covers chart structure,
  values schema, named templates, hooks, tests, and best practices for templating
  production-grade Helm charts including AKS-specific patterns. Activate for any
  Helm chart creation, modification, or debugging work.
license: MIT
metadata:
  version: 1.0.0
  author: IT Infrastructure
  category: engineering
---

# Helm Chart Builder Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/helm:create` | Scaffold a new Helm chart with production-grade defaults |
| `/helm:review` | Review an existing chart for correctness and security |
| `/helm:values` | Generate a values schema (values.schema.json) for a chart |
| `/helm:debug` | Debug a failing Helm release (template render + diff) |

## When This Skill Activates
Recognize these patterns:
- "Create a Helm chart for..."
- "Debug this Helm release / template error"
- "Add values schema / validation to chart"
- "Helm upgrade fails..."
- "Write a values.yaml for..."
- "Convert this manifest to a Helm chart"
- Any request involving: `helm template`, `helm install`, `Chart.yaml`, `_helpers.tpl`

---

## Chart Directory Structure
```
mychart/
  Chart.yaml           # Chart metadata
  values.yaml          # Default values
  values.schema.json   # JSON Schema for values validation
  templates/
    _helpers.tpl       # Named templates (partials)
    deployment.yaml
    service.yaml
    ingress.yaml
    serviceaccount.yaml
    hpa.yaml
    NOTES.txt          # Post-install notes
  tests/
    test-connection.yaml
  .helmignore
```

## Chart.yaml Template
```yaml
apiVersion: v2
name: myapp
description: A production-grade Helm chart for myapp
type: application
version: 0.1.0        # Chart version (SemVer)
appVersion: "1.0.0"   # App version (quoted string)
keywords:
  - myapp
maintainers:
  - name: IT Infrastructure
    email: platform@example.com
```

## _helpers.tpl Essentials
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## Deployment Template Pattern
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            {{- toYaml .Values.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## Secure Default values.yaml
```yaml
replicaCount: 2

image:
  repository: myregistry.azurecr.io/myapp
  pullPolicy: IfNotPresent
  tag: ""   # Overridden by CI with image digest or version

serviceAccount:
  create: true
  automount: false
  annotations: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: [ALL]

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 15
  periodSeconds: 20

readinessProbe:
  httpGet:
    path: /readyz
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## values.schema.json (partial)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["image", "resources"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    }
  }
}
```

## Helm Hooks
```yaml
# Pre-upgrade DB migration job
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

## Debugging Workflow
```bash
# Render templates locally (no cluster needed)
helm template myapp ./mychart -f values-override.yaml

# Dry-run against cluster (validates server-side)
helm install myapp ./mychart --dry-run --debug

# Diff against running release (requires helm-diff plugin)
helm diff upgrade myapp ./mychart -f values-override.yaml

# Check release history
helm history myapp -n mynamespace

# Rollback
helm rollback myapp 2 -n mynamespace
```

## Proactive Triggers
Flag these without being asked:
- **No `values.schema.json`** → Add JSON Schema to catch misconfigured values early
- **Hardcoded image tag in values.yaml** → Use `default .Chart.AppVersion` pattern
- **`automount: true` on ServiceAccount** → Set to false unless API access needed
- **Missing `NOTES.txt`** → Add post-install instructions for connection info
- **No `podDisruptionBudget`** → Add PDB for workloads with `replicaCount > 1`
- **Resources not in values.yaml** → Hardcoded resources can't be overridden

## Helm Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "mychart.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox:1.36
      command: ['wget']
      args: ['{{ include "mychart.fullname" . }}:{{ .Values.service.port }}']
      resources:
        limits: {cpu: 100m, memory: 64Mi}
        requests: {cpu: 50m, memory: 32Mi}
```

Run tests:

```bash
helm test myapp -n mynamespace --logs
```

## OCI Registry (ACR)

```bash
# Push chart to Azure Container Registry
helm package mychart/
helm push mychart-1.0.0.tgz oci://myregistry.azurecr.io/helm

# Pull and install from OCI
helm install myapp oci://myregistry.azurecr.io/helm/mychart --version 1.0.0

# Login to ACR for Helm
az acr login --name myregistry
```

## Library Charts (Shared Templates)

```yaml
# Chart.yaml — library chart
apiVersion: v2
name: mylib
type: library
version: 0.1.0
```

```yaml
# templates/_deployment.tpl in library chart
{{- define "mylib.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mylib.fullname" . }}
  labels: {{- include "mylib.labels" . | nindent 4 }}
spec:
  {{- toYaml .Values.deployment | nindent 2 }}
{{- end }}
```

```yaml
# Consumer chart Chart.yaml
dependencies:
  - name: mylib
    version: "0.1.0"
    repository: "oci://myregistry.azurecr.io/helm"
```

## CI Pipeline: Lint + Test + Push

```yaml
# Azure DevOps
- script: |
    helm lint mychart/
    helm template mychart/ --debug > /dev/null
    helm package mychart/
    helm push mychart-*.tgz oci://$(ACR_NAME).azurecr.io/helm
  displayName: Helm Lint, Package, Push
  env:
    HELM_EXPERIMENTAL_OCI: "1"
```

## Related Skills
- `kubernetes-expert` — underlying Kubernetes concepts and security context
- `infrastructure-security` — security hardening of chart defaults
- `devops-cicd` — Helm chart CI/CD (lint, test, package, push to ACR)
