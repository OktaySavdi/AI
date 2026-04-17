---
name: "observability-designer"
description: >
  Observability specialist for Kubernetes and Azure environments. Covers Prometheus
  metrics (ServiceMonitor, PrometheusRule), Grafana dashboards, Loki log aggregation,
  Elastic Agent, alerting design (SLO/SLA), distributed tracing (OpenTelemetry),
  and Azure Monitor integration. Activate for any monitoring, alerting, or
  observability work.
license: MIT
metadata:
  version: 1.0.0
  author: IT Infrastructure
  category: engineering
---

# Observability Designer Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/obs:slo` | Design SLOs and error budget alerts for a service |
| `/obs:dashboard` | Generate a Grafana dashboard JSON for a workload |
| `/obs:alerts` | Create PrometheusRule alerts for a component |
| `/obs:servicemonitor` | Generate a ServiceMonitor for a Kubernetes service |
| `/obs:runbook` | Write an alert runbook (what to do when alert fires) |

## When This Skill Activates
Recognize these patterns:
- "Add monitoring / metrics to..."
- "Create alerts for..."
- "Dashboard for this service"
- "SLO / SLA for this endpoint"
- "Why is this alert firing?"
- "Loki / Elastic / Prometheus setup"
- "Instrument this app with OpenTelemetry"
- "Azure Monitor integration"
- Any request involving: Grafana, Prometheus, ServiceMonitor, PrometheusRule, Loki, Jaeger

---

## Observability Stack (This Environment)

| Layer | Tool | Purpose |
|-------|------|---------|
| Metrics | Prometheus + kube-state-metrics | Cluster + app metrics |
| Dashboards | Grafana | Visualisation |
| Logs (K8s) | Loki + Promtail / Elastic Agent | Log aggregation |
| Logs (Azure) | Azure Monitor + Log Analytics | Platform logs |
| Tracing | OpenTelemetry Collector | Distributed traces |
| Alerting | Prometheus Alertmanager | Rule-based alerts |

## SLO Design Framework

### SLO Template
```
Service: <name>
SLI: <what we measure — e.g. request success rate>
SLO: <target — e.g. 99.5% over 30 days>
Error Budget: <1 - SLO = 0.5% = ~3.6h/month>
Alert: burn rate > 2× → page; burn rate > 1× → ticket
```

### Example SLO — API Availability
```yaml
# PrometheusRule for SLO burn rate
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: api-availability-slo
  namespace: monitoring
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
    - name: slo.api-availability
      interval: 30s
      rules:
        # SLI: success rate
        - record: job:http_requests:success_rate5m
          expr: |
            sum(rate(http_requests_total{job="myapp",code!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{job="myapp"}[5m]))

        # Fast burn (2% budget in 1h = 14.4× burn rate)
        - alert: AvailabilitySLOFastBurn
          expr: job:http_requests:success_rate5m < 0.986
          for: 2m
          labels:
            severity: critical
            slo: availability
          annotations:
            summary: "Fast SLO burn: API availability"
            description: "Error rate {{ $value | humanizePercentage }} over 5m. Page on-call."
            runbook_url: "https://wiki.internal/runbooks/api-availability"

        # Slow burn (5% budget in 6h = 5× burn rate)
        - alert: AvailabilitySLOSlowBurn
          expr: job:http_requests:success_rate5m < 0.995
          for: 15m
          labels:
            severity: warning
            slo: availability
          annotations:
            summary: "Slow SLO burn: API availability"
            description: "Sustained degradation. Create ticket."
```

## ServiceMonitor Template
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: monitoring
  labels:
    release: kube-prometheus-stack   # Must match Prometheus selector
spec:
  namespaceSelector:
    matchNames:
      - myapp-namespace
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
```

## Common PrometheusRule Alerts

### Pod health
```yaml
- alert: PodCrashLooping
  expr: rate(kube_pod_container_status_restarts_total[15m]) * 60 * 5 > 5
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash-looping"
    runbook_url: "https://wiki.internal/runbooks/pod-crashloop"

- alert: PodNotReady
  expr: kube_pod_status_ready{condition="false"} == 1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} not ready for 10m"
```

### Node health
```yaml
- alert: NodeMemoryPressure
  expr: kube_node_status_condition{condition="MemoryPressure",status="true"} == 1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Node {{ $labels.node }} under memory pressure"

- alert: NodeDiskPressure
  expr: kube_node_status_condition{condition="DiskPressure",status="true"} == 1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Node {{ $labels.node }} under disk pressure"
```

### Kyverno policy violations
```yaml
- alert: KyvernoPolicyViolations
  expr: |
    sum by (policy, namespace) (
      kyverno_policy_results_total{rule_result="fail"}
    ) > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Kyverno policy {{ $labels.policy }} has violations in {{ $labels.namespace }}"
```

## Loki Log Query Patterns
```logql
# All error logs in a namespace
{namespace="myapp"} |= "ERROR" | json | line_format "{{.level}} {{.msg}}"

