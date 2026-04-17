---
name: "terraform-azure"
description: >
  Expert Terraform IaC for Azure. Covers all 28 TfModules: AKS, node pools, ACR,
  Key Vault, Storage, VNet, NSG, Private Endpoints, DNS Resolver, Managed Identity,
  RBAC, Service Principal, OpenAI, Functions, WebApp, VMs, Databricks, App Gateway,
  NAT Gateway, Logic Apps, Cost Management, Virtual Hub (Panorama), K8S namespaces.
  Follows azurerm 4.x + azuread 3.x patterns. Activate for any Terraform or Azure work.
license: MIT
metadata:
  version: 2.0.0
  author: IT Infrastructure
  category: engineering
---

# Terraform Azure Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/tf:review` | Full security + naming + best-practice review of Terraform code |
| `/tf:module` | Generate a new module scaffolded to TfModules structure |
| `/tf:compose` | Compose multiple TfModules for a target architecture |
| `/tf:drift` | Explain drift between Terraform state and real resources |
| `/tf:upgrade` | Upgrade provider version and flag breaking changes |

## When This Skill Activates
- "Write Terraform for..."
- "Review / fix this `.tf` file"
- "Add a module for ACR / AKS / Key Vault / VNet / VM..."
- "How do I use TfModules for..."
- "Terraform plan/apply error..."
- "Add a private endpoint for..."
- Any file: `.tf`, `.tfvars`, `providers.tf`, `variables.tf`

---

## Provider Versions (pinned in TfModules)
```hcl
terraform {
  required_version = ">= 1.3"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.32.0"     # Exact pin — upgrade deliberately
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "3.0.2"      # Used by AKS, Keyvault, ServicePrincipal
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 3.1"     # Used by AKS for SSH key generation
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"     # Used by K8S_Namespace, K8S_Namespace_RoleAssignement
    }
  }
}
```

> 3.x → 4.x breaking changes: `network_profile.docker_bridge_cidr` removed,
> `enable_accelerated_networking` → `accelerated_networking_enabled` on NIC,
> `disable_bgp_route_propagation` → `bgp_route_propagation_enabled` (inverted).

---

## Universal Lifecycle Convention
**Every** AzModule uses this — never remove it:
```hcl
lifecycle {
  ignore_changes = [tags]
}
```
Tags managed centrally via Azure Policy DINE — Terraform must not fight them.

---

## Module-by-Module Reference

### ACR — Azure Container Registry
**Path**: `TfModules/ACR/`
**Resource**: `azurerm_container_registry`
```hcl
module "acr" {
  source = "../../TfModules/ACR"

  name                          = "acrplatformprodweu"   # No hyphens, ≤50 chars
  resource_group_name           = var.resource_group_name
  location                      = var.location
  sku                           = "Standard"              # Basic | Standard | Premium
  admin_enabled                 = false                   # ⚠️ Always false — use UAMI
  public_network_access_enabled = false                   # Default false ✅
  quarantine_policy_enabled     = true                    # Premium only
  zone_redundancy_enabled       = true                    # Premium only
  trust_policy_enabled          = false                   # Premium only — content trust
  georeplications               = []                      # list({location, zone_redundancy_enabled})
  network_rule_set              = null
}
```
**Outputs**: `acr_id`, `login_server`
**Notes**: `public_network_access_enabled` defaults to `false` in the module ✅. Always pair with `PrivateEndpoint` module for production.

---

### AKS — Azure Kubernetes Service
**Path**: `TfModules/AKS/`
**Resource**: `azurerm_kubernetes_cluster`
```hcl
module "aks" {
  source = "../../TfModules/AKS"

  resource_group_name = var.resource_group_name
  cluster_name        = "aks-platform-prod-weu"
  location            = var.location
  dns_prefix          = "aks-platform-prod"

  # Version & upgrades
  kubernetes_version        = "1.31"
  automatic_channel_upgrade = "patch"      # none|patch|rapid|stable|node-image
  node_os_channel_upgrade   = "NodeImage"

  # System node pool
  agents_pool_name             = "system"
  agents_size                  = "Standard_D4ds_v5"
  agents_count                 = 3                        # Set null when autoscaling
  agents_availability_zones    = ["1", "2", "3"]          # Always 3 zones
  only_critical_addons_enabled = true                     # No workloads on system pool
  os_disk_type                 = "Ephemeral"
  os_sku                       = "AzureLinux"
  vnet_subnet_id               = var.subnet_id
  enable_auto_scaling          = false                    # Use AKS_Nodepool for autoscaling user pools

  # Identity — always UAMI
  identity = [{
    type         = "UserAssigned"
    identity_ids = [module.aks_uami.id]
  }]

  # Security
  azure_policy_enabled              = true
  oidc_issuer_enabled               = true
  workload_identity_enabled         = true
  local_account_disabled            = true                # ⚠️ Must be true in prod
  role_based_access_control_enabled = true
  private_cluster_enabled           = true
  private_dns_zone_id               = var.private_dns_zone_id
  disk_encryption_set_id            = var.disk_encryption_set_id

  # AAD admin groups
  rbac_aad_admin_group_name = ["aks-admins"]              # Resolved via azuread_group data source

  # Reliability
  image_cleaner_enabled        = true
  image_cleaner_interval_hours = 48
  cost_analysis_enabled        = true

  # SKU
  sku_tier     = "Standard"                               # Free(no SLA)|Standard|Premium
  support_plan = "KubernetesOfficial"
}
```
**Key Outputs**: `aks_id`, `oidc_issuer_url`, `admin_client_certificate`(sensitive), `admin_host`(sensitive)
**Notes**: Module uses `azuread_group` data source to resolve `rbac_aad_admin_group_name` by display name.

