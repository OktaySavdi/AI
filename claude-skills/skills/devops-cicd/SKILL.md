---
name: "devops-cicd"
description: >
  DevOps and CI/CD specialist for Azure DevOps Pipelines (YAML), GitHub Actions,
  Ansible automation, shell scripting best practices, and Python tooling. Covers
  pipeline design, approval gates, reusable templates, secret variable groups,
  and deployment strategies. Grounded in Pipelines (Azure + TKG).
  Activate for any pipeline, automation, or scripting work.
license: MIT
metadata:
  version: 2.0.0
  author: IT Infrastructure
  category: engineering
---

# DevOps & CI/CD Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/pipeline:generate` | Generate an Azure DevOps YAML pipeline for a resource type |
| `/pipeline:review` | Review pipeline for security, secrets, and best practices |
| `/pipeline:template` | Design or update a reusable step template |
| `/script:review` | Review shell/PowerShell script for safety and quality |
| `/tkg:pipeline` | Generate a TKG (vSphere) cluster lifecycle pipeline |

## When This Skill Activates

- "Create / review this pipeline"
- "Add a pipeline for [ACR / AKS / AKS nodepool / Keyvault / VNET / TKG / ...]"
- "Write a bash / PowerShell script for..."
- "Azure DevOps stage with approval gate"
- "Pipeline is failing at..."
- Any request involving: `.yml` pipelines, Azure DevOps, bash, Ansible, Docker, Dockerfile

---

## Pipeline Repository Layout

```
Pipelines/
├── Azure/                   # All Azure resource provisioning pipelines
│   ├── ACR/                 # Container Registry
│   ├── AKS/                 # Kubernetes cluster
│   ├── AKS_Delete/          # Cluster teardown
│   ├── AKS_NodePool/        # Node pool add
│   ├── AKS_NodePool_Delete/ # Node pool remove
│   ├── AKS_Upgrade/         # Control-plane + node upgrade
│   ├── Databricks/
│   ├── DeleteResource/      # Generic resource destroy
│   ├── Elastic_Agent_Update/
│   ├── Functions/
│   ├── Keyvault/            # Key Vault create (legacy)
│   ├── Keyvault_new/        # Key Vault create (RBAC mode)
│   ├── ManagedIdentity/
│   ├── NATGateway/
│   ├── NSG_Internal/ + NSG_Rule/
│   ├── OpenAI/
│   ├── Policy_Exemption/    # Kyverno/OPA exception pipeline
│   ├── PrivateEndpoint/
│   ├── Private_DNSZone/
│   ├── Private_DNS_Resolver/
│   ├── PublicIP/
│   ├── Quota/
│   ├── ResourceGroup/
│   ├── Role/ + RoleAssignment/ + Subscription/
│   ├── Storage/
│   ├── VNET/ + VirtualNetwork/
│   ├── VirtualMachine_Linux/ + VirtualMachine_Windows/
│   ├── WebApp/
│   ├── scripts/             # Helper bash/PowerShell scripts
│   └── templates/           # Reusable step templates (YAML)
└── TKG/                     # vSphere TKG cluster lifecycle pipelines
    ├── ServiceAccount_Create/
    ├── SupervisorNamespace_Create/
    ├── SupervisorNamespace_QuotaExtension/
    ├── TKG_AddNodePool/
    ├── TKG_Create/
    ├── TKG_Delete/
    ├── TKG_ResizeNodePool/
    ├── TKG_RoleAssignment/
    ├── TKG_Upgrade/
    └── TKG_VersionReport/
```

---

## Azure Pipeline Canonical Structure

Every Azure resource pipeline follows this skeleton:

