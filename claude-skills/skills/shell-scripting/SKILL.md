---
name: "shell-scripting"
description: >
  Shell scripting specialist for Bash automation in IT infrastructure contexts.
  Grounded in real scripts from the Shell/ folder: TKG Supervisor cert monitoring,
  Commvault backup integration, Elastic Agent Fleet management, AKS/TKG SSH access,
  and Wiz Helm integration updaters. Covers script structure, error handling,
  Jira/Teams alerting, SSH connectivity patterns (direct + jump host), and Azure CLI.
  Activate for any Bash script creation, review, or debugging work.
license: MIT
metadata:
  version: 1.0.0
  author: IT Infrastructure
  category: engineering
---

# Shell Scripting Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/shell:new` | Scaffold a new script following team standards |
| `/shell:review` | Full review: safety, secrets, error handling, style |
| `/shell:jira` | Add Jira ticket creation on failure to a script |
| `/shell:notify` | Add Teams webhook notification to a script |
| `/shell:ssh` | Add correct SSH connectivity (direct or jump host) |

## When This Skill Activates

- "Write a bash script for..."
- "Review / fix this shell script"
- "Add Jira / Teams notification to..."
- "Script to SSH into TKG / AKS nodes"
- "Automate Wiz / Elastic / Commvault integration"
- Any `.sh` file in the workspace

---

## Script Canonical Structure

Every production script in the team follows this structure:

```bash
#!/usr/bin/env bash
# ==============================================================================
# <Title>
# Author: Oktay Savdi
# Description: <What it does>
#
# Usage:
#   Method 1 (CLI args):   ./script.sh <ACTION> <ARG1> <ARG2>
#   Method 2 (env vars):   export ACTION="create"; ./script.sh
#
# Examples:
#   ./script.sh create my-cluster https://10.0.0.1:443 eyJhbGc...
#   ./script.sh delete my-cluster
# ==============================================================================

set -euo pipefail   # Exit on error, undefined vars, pipe failures

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── COLOUR CODES ───────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'   # No Color

# ── LOGGING ────────────────────────────────────────────────────────────────────
LOG_DIR="/opt/<ORG>/<script-name>"
LOG_FILE="${LOG_DIR}/<script-name>.log"

log_info()    { echo -e "${BLUE}[INFO]${NC} $*";                 echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*" >> "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*";             echo "[$(date '+%Y-%m-%d %H:%M:%S')] OK    $*" >> "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*";            echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*" >> "$LOG_FILE"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2;             echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >> "$LOG_FILE"; }
die()         { log_error "$*"; exit 1; }

# ── CONFIGURATION (from env vars — never hardcode secrets) ────────────────────
: "${REQUIRED_SECRET:?Must set REQUIRED_SECRET}"          # fail fast if missing
OPTIONAL_PARAM="${OPTIONAL_PARAM:-default_value}"

# ── JIRA CONFIGURATION ─────────────────────────────────────────────────────────
# (copy the jira_create_ticket function below when failure alerting is needed)
JIRA_URL="https://<YOUR_ORG>.atlassian.net"
JIRA_AUTH="<JIRA_SERVICE_ACCOUNT>@<YOUR_ORG>.com:${JIRA_API_TOKEN:-}"
PROJECT_ID="10008"
ISSUETYPE_ID="10002"   # Bug / Task
PRIORITY_ID="3"        # Medium
ASSIGNEE="<JIRA_ASSIGNEE_EMAIL>"
AREA_ID="17610"        # IT
COMPONENTS=("Cloud and Systems Engineering")
LABELS=("TKG" "<TEAM>_Operations" "<TEAM>_Automation")
TICKET_STATE_FILE="/opt/<ORG>/<script-name>/tickets.json"

# ── TEAMS WEBHOOK ──────────────────────────────────────────────────────────────
TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL:-}"

# ── PARAMETER HANDLING ─────────────────────────────────────────────────────────
ACTION="${1:-${ACTION:-}}"
ARG1="${2:-${ARG1:-}}"

[[ -z "$ACTION" ]] && die "ACTION is required (create|delete)"

# ── MAIN ───────────────────────────────────────────────────────────────────────
main() {
    mkdir -p "$LOG_DIR"
    log_info "Starting — ACTION=$ACTION"

    case "$ACTION" in
        create) do_create ;;
        delete) do_delete ;;
        *)      die "Unknown ACTION: $ACTION. Use: create | delete" ;;
    esac
}

main "$@"
```

---

## Security Rules (non-negotiable)