---

### AKS_Nodepool — Additional Node Pools
**Path**: `TfModules/AKS_Nodepool/`
**Resource**: `azurerm_kubernetes_cluster_node_pool`
```hcl
# General workload pool
module "app_nodepool" {
  source = "../../TfModules/AKS_Nodepool"

  name                    = "apps"                        # ≤12 chars, lowercase alpha
  mode                    = "User"                        # System | User
  kubernetes_cluster_id   = module.aks.aks_id
  orchestrator_version    = "1.31"
  vm_size                 = "Standard_D8ds_v5"
  os_disk_type            = "Ephemeral"
  os_disk_size_gb         = 128
  os_sku                  = "AzureLinux"
  vnet_subnet_id          = var.app_subnet_id
  zones                   = ["1", "2", "3"]
  auto_scaling_enabled    = true
  min_count               = 2
  max_count               = 10
  node_count              = 3
  max_pods                = 110
  node_labels             = { "workload-type" = "general" }
  node_taints             = []
  host_encryption_enabled = true
  node_public_ip_enabled  = false
}

# Spot pool for fault-tolerant workloads
module "spot_nodepool" {
  source = "../../TfModules/AKS_Nodepool"

  name                  = "spot"
  mode                  = "User"
  kubernetes_cluster_id = module.aks.aks_id
  orchestrator_version  = "1.31"
  vm_size               = "Standard_D8ds_v5"
  zones                 = ["1", "2", "3"]
  auto_scaling_enabled  = true
  min_count             = 0
  max_count             = 20
  node_count            = 0
  # priority            = "Spot"        # Uncomment when needed (variable commented in module)
  # eviction_policy     = "Delete"      # Uncomment when needed
  node_taints = ["kubernetes.azure.com/scalesetpriority=spot:NoSchedule"]
  node_labels = { "workload-type" = "spot" }
}
```

---

### Keyvault — Azure Key Vault
**Path**: `TfModules/Keyvault/`
**Resource**: `azurerm_key_vault`
```hcl
module "keyvault" {
  source = "../../TfModules/Keyvault"

  resource_group_name        = var.resource_group_name
  location                   = var.location
  key_vault_name             = "kv-platform-prod-weu"
  key_vault_sku_pricing_tier = "standard"                 # standard | premium
  enable_rbac_authorization  = true                       # ⚠️ Default false — always set true for new KVs
  enable_purge_protection    = true                       # ⚠️ Default false — always true in prod
  soft_delete_retention_days = 7                          # 7–90 days

  # Legacy access policies (only if enable_rbac_authorization = false)
  access_policies = []

  # Network ACLs
  network_acls = {
    default_action             = "Deny"
    bypass                     = "AzureServices"
    ip_rules                   = []
    virtual_network_subnet_ids = []
  }

  # Private endpoint (module creates it internally via pe_name variable)
  pe_name   = "pe-kv-platform-prod-weu"
  subnet_id = var.pe_subnet_id
}
```
**⚠️ Security Deviations in Module Defaults**:
- `enable_rbac_authorization = false` — change to `true` for all new Key Vaults
- `enable_purge_protection = false` — change to `true` in production
- `soft_delete_retention_days = null` — set to `7` minimum
- `enabled_for_deployment = true`, `enabled_for_disk_encryption = true`, `enabled_for_template_deployment = true` — review if needed

---