```yaml
trigger: none                    # ALL pipelines: manual trigger only

variables:
- group: PIPELINE_CONFIG         # Contains: AZURE_SERVICE_CONNECTION, tagversion,
                                 #   resourceGroupName, storageAccountName, containerName,
                                 #   IPAM_TOKEN, serviceNowConnection, JIRA_API_TOKEN
- name: owner_email
  value: '<TEAM_EMAIL>'

parameters:
- name: subscription_id
  displayName: 'Subscription ID'
  default: '<SUBSCRIPTION_ID>'   # your Azure subscription ID
- name: environment
  displayName: 'Environment'
  default: 'prod'
  values: [prod, nonprod, dev, test, stg]
- name: location
  displayName: 'Location'
  default: '<AZURE_REGION>'                          # Primary Azure region
- name: project_name
  displayName: 'Project Name'
  default: 'myproject'
- name: change
  displayName: 'Change Request (ServiceNow)'
  default: 'CHG0000001'
- name: skipServiceNow
  displayName: 'Skip ServiceNow (internal environments)'
  default: 'false'
- name: tagversion                                   # TfModules git tag to pin
  type: string
  default: ' '                                       # space = use variable group default

jobs:
  - job: create
    displayName: 'Create <Resource>'
    pool: <AGENT_POOL>                                # Azure pipelines agent pool
    workspace:
      clean: all
    steps:
      # ─── 1. CHECKOUT ─────────────────────────────────────────────────────
      - checkout: git://<ORG>/Resources               # Stores tfvars state per resource
        persistCredentials: true
      - ${{ if eq(parameters.tagversion, ' ') }}:
        - checkout: git://<ORG>/TfModules@refs/tags/$(tagversion)   # pin via variable group
      - ${{ if ne(parameters.tagversion, ' ') }}:
        - checkout: git://<ORG>/TfModules@refs/tags/${{parameters.tagversion}}
      - checkout: self

      # ─── 2. GENERATE NAME ────────────────────────────────────────────────
      - template: ../templates/generate-name-for-resources.yml
        parameters:
          resource_short_name: '<short>'             # e.g. aks, kv, st, acr, rg, pe, func
          environment: '${{ parameters.environment }}'
          project_name: '${{ parameters.project_name }}'
          location: '${{ parameters.location }}'
          subscription_id: '${{ parameters.subscription_id }}'
          resource_group_name: '${{ parameters.resource_group_name }}'
          serviceConnection: '$(AZURE_SERVICE_CONNECTION)'

      - bash: |
          echo '<resource_var>="$(resource_name)"' >> parameters.auto.tfvars
          echo "##vso[task.setvariable variable=<resource_var>]$(resource_name)"
        workingDirectory: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
        displayName: "Capture resource name"

      # ─── 3. GET SUBNET (when VNet integration needed) ────────────────────
      - template: ../templates/get-subnet-id.yml
        parameters:
          subscription_id: '${{ parameters.subscription_id }}'
          subnet_name: '${{ parameters.subnet_name }}'
          serviceConnection: '$(AZURE_SERVICE_CONNECTION)'

      - bash: |
          echo 'subnet_id="$(subnet_id)"' >> parameters.auto.tfvars
        workingDirectory: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
        displayName: "Add subnet_id to tfvars"

      # ─── 4. WRITE ALL PARAMS TO TFVARS ───────────────────────────────────
      - ${{ each item in parameters }}:
        - ${{ if notIn(item.key, 'change', 'skipServiceNow', 'tagversion') }}:
          - script: |
              echo '${{ item.key }}=${{ item.value }}' >> parameters.auto.tfvars
            displayName: "Add param - ${{ item.key }}"
            workingDirectory: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'

      # ─── 5. TERRAFORM init / plan / apply ────────────────────────────────
      - template: ../templates/terraform-steps.yml
        parameters:
          workingDirectory: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
          stateFilePath: '$(subscription_name)/<ResourceType>/$(resource_name)/terraform.tfstate'
          serviceConnection: '$(AZURE_SERVICE_CONNECTION)'
          isApply: true

      # ─── 6. STORE TFVARS TO RESOURCES REPO ───────────────────────────────
      - template: ../templates/tfvars-store-steps.yml
        parameters:
          workingDirectory: '$(System.DefaultWorkingDirectory)/Resources'
          sourceFilePath: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
          targetFilePath: '$(subscription_name)/<ResourceType>/$(resource_name)'

      # ─── 7. WIZ (optional) ───────────────────────────────────────────────
      - ${{ if eq(parameters.application_deploy, 'true') }}:
        - template: ../templates/wiz.yml

  # ─── SERVICENOW CLOSE (when skipServiceNow=false) ──────────────────────────
  - ${{ if eq(parameters.skipServiceNow, false) }}:
    - job: succeeded_change
      displayName: 'Update Change Request — Succeeded'
      pool: server
      dependsOn: create
      condition: succeeded()
      variables:
        name: $[dependencies.create.outputs['generatename_<short>.service_resource_name']]
      steps:
      - task: UpdateServiceNowChangeRequest@2
        inputs:
          ServiceNowConnection: '$(serviceNowConnection)'
          ChangeRequestNumber: '${{ parameters.change }}'
          NewStatus: '0'
          WorkNotes: '<Resource> $(name) created successfully.'
          otherParameters: |
            { "u_close_code": "successful", "u_close_notes": "<Resource> $(name) created." }

    - job: failed_change
      displayName: 'Update Change Request — Failed'
      pool: server
      dependsOn: create
      condition: failed()
      variables:
        errorMessage: $[dependencies.create.outputs['ErrorHandler.final_error_message']]
      steps:
      - task: UpdateServiceNowChangeRequest@2
        inputs:
          ServiceNowConnection: '$(serviceNowConnection)'
          ChangeRequestNumber: '${{ parameters.change }}'
          NewStatus: '0'
          WorkNotes: '<Resource> task [$(Build.BuildId)] failed. Error: $(errorMessage)'
          otherParameters: |
            { "u_close_code": "-12", "u_close_notes": "<Resource> task [$(Build.BuildId)] failed. Error: $(errorMessage)" }
```