# Slow HTTP requests (>1s) from access log
{app="nginx"} | logfmt | duration > 1s

# Kyverno admission denials
{app="kyverno"} |= "admission webhook" |= "denied"

# OOMKilled events
{job="kube-events"} |= "OOMKilled"
```

## OpenTelemetry Collector Config (sidecar)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
    processors:
      batch:
        timeout: 1s
      memory_limiter:
        limit_mib: 128
    exporters:
      prometheus:
        endpoint: 0.0.0.0:8889
      jaeger:
        endpoint: jaeger-collector:14250
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [jaeger]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
```

## Alert Runbook Template (/obs:runbook)
```markdown
## Alert: <AlertName>
**Severity**: Critical / Warning
**Team**: Platform / App

### What is firing?
[Plain-English description of the condition]

### Immediate Actions (< 5 min)
1. `kubectl get pods -n <ns>` — check pod state
2. `kubectl logs <pod> --previous` — check recent logs
3. `kubectl describe pod <pod>` — check events

### Escalation
- If unresolved after 15 min → page [team]
- If data loss risk → invoke incident commander

### Root Cause Queries
```promql
# [Paste relevant PromQL]
```

### Resolution
[Steps to fix, including rollback instructions]
```

## Proactive Triggers
Flag these without being asked:
- **No ServiceMonitor for a Deployment** → App metrics not scraped → add `/metrics` endpoint + ServiceMonitor
- **No PrometheusRule for a critical service** → Blind to failures → add availability + latency alerts
- **Alert without `runbook_url`** → On-call has no guidance → add runbook link
- **Loki not scraping namespace** → Logs invisible → add `logging: "true"` label + Promtail config
- **No SLO defined for user-facing service** → No error budget → design SLO first
- **Retention < 30 days on Prometheus** → Compliance risk → increase or federate to Thanos/Grafana Cloud

## Grafana Dashboard JSON Skeleton

```json
{
  "title": "Service Overview",
  "uid": "service-overview",
  "tags": ["kubernetes", "service"],
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{namespace=\"$namespace\",service=\"$service\"}[5m])) by (status_code)",
          "legendFormat": "{{status_code}}"
        }
      ]
    },
    {
      "title": "P99 Latency",
      "type": "timeseries",
      "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
      "targets": [
        {
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace=\"$namespace\"}[5m])) by (le))",
          "legendFormat": "p99"
        }
      ]
    }
  ],
  "templating": {
    "list": [
      {"name": "namespace", "type": "query", "query": "label_values(kube_pod_info, namespace)"},
      {"name": "service", "type": "query", "query": "label_values(kube_service_info{namespace=\"$namespace\"}, service)"}
    ]
  }
}
```

## Azure Monitor Diagnostic Settings (Terraform)

```hcl
resource "azurerm_monitor_diagnostic_setting" "aks" {
  name               = "aks-diagnostics"
  target_resource_id = module.aks.cluster_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log { category = "kube-apiserver" }
  enabled_log { category = "kube-controller-manager" }
  enabled_log { category = "kube-scheduler" }
  enabled_log { category = "kube-audit" }
  enabled_log { category = "guard" }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
```

## Elastic Agent Fleet (Kubernetes)

```yaml
# DaemonSet for Elastic Agent on AKS
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: elastic-agent
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: elastic-agent
  template:
    spec:
      serviceAccountName: elastic-agent
      containers:
        - name: elastic-agent
          image: docker.elastic.co/beats/elastic-agent:8.13.0
          env:
            - name: FLEET_URL
              valueFrom:
                secretKeyRef:
                  name: elastic-fleet-credentials
                  key: fleet_url
            - name: FLEET_ENROLLMENT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: elastic-fleet-credentials
                  key: enrollment_token
          resources:
            requests: {cpu: 100m, memory: 200Mi}
            limits: {cpu: 500m, memory: 500Mi}
          securityContext:
            runAsUser: 0  # required for host log access via DaemonSet
```

## Kyverno Policy Violation Alert

```yaml
# PrometheusRule for Kyverno audit violations
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: kyverno-policy-alerts
  namespace: kyverno
spec:
  groups:
    - name: kyverno.rules
      rules:
        - alert: KyvernoPolicyViolationHigh
          expr: |
            sum by (policy, namespace) (
              kyverno_policy_results_total{rule_type="validate", status="fail"}
            ) > 0
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Kyverno policy violation: {{ $labels.policy }} in {{ $labels.namespace }}"
            runbook_url: "https://wiki.example.com/runbooks/kyverno-violations"
```

## Related Skills
- `kubernetes-expert` — Kubernetes resource context for alerts
- `infrastructure-security` — security alerts (Kyverno violations, RBAC changes)
- `devops-cicd` — pipeline metrics and deployment frequency tracking
- `azure-cloud-architect` — Azure Monitor / Log Analytics integration patterns