### ManagedIdentity — User-Assigned Managed Identity
**Path**: `TfModules/ManagedIdentity/`
**Resource**: `azurerm_user_assigned_identity` + `azurerm_role_assignment`
```hcl
module "app_uami" {
  source = "../../TfModules/ManagedIdentity"

  name                = "uami-myapp-prod-weu"
  location            = var.location
  resource_group_name = var.resource_group_name

  # Role assignments are created inline
  assignments = [
    {
      scope                = module.keyvault.key_vault_id
      role_definition_name = "Key Vault Secrets User"
    },
    {
      scope                = module.acr.acr_id
      role_definition_name = "AcrPull"
    }
  ]
}
```
**Output**: `id`, `principal_id`, `client_id`
**Federated credential** (for AKS workload identity — add separately):
```hcl
resource "azurerm_federated_identity_credential" "app" {
  name                = "fi-myapp-prod"
  resource_group_name = var.resource_group_name
  parent_id           = module.app_uami.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = module.aks.oidc_issuer_url
  subject             = "system:serviceaccount:mynamespace:myapp-sa"
}
```

---

### RoleAssignement — Azure RBAC Role Assignment
**Path**: `TfModules/RoleAssignement/`
**Resource**: `azurerm_role_assignment`
```hcl
module "aks_acr_pull" {
  source               = "../../TfModules/RoleAssignement"
  scope                = module.acr.acr_id
  role_definition_name = "AcrPull"
  principal_id         = module.aks_uami.principal_id
}
```
**Note**: No `type` on `principal_id` — Terraform auto-detects. Use `depends_on` when the principal is created in the same root module.

---

### Role — Custom Role Definition
**Path**: `TfModules/Role/`
**Resource**: `azurerm_role_definition`
```hcl
module "custom_role" {
  source            = "../../TfModules/Role"
  role_name         = "AKS Node Pool Reader"
  scope             = "/subscriptions/${var.subscription_id}"
  role_description  = "Read-only access to AKS node pools"
  actions           = ["Microsoft.ContainerService/managedClusters/agentPools/read"]
  not_actions       = []
  data_actions      = []
  not_data_actions  = []
  assignable_scopes = ["/subscriptions/${var.subscription_id}"]
}
```

---

### ServicePrincipal — Azure AD Application + SP
**Path**: `TfModules/ServicePrincipal/`
**Resource**: `azuread_application` + `azuread_service_principal` + `azuread_application_password`
```hcl
module "sp" {
  source                  = "../../TfModules/ServicePrincipal"
  service_principal_name  = "sp-myapp-prod"
  service_principal_owner = [data.azurerm_client_config.current.object_id]
  assignments = [
    {
      scope                = var.resource_group_id
      role_definition_name = "Contributor"
    }
  ]
}
```
**⚠️ SECURITY**: Module creates a password valid for 8760h (1 year). Prefer `ManagedIdentity` for workloads running on Azure. Use `ServicePrincipal` only for external systems that cannot use UAMI.

---

### StorageAccount — Azure Storage Account
**Path**: `TfModules/StorageAccount/`
**Resource**: `azurerm_storage_account`
```hcl
module "storage" {
  source = "../../TfModules/StorageAccount"

  storage_account_name     = "stplatformprodweu"         # No hyphens, ≤24 chars
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"                  # Standard | Premium
  account_replication_type = "ZRS"                       # LRS|GRS|RAGRS|ZRS — use ZRS for prod
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"                    # Always TLS1_2

  # ⚠️ Module hardcodes public_network_access_enabled = true — pair with PrivateEndpoint
  default_action                   = "Deny"              # Block all by default
  ip_rules                         = []
  bypass                           = ["AzureServices"]
  allow_nested_items_to_be_public  = false               # Never allow public blobs
  cross_tenant_replication_enabled = false

  # Security features
  versioning_enabled                = true
  enable_advanced_threat_protection = true
  is_hns_enabled                    = false              # true only for ADLS Gen2
}
```
**⚠️ CRITICAL**: `public_network_access_enabled` is hardcoded to `true` in the module source. Always add `PrivateEndpoint` module and set `default_action = "Deny"` in `network_rules`.

---

### PrivateEndpoint — Azure Private Endpoint
**Path**: `TfModules/PrivateEndpoint/`
**Resource**: `azurerm_private_endpoint`
```hcl
# Private endpoint for Storage Account
module "pe_storage" {
  source = "../../TfModules/PrivateEndpoint"

  private_endpoint_name      = "pe-st-platform-prod-weu"
  resource_group_name        = var.resource_group_name
  location                   = var.location
  subnet_id                  = var.pe_subnet_id
  resource_id                = module.storage.storage_account_id
  subresource_names          = ["blob"]                  # blob|file|queue|table|dfs
  private_dns_zone_group_name = "default"
  private_dns_zone_ids       = [var.blob_dns_zone_id]
}

# Common subresource_names by service:
# ACR:          ["registry"]
# Key Vault:    ["vault"]
# Storage blob: ["blob"]
# Storage file: ["file"]
# OpenAI:       ["account"]
# Databricks:   ["databricks_ui_api"]
# Functions:    ["sites"]
# WebApp:       ["sites"]
```