---

## Reusable Templates Reference

### `generate-name-for-resources.yml`
**Input parameters**: `resource_short_name`, `environment`, `project_name`, `location`, `subscription_id`, `resource_group_name`, `serviceConnection`, `team_name` (optional)

**Output variables**: `$(resource_name)`, `$(subscription_name)`, `service_resource_name` (isOutput=true on task `generatename_<short>`)

**Naming logic** (queries variable group 6 for region code):
| `resource_short_name` | Pattern |
|---|---|
| `rg` | `az{region}-rg-{team}-{project}-{env}-0N` |
| `kv`, `st`, `acr` | `az{region}{short}{project}{env}0N` (no hyphens) |
| all others | `az{region}-{short}-{project}-{env}-0N` |

```yaml
- template: ../templates/generate-name-for-resources.yml
  parameters:
    resource_short_name: 'aks'    # aks | kv | st | acr | rg | pe | func | asp | wa | ng | pip | nsg | rt
    environment: '${{ parameters.environment }}'
    project_name: '${{ parameters.project_name }}'
    location: '${{ parameters.location }}'
    subscription_id: '${{ parameters.subscription_id }}'
    resource_group_name: '${{ parameters.resource_group_name }}'
    serviceConnection: '$(AZURE_SERVICE_CONNECTION)'
```

### `terraform-steps.yml`
Runs TerraformTaskV4@4: init → plan → apply (conditional).

```yaml
- template: ../templates/terraform-steps.yml
  parameters:
    workingDirectory: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
    stateFilePath: '$(subscription_name)/<ResourceType>/$(resource_name)/terraform.tfstate'
    serviceConnection: '$(AZURE_SERVICE_CONNECTION)'
    isPlan: true                  # default: true
    isApply: true                 # default: true — set false for plan-only PRs
```

Backend config: reads `$(resourceGroupName)`, `$(storageAccountName)`, `$(containerName)` from `PIPELINE_CONFIG` variable group.

### `get-subnet-id.yml`
Looks up subnet ID across all VNets in a subscription by name. Sets `$(subnet_id)` and `$(vnet_id)`.

```yaml
- template: ../templates/get-subnet-id.yml
  parameters:
    subscription_id: '${{ parameters.subscription_id }}'
    subnet_name: '${{ parameters.subnet_name }}'   # full subnet name, e.g. <prefix>-snet-aks-prod-01
    serviceConnection: '$(AZURE_SERVICE_CONNECTION)'
```