1. **Never hardcode secrets** — use environment variables (`${VAR:-}` pattern)
2. **`set -euo pipefail`** on every script — no exceptions
3. **Validate env vars** with `: "${VAR:?message}"` at the top
4. **`curl -k`** only for internal TLS (VPN-protected endpoints); never against public APIs
5. **Temp files**: always use `mktemp` + `trap cleanup EXIT` for cleanup
6. **Base64-encode passwords** with special characters (as in cert monitor): `echo -n 'pass' | base64`
7. **SSH**: always clean known_hosts before connecting → `ssh-keygen -R "$IP" 2>/dev/null || true`

```bash
# Temp file pattern
VALUES_FILE=$(mktemp /tmp/script-XXXXXX.tmp)
cleanup() { rm -f "$VALUES_FILE"; }
trap cleanup EXIT
```

---

## Jira Ticket Creation on Failure

Pattern used in `check_supervisor_cert.sh`, `Commvault_Backup_Enhanced.sh`, `Elastic_Agent_Enhanced.sh`:

```bash
# ── JIRA ───────────────────────────────────────────────────────────────────────
# State file prevents duplicate tickets for the same issue
TICKET_STATE_FILE="/opt/<ORG>/script-name/tickets.json"
[ -f "$TICKET_STATE_FILE" ] || { mkdir -p "$(dirname "$TICKET_STATE_FILE")"; echo '{}' > "$TICKET_STATE_FILE"; }

jira_create_ticket() {
    local summary="$1"
    local description="$2"
    local state_key="$3"   # unique key to prevent duplicates (e.g. host+cert name)

    [[ -z "${JIRA_API_TOKEN:-}" ]] && { log_warning "JIRA_API_TOKEN not set — skipping ticket"; return 0; }

    # Check if ticket already exists for this key
    existing_ticket=$(jq -r --arg k "$state_key" '.[$k] // empty' "$TICKET_STATE_FILE")
    if [[ -n "$existing_ticket" ]]; then
        log_info "Jira ticket already exists for '$state_key': $existing_ticket"
        return 0
    fi

    # Build components JSON
    components_json=$(printf '%s\n' "${COMPONENTS[@]}" | jq -Rn '[inputs | {"name": .}]')
    labels_json=$(printf '%s\n' "${LABELS[@]}" | jq -Rn '[inputs]')

    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "X-ExperimentalApi: true" \
        -u "$JIRA_AUTH" \
        "$JIRA_URL/rest/api/3/issue" \
        --data "{
            \"fields\": {
                \"project\": { \"id\": \"$PROJECT_ID\" },
                \"summary\": \"$summary\",
                \"issuetype\": { \"id\": \"$ISSUETYPE_ID\" },
                \"priority\": { \"id\": \"$PRIORITY_ID\" },
                \"assignee\": { \"emailAddress\": \"$ASSIGNEE\" },
                \"customfield_10014\": { \"id\": \"$AREA_ID\" },
                \"components\": $components_json,
                \"labels\": $labels_json,
                \"description\": {
                    \"type\": \"doc\", \"version\": 1,
                    \"content\": [{ \"type\": \"paragraph\",
                        \"content\": [{ \"type\": \"text\", \"text\": \"$description\" }]
                    }]
                }
            }
        }")

    ticket_key=$(echo "$response" | jq -r '.key // empty')
    if [[ -n "$ticket_key" ]]; then
        log_success "Jira ticket created: $ticket_key — $JIRA_URL/browse/$ticket_key"
        # Save to state file
        tmp=$(mktemp)
        jq --arg k "$state_key" --arg v "$ticket_key" '.[$k] = $v' "$TICKET_STATE_FILE" > "$tmp" && mv "$tmp" "$TICKET_STATE_FILE"
    else
        log_error "Failed to create Jira ticket. Response: $response"
    fi
}
```

**Jira field reference**:
| Field | Value |
|-------|-------|
| `PROJECT_ID` | `10008` |
| `ISSUETYPE_ID` | `10002` (Bug) |
| `PRIORITY_ID` | `3` (Medium) |
| `AREA_ID` | `17610` (IT), `17617` (GAMES), `17611` (Mynt), `17616` (RMG) |
| `ASSIGNEE` (Ops) | `<JIRA_OPS_EMAIL>` |
| `ASSIGNEE` (Infra) | `<JIRA_INFRA_EMAIL>` |

---

## Teams Webhook Notification

Pattern used in `check_supervisor_cert.sh` and `check_supervisor_web_cert.sh`:

```bash
send_teams_notification() {
    local title="$1"
    local message="$2"
    local color="${3:-FF0000}"    # Red by default (alerts); use 00FF00 for success

    [[ -z "${TEAMS_WEBHOOK_URL:-}" ]] && return 0

    curl -s -X POST "$TEAMS_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        --data "{
            \"@type\": \"MessageCard\",
            \"@context\": \"http://schema.org/extensions\",
            \"themeColor\": \"$color\",
            \"summary\": \"$title\",
            \"sections\": [{
                \"activityTitle\": \"$title\",
                \"activityText\": \"$message\"
            }]
        }" || log_warning "Failed to send Teams notification"
}

# Usage:
# send_teams_notification "⚠️ Certificate Expiry Warning" \
#     "Supervisor <CLUSTER> certificate expires in 15 days ($(date))" "FF6600"
```

---

## SSH Connectivity Patterns

### Direct Connection (Staging)
Used by `check_supervisor_cert.sh` and TKG pipelines for staging:

```bash
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10"

ssh_direct() {
    local ip="$1"
    local user="$2"
    local password_b64="$3"   # base64-encoded — handles special chars
    local remote_cmd="$4"

    local password
    password=$(echo "$password_b64" | base64 -d)
    ssh-keygen -R "$ip" 2>/dev/null || true
    sshpass -p "$password" ssh $SSH_OPTS "${user}@${ip}" "$remote_cmd"
}

# Example: staging Supervisor
ssh_direct "<TKG_STAGING_IP>" "root" "$STG_SA_B64" "kubectl get nodes"
```

### Jump Host Connection (Production)
Used for production TKG Supervisor (unreachable directly):

```bash
ssh_via_jump() {
    local target_ip="$1"
    local target_user="$2"
    local target_pass_b64="$3"
    local remote_cmd="$4"
    local jump_ip="${5:-<JUMP_HOST_IP>}"
    local jump_user="${6:-jbx}"
    local jump_key="${7:-/opt/<ORG>/ssh-key_jump.key}"

    local password
    password=$(echo "$target_pass_b64" | base64 -d)
    ssh-keygen -R "$jump_ip" 2>/dev/null || true
    ssh-keygen -R "$target_ip" 2>/dev/null || true
    PROXY_CMD="ssh -i ${jump_key} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p ${jump_user}@${jump_ip}"
    sshpass -p "$password" ssh $SSH_OPTS \
        -o "ProxyCommand=${PROXY_CMD}" \
        "${target_user}@${target_ip}" "$remote_cmd"
}

# Example: production Supervisor
ssh_via_jump "<TKG_PROD_IP>" "root" "$PROD_SA_B64" "kubectl get nodes"
```

### Environment Router
```bash
run_on_supervisor() {
    local environment="$1"   # stg | prod
    local remote_cmd="$2"

    if [[ "$environment" == "stg" ]]; then
        ssh_direct "<TKG_STAGING_IP>" "root" "$STG_SA" "$remote_cmd"
    else
        ssh_via_jump "<TKG_PROD_IP>" "root" "$PROD_SA" "$remote_cmd"
    fi
}
```

### AKS Node SSH (`SSH_AKS.sh` pattern)
Try multiple usernames until one works:

```bash
SSH_USERS=("<admin-user-1>" "<admin-user-2>" "azureuser" "<admin-user-3>")
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"

try_ssh_to_node() {
    local node_ip="$1"
    local node_name="$2"

    [ -f "$SSH_KEY" ] || die "SSH key not found: $SSH_KEY"

    for ssh_user in "${SSH_USERS[@]}"; do
        if ssh -n -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
            "${ssh_user}@${node_ip}" "exit 0" 2>/dev/null; then
            log_success "Connected as ${ssh_user}@${node_ip}"
            # Execute actual command:
            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
                "${ssh_user}@${node_ip}" "YOUR_COMMAND_HERE"
            return 0
        fi
    done
    log_error "Could not SSH to node $node_name ($node_ip) with any user"
    return 1
}
```

---

## Certificate Expiry Checking

Pattern from `check_supervisor_web_cert.sh`:

```bash
NOTIFICATION_DAYS=(60 30 15 5)   # Alert at these thresholds

check_tls_cert_expiry() {
    local host="$1"
    local port="${2:-443}"

    # Reachability check first
    if ! timeout 5 bash -c "echo > /dev/tcp/${host}/${port}" 2>/dev/null; then
        log_error "Cannot reach ${host}:${port}"
        return 1
    fi

    local expiry_str
    expiry_str=$(timeout 10 openssl s_client -connect "${host}:${port}" \
        -servername "${host}" < /dev/null 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null \
        | cut -d= -f2)

    [[ -z "$expiry_str" ]] && { log_error "Could not retrieve cert from ${host}:${port}"; return 1; }

    local expiry_epoch now_epoch days_remaining
    expiry_epoch=$(date -d "$expiry_str" +%s 2>/dev/null || \
                   date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_str" +%s)  # macOS fallback
    now_epoch=$(date +%s)
    days_remaining=$(( (expiry_epoch - now_epoch) / 86400 ))

    log_info "${host}: certificate expires in ${days_remaining} days (${expiry_str})"

    for threshold in "${NOTIFICATION_DAYS[@]}"; do
        if [[ $days_remaining -le $threshold ]]; then
            log_warning "ALERT: ${host} cert expires in ${days_remaining} days (≤${threshold} day threshold)"
            send_teams_notification "⚠️ Certificate Expiry" \
                "${host}:${port} expires in ${days_remaining} days" "FF6600"
            jira_create_ticket \
                "Certificate expiring: ${host}" \
                "Certificate on ${host}:${port} expires in ${days_remaining} days on ${expiry_str}" \
                "${host}_cert_expiry"
            break
        fi
    done
}
```

---

## Wiz Helm Integration Pattern

From `wiz_integration_update.sh` and `wiz_integration_update_aks.sh`:

```bash
VALUES_FILE=$(mktemp /tmp/wiz-values-XXXXXX.yaml)
cleanup() { rm -f "$VALUES_FILE"; }
trap cleanup EXIT

generate_wiz_values() {
    local cluster_name="$1"
    cat > "$VALUES_FILE" << EOF
global:
  wizApiToken:
    secret:
      create: false
      name: wiz-api-token

wiz-sensor:
  enabled: true
  imagePullSecret:
    create: false
    name: sensor-image-pull
  sensorClusterName: ${cluster_name}

wiz-admission-controller:
  enabled: true
  opaWebhook:
    namespaceSelector:
      matchExpressions:
      - key: kubernetes.io/metadata.name
        operator: NotIn
        values: [kube-system, kube-public, default, kube-node-lease,
                 tanzu-package-repo-global, tanzu-system, argocd,
                 monitoring, cert-manager, ingress-nginx]
EOF
}

install_wiz() {
    local cluster="$1"
    generate_wiz_values "$cluster"
    helm repo add wiz-sec https://charts.wiz.io 2>/dev/null || true
    helm repo update
    helm upgrade --install wiz-integration wiz-sec/wiz-kubernetes-integration \
        -n wiz-integration --create-namespace \
        -f "$VALUES_FILE" \
        --wait --timeout 5m
    log_success "Wiz installed on $cluster"
}

# For TKG clusters (kubectx):
for CLUSTER in "${CLUSTERS[@]}"; do
    kubectx "$CLUSTER" 2>/dev/null || { log_error "Context not found: $CLUSTER"; continue; }
    install_wiz "$CLUSTER"
done

# For AKS clusters (az aks get-credentials):
install_wiz_aks() {
    local cluster="$1"
    local rg="$2"
    local sub="$3"
    az aks get-credentials --resource-group "$rg" --name "$cluster" \
        --subscription "$sub" --overwrite-existing
    install_wiz "$cluster"
}
```

---

## Commvault Integration Pattern

From `Commvault_Backup_Enhanced.sh` — REST API integration with auth token:

```bash
# Auth: returns token stored in AUTH_TOKEN global
commvault_auth() {
    local response
    response=$(curl -s $CURL_SSL_FLAG -X POST \
        "https://${WEB_URL}/commandcenter/api/Login" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        --data "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\", \"domain\": \"\"}")
    AUTH_TOKEN=$(echo "$response" | jq -r '.token // empty')
    [[ -z "$AUTH_TOKEN" ]] && die "Commvault auth failed: $response"
}

# Auto-detect environment from cluster name
detect_env() {
    local cluster="$1"
    if [[ "$cluster" =~ aks ]]; then
        PLAN="SP_AKS"
        SERVER_NAME="azure-aks-endpoint"
    else
        PLAN="SP_TKG"
        SERVER_NAME="tkg-endpoint"
    fi
}
```

---

## Elastic Agent Fleet Pattern

From `Elastic_Agent_Enhanced.sh` — Kibana Fleet API:

```bash
create_fleet_policy() {
    local cluster="$1"
    local api_key="$2"
    local kibana_url="$3"

    # Create agent policy
    response=$(curl -s -k -X POST "${kibana_url}/api/fleet/agent_policies" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -H "Authorization: ApiKey $api_key" \
        --data "{\"name\": \"${cluster}\", \"namespace\": \"${cluster}\", \"monitoring_enabled\": [\"logs\", \"metrics\"]}")

    policy_id=$(echo "$response" | jq -r '.item.id // empty')
    [[ -z "$policy_id" ]] && { log_error "Failed to create agent policy: $response"; return 1; }
    log_success "Fleet policy created: $policy_id"

    # Add Kubernetes integration
    curl -s -k -X POST "${kibana_url}/api/fleet/package_policies" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -H "Authorization: ApiKey $api_key" \
        --data "{
            \"name\": \"kubernetes-${cluster}\",
            \"namespace\": \"${cluster}\",
            \"policy_id\": \"${policy_id}\",
            \"package\": { \"name\": \"kubernetes\", \"version\": \"latest\" }
        }"
}
```

---

## Input Validation Patterns

```bash
# Required argument
validate_required() {
    local name="$1" value="$2"
    [[ -z "$value" ]] && die "$name is required"
}

# Action enum
validate_action() {
    local action="$1"
    case "$action" in
        create|delete|update) ;;
        *) die "Invalid ACTION: $action. Allowed: create | delete | update" ;;
    esac
}

# URL format
validate_url() {
    local url="$1"
    [[ "$url" =~ ^https?:// ]] || die "Invalid URL: $url (must start with https://)"
}

# Supervisor environment
validate_environment() {
    local env="$1"
    [[ "$env" == "stg" || "$env" == "prod" ]] || die "Invalid environment: $env. Use: stg | prod"
}
```

---

## Existing Scripts Reference (`Shell/`)

| Script | Purpose | Key Pattern |
|--------|---------|-------------|
| `check_supervisor_cert.sh` | Monitor TKG internal certs (etcd, apiserver, kubelet, vip) via SSH | Multi-supervisor loop, jump host, Jira dedup via state file, Teams webhook |
| `check_supervisor_web_cert.sh` | Monitor TKG Supervisor TLS endpoint cert | `openssl s_client`, NOTIFICATION_DAYS thresholds, Teams + Jira |
| `Commvault_Backup_Enhanced.sh` | Create/delete Commvault K8s backup integration | Env-var inputs, auto-detect AKS vs TKG, Jira on failure |
| `Commvault_Backup.sh` | Older CLI-arg version of Commvault script | Positional args pattern |
| `Elastic_Agent_Enhanced.sh` | Create/delete Elastic Fleet agent policy | Kibana REST API, CURL_SSL_FLAG auto-detect, Jira on failure |
| `Elastic_Agent.sh` | Older CLI-arg version of Elastic script | Positional args pattern |
| `SSH_AKS.sh` | SSH to AKS worker nodes, try multiple users | `az aks list`, try user array, SSH key |
| `SSH_TKG.sh` | SSH to TKG worker nodes across clusters | `kubectx`, cluster list arrays (test/prod), `kubectl-vsphere` |
| `wiz_integration_update.sh` | Update Wiz Helm chart on TKG clusters | kubectx loop, tmpfile values, `helm upgrade --install` |
| `wiz_integration_update_aks.sh` | Update Wiz Helm chart on AKS clusters | `az aks get-credentials`, subscription search, admission controller NSE excludes |

---

## Proactive Triggers

Flag these without being asked:
- **Hardcoded password/token in script** → Move to env var (`${VAR:-}`) or base64-encode
- **Missing `set -euo pipefail`** → Add as first non-comment line
- **`curl` without error check** → Check HTTP status code or jq `.error`
- **`ssh` without `ssh-keygen -R`** → Stale known_hosts causes failures
- **`mktemp` file without `trap cleanup EXIT`** → Temp file leak
- **Jira token hardcoded** → Use `${JIRA_API_TOKEN:-}` from env; old `Commvault_Backup.sh` has a real token — rotate it
- **No duplicate-ticket guard** → Add state file check before `jira_create_ticket`
- **`sshpass -p "$(literal_password)"`** → Always use env var for password
- **`curl -k` against public endpoint** → Only acceptable for internal (VPN-gated) services

## Related Skills
- `devops-cicd` — These scripts are called from Azure DevOps pipelines
- `kubernetes-expert` — Scripts interact with AKS + TKG clusters
- `infrastructure-security` — Secret handling, credential rotation
- `terraform-azure` — Resources provisioned by Terraform, managed by these scripts