---

### VirtualNetwork — VNet + Route Tables + Subnets
**Path**: `TfModules/VirtualNetwork/`
**Resource**: `azurerm_virtual_network` + `azurerm_route_table` + `azurerm_subnet`
```hcl
module "vnet" {
  source = "../../TfModules/VirtualNetwork"

  vnet_name           = "vnet-platform-prod-weu"
  resource_group_name = var.resource_group_name
  location            = var.location
  vnet_address_space  = ["10.0.0.0/16"]
  dns_servers         = []                               # Empty = Azure-provided DNS

  route_tables = {
    aks = {
      rt_name                      = "rt-aks-prod-weu"
      bgp_route_propagation_enabled = false
      routes = [
        {
          name                   = "default"
          address_prefix         = "0.0.0.0/0"
          next_hop_type          = "VirtualAppliance"
          next_hop_in_ip_address = var.firewall_private_ip
        }
      ]
    }
  }

  subnets = {
    system = {
      name             = "snet-aks-system"
      address_prefixes = ["10.0.0.0/24"]
      service_endpoints = []
    }
    apps = {
      name             = "snet-aks-apps"
      address_prefixes = ["10.0.1.0/22"]
      service_endpoints = []
    }
    pe = {
      name             = "snet-privateendpoints"
      address_prefixes = ["10.0.10.0/24"]
      service_endpoints = []
    }
  }
}
```

---

### NSG_RouteTable — NSG + Route Table (existing VNet)
**Path**: `TfModules/NSG_RouteTable/`
**Resource**: `azurerm_route_table` + `azurerm_network_security_group`
```hcl
module "nsg_rt" {
  source = "../../TfModules/NSG_RouteTable"

  resource_group_name = var.resource_group_name
  location            = var.location
  vnet_name           = module.vnet.vnet_name

  route_tables = {
    aks = {
      rt_name                      = "rt-aks-prod-weu"
      bgp_route_propagation_enabled = false
      routes = [...]
    }
  }

  nsgs = {
    aks = { name = "nsg-aks-prod-weu" }
  }

  nsg_associations      = { ... }
  route_table_associations = { ... }
}
```
**Note**: `disable_bgp_route_propagation` deprecated in azurerm 4.x → use `bgp_route_propagation_enabled = false`.

---

### NetworkSecurityRule — Individual NSG Rules
**Path**: `TfModules/NetworkSecurityRule/`
**Resource**: `azurerm_network_security_rule`
```hcl
module "nsg_rules" {
  source = "../../TfModules/NetworkSecurityRule"

  resource_group_name         = var.resource_group_name
  network_security_group_name = module.nsg_rt.nsg_name

  security_rules = [
    {
      name                       = "AllowHTTPS"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "443"
      source_address_prefix      = "AzureFrontDoor.Backend"
      destination_address_prefix = "*"
    },
    {
      name                       = "DenyAllInbound"
      priority                   = 4096
      direction                  = "Inbound"
      access                     = "Deny"
      protocol                   = "*"
      source_port_range          = "*"
      destination_port_range     = "*"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  ]
}
```

---

### Private_DNS_Resolver — Azure DNS Private Resolver
**Path**: `TfModules/Private_DNS_Resolver/`
**Resource**: `azurerm_private_dns_resolver` + inbound/outbound endpoints + forwarding rulesets
```hcl
module "dns_resolver" {
  source = "../../TfModules/Private_DNS_Resolver"

  resource_group_name              = var.resource_group_name
  resource_group_name_for_dnsresolver = var.resource_group_name
  location                         = var.location
  dns_resolver_name                = "dnsresolver-platform-prod-weu"
  virtual_network_id               = module.vnet.vnet_id
  tags                             = var.tags

  dns_resolver_inbound_endpoints = [
    {
      inbound_endpoint_name = "inbound-primary"
      inbound_subnet_id     = var.dns_inbound_subnet_id
    }
  ]

  dns_resolver_outbound_endpoints = [
    {
      outbound_endpoint_name = "outbound-primary"
      outbound_subnet_id     = var.dns_outbound_subnet_id
      forwarding_rulesets = [
        {
          forwarding_ruleset_name = "ruleset-onprem"
        }
      ]
    }
  ]
}
```

---