### `tfvars-store-steps.yml`
Copies `parameters.auto.tfvars` to `Resources` repo under `{subscription_name}/{ResourceType}/{resource_name}/` and commits.

```yaml
- template: ../templates/tfvars-store-steps.yml
  parameters:
    workingDirectory: '$(System.DefaultWorkingDirectory)/Resources'
    sourceFilePath: '$(System.DefaultWorkingDirectory)/Pipelines/Azure/<Module>'
    targetFilePath: '$(subscription_name)/<ResourceType>/$(resource_name)'
```

### `check-resource-exists.yml`
Pre-flight check — sets `$(CheckResourceExists.resource_available)` to `true`/`false`.

```yaml
- template: ../templates/check-resource-exists.yml
  parameters:
    resourceName: '$(resource_name)'
    resourceGroupName: '${{ parameters.resource_group_name }}'
    subscriptionId: '${{ parameters.subscription_id }}'
    serviceConnection: '$(AZURE_SERVICE_CONNECTION)'
    resourceType: 'AKS'
```

### `wiz.yml`
Deploys Wiz sensor to a newly created resource. Called at end of AKS/VM pipelines.

### `role-assignment.yml` / `role-assignment-sub-level.yml`
Assigns an Azure RBAC role to a principal. Used inside resource pipelines after creation.

---

## Azure Pipeline — Per Resource Patterns

### AKS
```yaml
parameters:
- name: subscription_id
- name: resource_group_name
- name: location
- name: environment               # prod | nonprod | dev | test | stg
- name: kubernetes_version        # e.g. "1.31"
- name: project_name
- name: sku_tier                  # Standard | Free | Premium
- name: rbac_aad_admin_group_name # type: object (list of AAD group names)
- name: subnet_name               # name of the AKS subnet
- name: cluster_auto_upgrade      # type: boolean
- name: agents_availability_zones # e.g. '["1","2","3"]'
- name: add_on                    # object: open_service_mesh_enabled, enable_auto_scaling, commvault_backup, reservation, reservation_year
- name: default_node_pool         # object: name, vm_size, os_sku, os_disk_size_gb, node_count, min_count, max_count, max_pods
- name: application_deploy        # 'true' → deploys Wiz, Elastic, Commvault post-create
- name: change
- name: skipServiceNow
- name: tagversion
```
**Name templates**: `aks` → `get-subnet-id` → write tfvars → `terraform-steps` → `tfvars-store-steps` → (if application_deploy) Wiz/Elastic/Commvault

### AKS_NodePool
Same structure as AKS, adds `kubernetes_cluster_name` parameter. Calls `check-resource-exists` to prevent duplicate pool names.

### AKS_Upgrade
```yaml
parameters:
- name: cluster_name              # Exact AKS cluster name
- name: resource_group_name
- name: subscription_id
- name: environment
- name: kubernetes_version        # Target version, e.g. "1.32"
- name: change
- name: skipServiceNow
```
Steps: check cluster state → start upgrade (`az aks upgrade`) → poll for completion → update ServiceNow.

### Keyvault_new (RBAC mode)
Same skeleton + generates `kv` name → resolves PE subnet → writes `enable_rbac_authorization = true` to tfvars.

### VNET (most complex)
```yaml
parameters:
- name: subscription_id
- name: location
- name: environment
- name: project_name
- name: subnets                   # type: object — list of roles: [aks, others, apg, db, function, webapp]
- name: virtual_hub               # azure | paloalto-<region1> | paloalto-<region2> | paloalto-<region3>
- name: cidr_range                # Paloalto only: /24 | /25 | /26 | /27 | /28 | /29
- name: change
- name: skipServiceNow
- name: tagversion
```
**Key steps**:
1. Generate RG name + create RG
2. Resolve virtual hub ID from `virtual_hub` parameter
3. Call `subnet_allocator.sh allocate` (uses `IPAM_TOKEN` from PIPELINE_CONFIG)
4. Expand subnet config via `jq` — auto-generates NSG names, RT names, subnet names, service endpoints, delegations, private endpoint names
5. Write all to `parameters.auto.tfvars`
6. `terraform-steps.yml`
7. `tfvars-store-steps.yml`
8. On failure: `subnet_allocator.sh release` (rollback)

