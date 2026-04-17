# ops — Operations / Incident Mode

Activate OPERATIONS mode for live-system debugging and incident response.

---

## Mode: OPERATIONS

You are in **live-system debugging mode**. All actions must prioritise:
1. **Safety** — do not make changes that worsen the incident
2. **Speed** — reduce MTTR
3. **Evidence** — collect before acting, document everything

---

## Incident Classification

| Severity | Criteria | SLA |
|---|---|---|
| P1 | Production down, data loss risk | 15 min response |
| P2 | Degraded production, workaround available | 1 hour |
| P3 | Non-production affected | 4 hours |
| P4 | Informational / monitoring alert | Next business day |

---

## Triage Runbook

### Step 1: Classify
- What is the observed symptom?
- Which cluster / namespace / workload?
- When did it start? Any recent deployments?

### Step 2: Collect
```bash
# Pod status
kubectl get pods -n <namespace> -o wide

# Events (last 1 hour)
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -30

# Logs
kubectl logs <pod> -n <namespace> --previous --tail=100

# Describe
kubectl describe pod <pod> -n <namespace>

# Node pressure
kubectl top nodes
kubectl describe node <node>
```

### Step 3: Diagnose
Common patterns:
- **CrashLoopBackOff** → OOM, bad config, failed liveness probe
- **Pending** → resource exhaustion, PVC not bound, affinity mismatch
- **ImagePullBackOff** → ACR auth, wrong tag, network policy
- **Terminating stuck** → finalizer loop, node NotReady
- **Service unreachable** → selector mismatch, NetworkPolicy block, endpoint missing

### Step 4: Mitigate
- Scale deployment: `kubectl scale deploy <name> -n <ns> --replicas=N`
- Rollback: `kubectl rollout undo deploy/<name> -n <ns>`
- Cordon/drain node: `kubectl cordon <node> && kubectl drain <node> --ignore-daemonsets`
- Force delete stuck pod: `kubectl delete pod <name> -n <ns> --grace-period=0 --force`

### Step 5: Restore
- Confirm pods Running and Ready
- Verify service endpoints: `kubectl get endpoints -n <namespace>`
- Check ingress: `kubectl describe ingress -n <namespace>`
- Run smoke test

### Step 6: Post-Mortem
- Timeline of events
- Root cause
- Fix applied
- Prevention action items
- Jira ticket: PROJECT_ID 10008

---

## TKG Cluster Access

```bash
# Staging (direct)
ssh root@<TKG_STAGING_IP>

# Production (jump host)
ssh <JUMP_USER>@<JUMP_HOST_IP>
# then
ssh root@<TKG_PROD_IP>
```

---

## AKS Quick Checks

```bash
# Get AKS credentials
az aks get-credentials --resource-group <rg> --name <cluster>

# Node pool status
az aks nodepool list --resource-group <rg> --cluster-name <cluster>

# Activity log (last hour)
az monitor activity-log list --resource-group <rg> --offset 1h
```

---

## Completion Checklist

- [ ] Incident documented in Jira
- [ ] Timeline written
- [ ] Root cause identified
- [ ] Fix validated in production
- [ ] Monitoring/alerting gap addressed
- [ ] Post-mortem scheduled if P1/P2