### NatGateway — NAT Gateway + Public IP
**Path**: `TfModules/NatGateway/`
**Resources**: `azurerm_public_ip` + `azurerm_nat_gateway` + subnet associations
```hcl
module "nat_gw" {
  source = "../../TfModules/NatGateway"

  resource_group_name = var.resource_group_name
  location            = var.location
  public_ip_name      = "pip-nat-platform-prod-weu"
  allocation_method   = "Static"
  public_ip_sku       = "Standard"
  nat_gateway_name    = "ng-platform-prod-weu"
  subnets             = [module.vnet.subnet_ids["apps"]]
}
```

---

### PublicIP — Azure Public IP
**Path**: `TfModules/PublicIP/`
**Resource**: `azurerm_public_ip`
```hcl
module "pip" {
  source              = "../../TfModules/PublicIP"
  name                = "pip-agw-platform-prod-weu"
  resource_group_name = var.resource_group_name
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "null"                           # "null" string = use name as label
}
```

---

### ResourceGroup — Azure Resource Group
**Path**: `TfModules/ResourceGroup/`
**Resource**: `azurerm_resource_group`
```hcl
module "rg" {
  source              = "../../TfModules/ResourceGroup"
  resource_group_name = "rg-platform-prod-weu"
  location            = var.location
  tags                = var.tags
}
```
**Note**: ResourceGroup does NOT use `lifecycle { ignore_changes = [tags] }` — tags are managed here explicitly.

---

### OpenAI — Azure Cognitive Account (OpenAI)
**Path**: `TfModules/OpenAI/`
**Resource**: `azurerm_cognitive_account` + `azurerm_private_endpoint`
```hcl
module "openai" {
  source = "../../TfModules/OpenAI"

  resource_group_name = var.resource_group_name
  location            = var.location
  openai_name         = "oai-platform-prod-weu"
  kind                = "OpenAI"
  openai_sku_name     = "S0"
  # public_network_access_enabled = false  ← Hardcoded in module ✅

  # Private endpoint (inline in module)
  pe_name   = "pe-oai-platform-prod-weu"
  subnet_id = var.pe_subnet_id
}
```
**Notes**: Module uses `SystemAssigned` identity. `public_network_access_enabled = false` is hardcoded ✅. Model deployments (`azurerm_cognitive_deployment`) are commented out — add separately.

---

### Functions — Azure Function App
**Path**: `TfModules/Functions/`
**Resources**: `azurerm_service_plan` + `azurerm_linux_function_app` + `azurerm_private_endpoint`
```hcl
module "function" {
  source = "../../TfModules/Functions"

  resource_group_name  = var.resource_group_name
  location             = var.location
  service_plan_name    = "asp-myfunction-prod-weu"
  sku_name             = "EP1"                           # Y1(consumption)|EP1|EP2|EP3|P1v2+
  os_type              = "Linux"
  function_name        = "func-myfunction-prod-weu"
  storage_account_name          = module.storage.storage_account_name
  storage_primary_access_key    = module.storage.primary_access_key  # ⚠️ See note below
  subnet_name                   = var.app_subnet_id
  pe_name                       = "pe-func-prod-weu"
  pe_subnet                     = var.pe_subnet_id
  site_config                   = [{ always_on = true }]
}
```
**⚠️ SECURITY**: `storage_primary_access_key` passed as plaintext variable — prefer `storage_uses_managed_identity = true` if module supports it, or store key in Key Vault. `public_network_access_enabled = false` and `ftp_publish_basic_authentication_enabled = false` are set in module ✅.

---

### WebApp — Azure Linux Web App
**Path**: `TfModules/WebApp/`
**Resources**: `azurerm_service_plan` + `azurerm_linux_web_app`
```hcl
module "webapp" {
  source = "../../TfModules/WebApp"

  resource_group_name    = var.resource_group_name
  location               = var.location
  app_service_plan_name  = "asp-myapp-prod-weu"
  sku_name               = "P1v3"
  os_type                = "Linux"
  web_app_name           = "app-myapp-prod-weu"
  subnet_id              = var.app_subnet_id

  site_config = [{
    always_on           = true
    ftps_state          = "Disabled"
    minimum_tls_version = "1.2"
    health_check_path   = "/health"
    http2_enabled       = true
  }]
}
```
**Notes**: `public_network_access_enabled = false`, `ftp_publish_basic_authentication_enabled = false`, `vnet_route_all_enabled = true` all set in module ✅. Module includes static IP restriction for `AzureMonitor` service tag.

---