**Subnet naming rules**:
- `azure` hub: NSGs created; names = `az{region}-{short}-{key}-{env}-01`
- `paloalto-*` hubs: NO NSGs; all subnets share one name derived from VNet name
- Routes: `apg` key → Internet; all others → VirtualAppliance (IP per hub)
- Service endpoints: `apg` → none; `db` → Storage+KeyVault+Sql; all others → Storage+KeyVault
- Delegations: `function`/`webapp` → `Microsoft.Web/serverFarms`; others → none

### WebApp / Functions
Validate subnet delegation (`Microsoft.Web/serverFarms`) before proceeding. PE subnet must differ from app subnet.

---

## TKG Pipeline Patterns

### Variable Groups and Connectivity
```yaml
variables:
- group: tkg_config   # Contains: supervisor_stg, supervisor_prod (root passwords),
                      #   tkg_stg_pass, tkg_prod_pass, notification_email, JIRA_API_TOKEN
- name: tkg_stg_server
  value: '<TKG_STG_SUPERVISOR_FQDN>'
- name: tkg_prod_server
  value: '<TKG_PROD_SUPERVISOR_FQDN>'
```

**SSH connectivity pattern**:
```bash
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

if [[ "${{ parameters.environment }}" == "stg" ]]; then
  sshpass -p "$SUPERVISOR_PASS" ssh $SSH_OPTS root@<TKG_STAGING_IP> \
    "bash -s -- '$CLUSTER' '$NS'" <<< "$REMOTE_SCRIPT"
else
  # Production: jump host required
  PROXY_CMD="ssh -i /opt/<ORG>/ssh-key_jump.key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p <JUMP_USER>@<JUMP_HOST_IP>"
  sshpass -p "$SUPERVISOR_PROD_PASS" ssh $SSH_OPTS \
    -o "ProxyCommand=${PROXY_CMD}" root@<TKG_PROD_IP> \
    "bash -s -- '$CLUSTER' '$NS'" <<< "$REMOTE_SCRIPT"
fi
```