### VirtualMachines_Linux / VirtualMachines_Windows
**Path**: `TfModules/VirtualMachines_Linux/` and `TfModules/VirtualMachines_Windows/`
```hcl
module "linux_vm" {
  source = "../../TfModules/VirtualMachines_Linux"

  vm_hostname                 = "myvm"
  team_name                   = "platform"
  environment                 = "prod"
  resource_group_name         = var.resource_group_name
  location                    = var.location
  size                        = "Standard_D4ds_v5"
  admin_username              = "azureuser"
  admin_password              = null                     # Use SSH key instead
  disable_password_authentication = true
  vnet_subnet_id              = var.vm_subnet_id
  zone                        = "1"
  enable_accelerated_networking = true
  enable_ip_forwarding        = false
  disk_access_name            = var.disk_access_name
  disk_access_resource_group_name = var.resource_group_name
  availability_set_enabled    = false                    # Use zones instead
  source_image_id             = null                     # Set for custom image
  tags                        = var.tags
}
```
**NIC naming**: hardcoded to `az-nic-{hostname}-{team}-{env}`.
**VM naming**: hardcoded to `az-vm-{hostname}-{team}-{env}`.
**⚠️ SECURITY**: `secure_boot_enabled` is commented out on Linux VM but enabled on Windows VM. Enable for Linux where possible. Never set `admin_password` without `disable_password_authentication = true`.

---

### Databricks — Azure Databricks Workspace
**Path**: `TfModules/Databricks/`
**Resources**: `azurerm_databricks_workspace` + `azurerm_private_endpoint`
```hcl
module "databricks" {
  source = "../../TfModules/Databricks"

  workspace_name                = "dbw-analytics-prod-weu"
  resource_group_name           = var.resource_group_name
  location                      = var.location
  sku                           = "premium"               # standard | premium | trial
  public_network_access_enabled = false                   # Default false ✅
  no_public_ip                  = true                    # Default true ✅
  managed_resource_group_name   = "rg-dbw-managed-prod-weu"
  virtual_network_id            = module.vnet.vnet_id
  public_subnet_name            = "snet-dbw-public"
  private_subnet_name           = "snet-dbw-private"
  network_security_group_rules_required = "NoAzureDatabricksRules"
  storage_account_name          = "stdbwprodweu"
  storage_account_sku_name      = "Standard_LRS"
  private_endpoint_name         = "pe-dbw-prod-weu"
  subnet_id                     = var.pe_subnet_id
  private_dns_zone_group_name   = "default"
  private_dns_zone_ids          = [var.databricks_dns_zone_id]
  subresource_names             = ["databricks_ui_api"]
}
```

---

### APG — Application Gateway
**Path**: `TfModules/APG/`
**Resource**: `azurerm_application_gateway` + UAMI + Key Vault access policy
```hcl
module "agw" {
  source = "../../TfModules/APG"

  name     = "agw-platform-prod-weu"
  rg       = var.resource_group_name
  location = var.location

  # Identity
  create_managed_identity = true
  uai_name                = "uami-agw-platform-prod-weu"

  # TLS certificate from Key Vault
  key_vault_name = module.keyvault.key_vault_name
  key_vault_rg   = var.resource_group_name
  tenant_id      = data.azurerm_client_config.current.tenant_id

  # (remaining AGW config passed via complex variables)
}
```
**Note**: APG module grants Key Vault access policy `Get` on secrets/certificates. If Key Vault uses RBAC mode, replace the `azurerm_key_vault_access_policy` resource in the module with `RoleAssignement` module (`Key Vault Certificates User`).

---

### Logic_Apps — Azure Logic App Workflow
**Path**: `TfModules/Logic_Apps/`
**Resource**: `azurerm_logic_app_workflow`
```hcl
module "logic_apps" {
  source = "../../TfModules/Logic_Apps"

  logic_app = [
    {
      logic_app_name      = "la-myworkflow-prod-weu"
      location            = var.location
      resource_group_name = var.resource_group_name
      workflow_version    = "1.0.0.0"
      workflow_schema     = "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#"
      tags                = var.tags
    }
  ]
}
```

---

### K8S_Namespace — Kubernetes Namespace + RBAC
**Path**: `TfModules/K8S_Namespace/`
**Resources**: `kubernetes_namespace` + `kubernetes_role` + `kubernetes_role_binding`
```hcl
module "namespace" {
  source = "../../TfModules/K8S_Namespace"

  namespace   = "ns-myteam-01"
  environment = "prod"            # "prod" → read-only role | "nonprod" → full access role
  labels      = { team = "myteam", environment = "prod" }
  annotations = {}
  quota       = { requests.cpu = "4", requests.memory = "8Gi", limits.cpu = "8", limits.memory = "16Gi" }
  limitrange  = []

  assign_group = {
    users  = []
    groups = ["myteam-aks-admins"]  # AAD group names
  }
}
```
**RBAC Behaviour**:
- `environment = "nonprod"` → Creates `Role` with `verbs: ["*"]` on `resources: ["*"]`
- `environment = "prod"` → Creates `Role` with `verbs: ["get","list","watch"]` only

---

### K8S_Namespace_RoleAssignement — Namespace Role Binding
**Path**: `TfModules/K8S_Namespace_RoleAssignement/`
**Resources**: `kubernetes_role` + `kubernetes_role_binding_v1`
```hcl
module "ns_rbac" {
  source = "../../TfModules/K8S_Namespace_RoleAssignement"

  namespace   = "ns-myteam-01"
  environment = "prod"
  labels      = { team = "myteam" }

  assign_group = {
    users  = []
    groups = ["myteam-readonly"]
  }
}
```

---

### Cost_Management_View — Azure Cost Management View
**Path**: `TfModules/Cost_Management_View/`
**Resource**: `azurerm_subscription_cost_management_view`
```hcl
module "cost_view" {
  source            = "../../TfModules/Cost_Management_View"
  subscription_id   = var.subscription_id
  subscription_name = "platform-prod"
  distribution_list = "platform-team@example.com"
}
```

---

### Virtual_Hub_Panorama — Virtual WAN Hub + Palo Alto NGFW
**Path**: `TfModules/Virtual_Hub_Panorama/`
**Resources**: `azurerm_virtual_hub` + `azurerm_palo_alto_virtual_network_appliance` + `azurerm_palo_alto_next_generation_firewall_virtual_hub_panorama`
```hcl
module "vhub" {
  source = "../../TfModules/Virtual_Hub_Panorama"

  vwan_name                     = var.vwan_name
  vwan_resource_group_name      = var.vwan_rg
  resource_group_name           = var.resource_group_name
  location                      = var.location
  vhub_name                     = "vhub-platform-prod-weu"
  address_prefix                = "10.100.0.0/23"
  public_ip_name                = "pip-vhub-prod-weu"
  allocation_method             = "Static"
  virtual_network_appliance_name = "vnva-palo-prod-weu"
  virtual_hub_panorama_name     = "panfw-prod-weu"
  panorama_base64_config        = var.panorama_base64_config
  tags                          = var.tags
}
```

---

## Naming Convention
`<type-short>-<workload>-<env>-<region-short>`

| Resource | Format | Example |
|----------|--------|---------|
| Resource Group | `rg-<workload>-<env>-<region>` | `rg-platform-prod-weu` |
| AKS Cluster | `aks-<workload>-<env>-<region>` | `aks-platform-prod-weu` |
| ACR | `acr<workload><env><region>` | `acrplatformprodweu` (no hyphens) |
| Key Vault | `kv-<workload>-<env>-<region>` | `kv-platform-prod-weu` |
| Storage | `st<workload><env><region>` | `stplatformprodweu` (no hyphens, ≤24 chars) |
| UAMI | `uami-<component>-<env>-<region>` | `uami-aks-platform-prod-weu` |
| Private Endpoint | `pe-<svc>-<workload>-<env>-<region>` | `pe-acr-platform-prod-weu` |
| VNet | `vnet-<workload>-<env>-<region>` | `vnet-platform-prod-weu` |
| Subnet | `snet-<purpose>` | `snet-aks-system` |
| NSG | `nsg-<purpose>-<env>-<region>` | `nsg-aks-prod-weu` |
| Route Table | `rt-<purpose>-<env>-<region>` | `rt-aks-prod-weu` |
| App Gateway | `agw-<workload>-<env>-<region>` | `agw-platform-prod-weu` |
| Function App | `func-<workload>-<env>-<region>` | `func-myapp-prod-weu` |
| Web App | `app-<workload>-<env>-<region>` | `app-myapp-prod-weu` |
| VM (Linux/Win) | `az-vm-<hostname>-<team>-<env>` | `az-vm-jumpbox-platform-prod` (hardcoded in module) |

---

## Security Deviations — Known Issues in AzModule Defaults

| Module | Issue | Override Required |
|--------|-------|-------------------|
| `StorageAccount` | `public_network_access_enabled = true` hardcoded | Add `PrivateEndpoint` + `default_action = "Deny"` |
| `Keyvault` | `enable_rbac_authorization = false` | Set `true` for all new Key Vaults |
| `Keyvault` | `enable_purge_protection = false` | Set `true` in production |
| `Keyvault` | `soft_delete_retention_days = null` | Set minimum `7` |
| `ServicePrincipal` | 8760h password created automatically | Use `ManagedIdentity` for Azure workloads |
| `Functions` | `storage_primary_access_key` passed as plaintext | Store in Key Vault; reference via `azurerm_key_vault_secret` data |
| `APG` | Uses Key Vault access policy mode | Replace with RBAC role if KV uses `enable_rbac_authorization = true` |
| `VirtualMachines_Linux` | `secure_boot_enabled` commented out | Enable for new VMs |
| `K8S_Namespace` (nonprod) | `verbs: ["*"]` on all resources | Acceptable for dev; review for staging |
| `OpenAI` | `SystemAssigned` identity | Prefer `UserAssigned` for UAMI-based access control |