### TKG_Upgrade — Full Pattern
1. **Pre-upgrade info**: SSH → list TKRs, ClusterClasses, current cluster state + machine versions
2. **Save and delete ResourceQuota**: `supervisor_namespace_quota.sh ACTION=save-delete` (removes quotas so rolling upgrade isn't blocked)
3. **Check cluster health**: SSH → verify all nodes Ready + no PDB with 0 disruptionsAllowed
4. **Patch cluster**: SSH → auto-detect latest `builtin-generic-v*` ClusterClass → `kubectl patch cluster --type merge` with new classRef + version → wait `--for=condition=Available --timeout=90m`
5. **Post-upgrade verification**: Normalise TKR version (`-vkr.N` suffix stripped) → poll all machines for Running + correct version (30 min budget)
6. **Restore ResourceQuota**: `ACTION=restore` (success path)
7. **Rollback quota restore**: `condition: always()` — restores even on failure
8. **ServiceNow close**: `succeeded_change` / `failed_change` jobs

### TKG Common Parameters
```yaml
parameters:
- name: environment         # stg | prod
- name: cluster_name        # e.g. <prefix>-tkg-app-prod-01
- name: supervisor_namespace # e.g. <prefix>-tns-app-prod-01
- name: change              # ServiceNow CHR number
- name: skipServiceNow      # true → skip ServiceNow
```

### TKG_Upgrade Additional
```yaml
- name: target_tkr_version  # TKR string, e.g. v1.35.0+vmware.2-vkr.4
```

### TKG_VersionReport
SSH to Supervisor → lists all TKR versions → for each cluster shows current version + available upgrades → sends email via `mail` command.

---

## Variable Groups

### `PIPELINE_CONFIG` (Azure pipelines)
| Variable | Purpose |
|----------|---------|
| `AZURE_SERVICE_CONNECTION` | ARM service connection name |
| `tagversion` | Default TfModules git tag |
| `resourceGroupName` | TF state storage RG |
| `storageAccountName` | TF state storage account |
| `containerName` | TF state blob container |
| `IPAM_TOKEN` | IPAM API token (secret) |
| `serviceNowConnection` | ServiceNow service connection |
| `JIRA_API_TOKEN` | Jira API token (secret) |
| `subscriptionId` | Active subscription (updated by VNET pipeline) |
| `subscription_name` | Active subscription name |
| `vnetName` | Current VNet name (updated by VNET pipeline) |

### `tkg_config` (TKG pipelines)
| Variable | Purpose |
|----------|---------|
| `supervisor_stg` | Root password staging Supervisor (secret) |
| `supervisor_prod` | Root password prod Supervisor (secret) |
| `tkg_stg_pass` | vSphere password staging (secret) |
| `tkg_prod_pass` | vSphere password prod (secret) |
| `notification_email` | Default email for TKG reports |

---

## Helper Scripts (`Azure/scripts/`)

| Script | Language | Purpose |
|--------|----------|---------|
| `subnet_allocator.sh` | Bash | Allocate / release subnets from NetBox |
| `supervisor_namespace_quota.sh` | Bash | Save/delete/restore ResourceQuota on TKG Supervisor |
| `supervisor_namespace_create.sh` | Bash | Create vSphere Supervisor namespace |
| `supervisor_namespace_access.sh` | Bash | Grant namespace access |
| `supervisor_namespace_quota_extension.sh` | Bash | Extend quota on existing namespace |
| `tkg_add_nodepool.sh` | Bash | Add node pool to TKG cluster |
| `tkg_resize_nodepool.sh` | Bash | Resize existing TKG node pool |
| `validate-billing-profile.sh` / `.ps1` | Bash/PS | Validate Azure billing profile |
| `validate-invoice-section.sh` / `.ps1` | Bash/PS | Validate Azure invoice section |
| `add-distribution-list-member.ps1` | PowerShell | Add user to distribution list |
| `create-distribution-list.ps1` | PowerShell | Create new distribution list |
| `add-role-assignment-group-member.ps1` | PowerShell | Add member to RBAC role group |
| `trigger-servicenow-group.ps1` | PowerShell | Trigger ServiceNow group assignment |

---

## Shell Script Standards

```bash
#!/usr/bin/env bash
set -euo pipefail
trap 'echo "ERROR at line $LINENO — exit $?" >&2' ERR

# Constants — readonly
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions for reuse
log_info() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] INFO  $*"; }
log_error() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] ERROR $*" >&2; }
die() { log_error "$*"; exit 1; }

# Validate required env vars
: "${REQUIRED_VAR:?Must set REQUIRED_VAR}"

main() {
  log_info "Starting..."
  # ... logic here
}

main "$@"
```

---

## Proactive Triggers

Flag these without being asked:
- **Secret or password in pipeline YAML** → Move to variable group (secret variable) or Key Vault link
- **`trigger: push` on infrastructure pipeline** → All infra pipelines use `trigger: none`
- **`tagversion` not passed to TfModules checkout** → Version drift risk; use pinned tag
- **TKG Supervisor SSH with `StrictHostKeyChecking=accept-new`** → Use `ssh-keygen -R` before connect + `no`
- **Missing `condition: always()` on quota restore step** → Quota not restored on upgrade failure
- **`isApply: false` in non-PR context** → Only `terraform plan` — add `isApply: true` for apply
- **No ServiceNow close jobs** → Add `succeeded_change` + `failed_change` unless `skipServiceNow=true`
- **TKR version with `-vkr.N` suffix in patch command** → Supervisor stores without suffix; normalise before compare
- **`sshpass` password from env var** → Correct pattern (never hardcode in YAML)
- **`workspace: clean: all` missing** → Add to every job to avoid stale tfvars from previous runs

## Related Skills
- `terraform-azure` — Terraform modules called by these pipelines
- `kubernetes-expert` — K8s resources managed by TKG pipelines
- `infrastructure-security` — Pipeline security gates, secret scanning
- `azure-cloud-architect` — Architecture decisions driving new pipeline needs