---

## Common Data Sources
```hcl
data "azurerm_client_config" "current" {}
data "azurerm_subscription" "current" {}
data "azurerm_resource_group" "main" { name = var.resource_group_name }
data "azuread_group" "admins" { display_name = "aks-admins" }
data "azurerm_key_vault" "shared" {
  name                = "kv-shared-prod-weu"
  resource_group_name = var.resource_group_name
}
data "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  key_vault_id = data.azurerm_key_vault.shared.id
}
```

---

## Proactive Triggers
Flag these without being asked:
- **`public_network_access_enabled = true`** on Storage → Add `PrivateEndpoint` + `default_action = "Deny"`
- **`enable_rbac_authorization = false`** on new Key Vault → Use RBAC mode
- **`enable_purge_protection = false`** on Key Vault → Risk of accidental deletion
- **`ServicePrincipal` module for Azure workload** → Use `ManagedIdentity` + federated credential
- **`admin_enabled = true`** on ACR → Disable; use `AcrPull` RBAC role
- **No `agents_availability_zones`** on AKS → Always spread across `["1","2","3"]`
- **`local_account_disabled = false`** on AKS → Local admin bypasses AAD — enable in prod
- **`sku_tier = "Free"`** on AKS → No uptime SLA — use `Standard`
- **`azure_policy_enabled = false`** on AKS → Azure Policy add-on required for compliance
- **Provider `~>` instead of exact pin** → Pin `azurerm = 4.32.0`, `azuread = 3.0.2`
- **Missing `lifecycle { ignore_changes = [tags] }`** in new module → Add to all resources
- **`disable_password_authentication = false`** on Linux VM → SSH keys only
- **`secure_boot_enabled`** commented out on Linux VM → Enable for new deployments

## Python: Terraform Automation Patterns

Use Python for orchestrating Terraform runs, parsing outputs, and generating `.tfvars`:

```python
import subprocess
import json
from pathlib import Path

TERRAFORM_DIR = Path("Terraform/Pipelines/aks")

def terraform_init() -> None:
    subprocess.run(
        ["terraform", "init", "-upgrade"],
        cwd=TERRAFORM_DIR, check=True
    )

def terraform_plan(var_file: str = "terraform.tfvars") -> str:
    """Run plan and return output as string."""
    result = subprocess.run(
        ["terraform", "plan", f"-var-file={var_file}", "-out=tfplan", "-no-color"],
        cwd=TERRAFORM_DIR, check=True,
        capture_output=True, text=True
    )
    return result.stdout

def terraform_output(key: str) -> str:
    """Read a Terraform output value."""
    result = subprocess.run(
        ["terraform", "output", "-json", key],
        cwd=TERRAFORM_DIR, check=True,
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

```python
# Generate tfvars from Python dict
from dataclasses import dataclass, asdict

@dataclass
class AKSConfig:
    cluster_name: str
    resource_group: str
    node_count: int
    vm_size: str = "Standard_D4ds_v5"
    kubernetes_version: str = "1.30"

def write_tfvars(config: AKSConfig, output_path: Path) -> None:
    lines = []
    for key, value in asdict(config).items():
        if isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        else:
            lines.append(f'{key} = {value}')
    output_path.write_text("\n".join(lines) + "\n")
```

```python
# Parse Terraform plan output to detect resource changes
import re

def parse_plan_summary(plan_output: str) -> dict[str, int]:
    """Extract add/change/destroy counts from terraform plan output."""
    pattern = r"Plan: (\d+) to add, (\d+) to change, (\d+) to destroy"
    match = re.search(pattern, plan_output)
    if not match:
        return {"add": 0, "change": 0, "destroy": 0}
    return {
        "add": int(match.group(1)),
        "change": int(match.group(2)),
        "destroy": int(match.group(3)),
    }
```

## Related Skills
- `kubernetes-expert` — Kubernetes workloads running in AKS clusters created by these modules
- `infrastructure-security` — Deep security review of Azure resources
- `azure-cloud-architect` — Architecture decisions driving module composition
- `devops-cicd` — Azure DevOps pipeline running `terraform plan` / `terraform apply`
