# Terraform Azure Resources - Production Ready

Complete production-ready examples using modules from:
> 📦 **Module Source**: https://github.com/OktaySavdi/Azure/tree/main/Modules

---

## Complete Infrastructure Example

### main.tf

```hcl
#----------------------------------------
# Locals
#----------------------------------------
locals {
  name_prefix = "${var.project}-${var.environment}"
  location    = var.location

  common_tags = {
    project      = var.project
    environment  = var.environment
    managed_by   = "terraform"
    owner        = var.owner
    cost_center  = var.cost_center
    created_date = timestamp()
  }
}

#----------------------------------------
# Resource Group
#----------------------------------------
resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name_prefix}"
  location = local.location
  tags     = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

#----------------------------------------
# Virtual Network Module
# Source: github.com/OktaySavdi/Azure/Modules/VirtualNetwork
#----------------------------------------
module "vnet" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/VirtualNetwork?ref=main"

  vnet_name           = "vnet-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  vnet_address_space  = var.vnet_address_space
  dns_servers         = var.dns_servers
  disk_access_name    = "disk-access-${local.name_prefix}"

  # Subnets with NSG and Route Table associations
  subnets = {
    aks-system = {
      subnet_name                               = "snet-aks-system"
      subnet_address_prefix                     = ["10.0.1.0/24"]
      service_endpoints                         = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.ContainerRegistry"]
      private_endpoint_network_policies_enabled = false
      nsg_name                                  = "nsg-aks-system"
      rt_name                                   = "rt-aks"
      private_endpoint_name                     = ""
      delegations                               = []
      tags                                      = local.common_tags
    }
    aks-workload = {
      subnet_name                               = "snet-aks-workload"
      subnet_address_prefix                     = ["10.0.2.0/24"]
      service_endpoints                         = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.ContainerRegistry"]
      private_endpoint_network_policies_enabled = false
      nsg_name                                  = "nsg-aks-workload"
      rt_name                                   = "rt-aks"
      private_endpoint_name                     = ""
      delegations                               = []
      tags                                      = local.common_tags
    }
    private-endpoints = {
      subnet_name                               = "snet-private-endpoints"
      subnet_address_prefix                     = ["10.0.10.0/24"]
      service_endpoints                         = []
      private_endpoint_network_policies_enabled = true
      nsg_name                                  = ""
      rt_name                                   = ""
      private_endpoint_name                     = "pe-disk-access"
      delegations                               = []
      tags                                      = local.common_tags
    }
    appgw = {
      subnet_name                               = "snet-appgw"
      subnet_address_prefix                     = ["10.0.20.0/24"]
      service_endpoints                         = []
      private_endpoint_network_policies_enabled = false
      nsg_name                                  = "nsg-appgw"
      rt_name                                   = ""
      private_endpoint_name                     = ""
      delegations                               = []
      tags                                      = local.common_tags
    }
  }

  # Network Security Groups
  nsgs = {
    aks-system = {
      name = "nsg-aks-system"
      tags = local.common_tags
    }
    aks-workload = {
      name = "nsg-aks-workload"
      tags = local.common_tags
    }
    appgw = {
      name = "nsg-appgw"
      tags = local.common_tags
    }
  }

  # Route Tables
  route_tables = {
    aks = {
      rt_name = "rt-aks"
      routes = [
        {
          name                   = "default-route"
          address_prefix         = "0.0.0.0/0"
          next_hop_type          = "VirtualAppliance"
          next_hop_in_ip_address = var.firewall_ip
        },
        {
          name           = "local-vnet"
          address_prefix = "10.0.0.0/16"
          next_hop_type  = "VnetLocal"
        }
      ]
    }
  }

  tags = local.common_tags
}

#----------------------------------------
# AKS Module
# Source: github.com/OktaySavdi/Azure/Modules/AKS
#----------------------------------------
module "aks" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/AKS?ref=main"

  # Basic Configuration
  prefix              = local.name_prefix
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  kubernetes_version  = var.kubernetes_version
  sku_tier            = "Standard"  # Free, Standard, Premium

  # Network Configuration
  vnet_subnet_id       = module.vnet.subnet_ids["aks-system"]
  network_plugin       = "azure"
  network_policy       = "calico"
  network_plugin_mode  = "overlay"  # For large clusters
  ebpf_data_plane      = "cilium"   # Optional: Cilium CNI
  load_balancer_sku    = "standard"
  net_profile_dns_service_ip = "10.100.0.10"
  net_profile_service_cidr   = "10.100.0.0/16"
  net_profile_outbound_type  = "userDefinedRouting"  # For private clusters

  # Identity
  identity_type = "UserAssigned"
  identity_ids  = [azurerm_user_assigned_identity.aks.id]

  # Private Cluster
  private_cluster_enabled             = true
  private_cluster_public_fqdn_enabled = false
  private_dns_zone_id                 = "System"  # Or specific zone ID

  # Default Node Pool (System)
  agents_pool_name         = "system"
  agents_size              = "Standard_D4s_v5"
  enable_auto_scaling      = true
  agents_min_count         = 2
  agents_max_count         = 5
  agents_max_pods          = 110
  os_disk_size_gb          = 128
  os_disk_type             = "Ephemeral"
  os_sku                   = "AzureLinux"  # Ubuntu, AzureLinux, CBLMariner
  agents_availability_zones = ["1", "2", "3"]
  only_critical_addons_enabled = true  # System pool for critical addons only
  enable_host_encryption   = true

  agents_labels = {
    "nodepool"                         = "system"
    "kubernetes.azure.com/scalesetpriority" = "regular"
  }

  agents_tags = merge(local.common_tags, {
    nodepool = "system"
  })

  # Auto Scaler Profile
  auto_scaler_profile_enabled                    = true
  auto_scaler_profile_balance_similar_node_groups = true
  auto_scaler_profile_expander                    = "least-waste"
  auto_scaler_profile_max_graceful_termination_sec = 600
  auto_scaler_profile_scale_down_delay_after_add   = "10m"
  auto_scaler_profile_scale_down_unneeded          = "10m"
  auto_scaler_profile_scan_interval                = "10s"

  # Azure AD RBAC
  role_based_access_control_enabled = true
  rbac_aad                          = true
  rbac_aad_managed                  = true
  rbac_aad_azure_rbac_enabled       = true
  rbac_aad_admin_group_object_ids   = var.aks_admin_group_ids
  local_account_disabled            = true  # Disable local admin

  # Add-ons
  azure_policy_enabled                = true
  log_analytics_workspace_enabled     = true
  log_analytics_workspace_id          = module.log_analytics.id
  oidc_issuer_enabled                 = true
  workload_identity_enabled           = true
  key_vault_secrets_provider_enabled  = true
  secret_rotation_enabled             = true
  secret_rotation_interval            = "2m"
  microsoft_defender_enabled          = true
  image_cleaner_enabled               = true
  image_cleaner_interval_hours        = 48

  # Maintenance Windows
  maintenance_window = {
    allowed = [
      {
        day   = "Saturday"
        hours = [1, 2, 3, 4, 5, 6]
      },
      {
        day   = "Sunday"
        hours = [1, 2, 3, 4, 5, 6]
      }
    ]
    not_allowed = []
  }

  maintenance_window_auto_upgrade = {
    frequency    = "Weekly"
    interval     = 1
    duration     = 4
    day_of_week  = "Sunday"
    start_time   = "02:00"
    utc_offset   = "+01:00"
    not_allowed  = []
  }

  # Additional Node Pools
  node_pools = {
    workload = {
      name                   = "workload"
      vm_size                = "Standard_D8s_v5"
      min_count              = 2
      max_count              = 20
      max_pods               = 110
      os_disk_size_gb        = 256
      os_disk_type           = "Ephemeral"
      os_sku                 = "AzureLinux"
      vnet_subnet_id         = module.vnet.subnet_ids["aks-workload"]
      availability_zones     = ["1", "2", "3"]
      enable_auto_scaling    = true
      enable_host_encryption = true
      node_labels = {
        "nodepool" = "workload"
        "workload" = "general"
      }
      node_taints = []
      tags        = local.common_tags
    }
    spot = {
      name                   = "spot"
      vm_size                = "Standard_D8s_v5"
      min_count              = 0
      max_count              = 50
      max_pods               = 110
      os_disk_size_gb        = 256
      os_disk_type           = "Ephemeral"
      os_sku                 = "AzureLinux"
      vnet_subnet_id         = module.vnet.subnet_ids["aks-workload"]
      availability_zones     = ["1", "2", "3"]
      enable_auto_scaling    = true
      enable_host_encryption = true
      priority               = "Spot"
      eviction_policy        = "Delete"
      node_labels = {
        "nodepool"                              = "spot"
        "kubernetes.azure.com/scalesetpriority" = "spot"
      }
      node_taints = ["kubernetes.azure.com/scalesetpriority=spot:NoSchedule"]
      tags        = local.common_tags
    }
    gpu = {
      name                   = "gpu"
      vm_size                = "Standard_NC6s_v3"  # GPU VM
      min_count              = 0
      max_count              = 10
      max_pods               = 30
      os_disk_size_gb        = 256
      os_disk_type           = "Managed"
      os_sku                 = "Ubuntu"  # GPU requires Ubuntu
      vnet_subnet_id         = module.vnet.subnet_ids["aks-workload"]
      availability_zones     = ["1"]
      enable_auto_scaling    = true
      enable_host_encryption = false
      node_labels = {
        "nodepool"                        = "gpu"
        "accelerator"                     = "nvidia"
        "nvidia.com/gpu.present"          = "true"
      }
      node_taints = ["nvidia.com/gpu=present:NoSchedule"]
      tags        = local.common_tags
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_resource_group.main,
    module.vnet
  ]
}

#----------------------------------------
# ACR Module
# Source: github.com/OktaySavdi/Azure/Modules/ACR
#----------------------------------------
module "acr" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/ACR?ref=main"

  acr_name            = "acr${replace(local.name_prefix, "-", "")}"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  sku                 = "Premium"
  admin_enabled       = false

  # Zone Redundancy
  zone_redundancy_enabled = true

  # Geo Replications
  georeplications = [
    {
      location                = "northeurope"
      zone_redundancy_enabled = true
      tags                    = local.common_tags
    }
  ]

  # Network Rules
  network_rule_set = {
    default_action = "Deny"
    ip_rule = [
      {
        action   = "Allow"
        ip_range = var.allowed_ip_ranges
      }
    ]
    virtual_network = [
      {
        action    = "Allow"
        subnet_id = module.vnet.subnet_ids["aks-system"]
      },
      {
        action    = "Allow"
        subnet_id = module.vnet.subnet_ids["aks-workload"]
      }
    ]
  }

  # Retention Policy
  retention_policy = {
    enabled = true
    days    = 30
  }

  # Trust Policy
  trust_policy = {
    enabled = true
  }

  # Export Policy (for air-gapped scenarios)
  export_policy_enabled = false

  tags = local.common_tags
}

# ACR Pull Role for AKS
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = module.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = module.acr.acr_id
  skip_service_principal_aad_check = true
}

#----------------------------------------
# Key Vault Module
# Source: github.com/OktaySavdi/Azure/Modules/Keyvault
#----------------------------------------
module "keyvault" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/Keyvault?ref=main"

  key_vault_name              = "kv-${local.name_prefix}"
  resource_group_name         = azurerm_resource_group.main.name
  location                    = local.location
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "premium"  # standard or premium
  soft_delete_retention_days  = 90
  purge_protection_enabled    = true
  enable_rbac_authorization   = true
  enabled_for_deployment      = false
  enabled_for_disk_encryption = true
  enabled_for_template_deployment = false
  public_network_access_enabled   = false

  # Network ACLs
  network_acls = {
    bypass                     = "AzureServices"
    default_action             = "Deny"
    ip_rules                   = var.allowed_ip_ranges
    virtual_network_subnet_ids = [
      module.vnet.subnet_ids["aks-system"],
      module.vnet.subnet_ids["aks-workload"]
    ]
  }

  tags = local.common_tags
}

# Key Vault Secrets User Role for AKS
resource "azurerm_role_assignment" "aks_keyvault" {
  principal_id         = module.aks.key_vault_secrets_provider_identity[0].object_id
  role_definition_name = "Key Vault Secrets User"
  scope                = module.keyvault.key_vault_id
}

#----------------------------------------
# Storage Account Module
# Source: github.com/OktaySavdi/Azure/Modules/StorageAccount
#----------------------------------------
module "storage" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/StorageAccount?ref=main"

  storage_account_name     = "st${replace(local.name_prefix, "-", "")}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = local.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"
  access_tier              = "Hot"

  # Security
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
  infrastructure_encryption_enabled = true

  # Network Rules
  network_rules = {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    ip_rules                   = var.allowed_ip_ranges
    virtual_network_subnet_ids = [
      module.vnet.subnet_ids["aks-system"]
    ]
  }

  # Blob Properties
  blob_properties = {
    versioning_enabled       = true
    change_feed_enabled      = true
    last_access_time_enabled = true
    delete_retention_policy = {
      days = 30
    }
    container_delete_retention_policy = {
      days = 7
    }
  }

  # Lifecycle Management
  lifecycle_rules = [
    {
      name    = "cleanup-old-versions"
      enabled = true
      filters = {
        blob_types = ["blockBlob"]
      }
      actions = {
        version = {
          delete_after_days_since_creation = 90
        }
      }
    }
  ]

  # Containers
  containers = [
    {
      name                  = "backups"
      container_access_type = "private"
    },
    {
      name                  = "logs"
      container_access_type = "private"
    },
    {
      name                  = "artifacts"
      container_access_type = "private"
    }
  ]

  tags = local.common_tags
}

#----------------------------------------
# Private Endpoint Module
# Source: github.com/OktaySavdi/Azure/Modules/PrivateEndpoint
#----------------------------------------
module "pe_keyvault" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/PrivateEndpoint?ref=main"

  private_endpoint_name   = "pe-kv-${local.name_prefix}"
  resource_group_name     = azurerm_resource_group.main.name
  location                = local.location
  subnet_id               = module.vnet.subnet_ids["private-endpoints"]
  private_connection_resource_id = module.keyvault.key_vault_id
  subresource_names       = ["vault"]
  is_manual_connection    = false

  private_dns_zone_group = {
    name                 = "keyvault-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.keyvault.id]
  }

  tags = local.common_tags
}

module "pe_acr" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/PrivateEndpoint?ref=main"

  private_endpoint_name   = "pe-acr-${local.name_prefix}"
  resource_group_name     = azurerm_resource_group.main.name
  location                = local.location
  subnet_id               = module.vnet.subnet_ids["private-endpoints"]
  private_connection_resource_id = module.acr.acr_id
  subresource_names       = ["registry"]
  is_manual_connection    = false

  private_dns_zone_group = {
    name                 = "acr-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.acr.id]
  }

  tags = local.common_tags
}

#----------------------------------------
# Managed Identity Module
# Source: github.com/OktaySavdi/Azure/Modules/ManagedIdentity
#----------------------------------------
resource "azurerm_user_assigned_identity" "aks" {
  name                = "id-aks-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "workload" {
  name                = "id-workload-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  tags                = local.common_tags
}

# Federated Identity Credential for Workload Identity
resource "azurerm_federated_identity_credential" "workload" {
  name                = "fc-workload"
  resource_group_name = azurerm_resource_group.main.name
  parent_id           = azurerm_user_assigned_identity.workload.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = module.aks.oidc_issuer_url
  subject             = "system:serviceaccount:default:workload-sa"
}

#----------------------------------------
# Log Analytics
#----------------------------------------
module "log_analytics" {
  source = "git::https://github.com/OktaySavdi/Azure.git//Modules/LogAnalytics?ref=main"

  name                = "log-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  sku                 = "PerGB2018"
  retention_in_days   = 90

  tags = local.common_tags
}

#----------------------------------------
# Private DNS Zones
#----------------------------------------
resource "azurerm_private_dns_zone" "keyvault" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone" "acr" {
  name                = "privatelink.azurecr.io"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone" "aks" {
  name                = "privatelink.${local.location}.azmk8s.io"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

# DNS Zone VNet Links
resource "azurerm_private_dns_zone_virtual_network_link" "keyvault" {
  name                  = "link-keyvault"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.keyvault.name
  virtual_network_id    = module.vnet.vnet_id
  registration_enabled  = false
  tags                  = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "acr" {
  name                  = "link-acr"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.acr.name
  virtual_network_id    = module.vnet.vnet_id
  registration_enabled  = false
  tags                  = local.common_tags
}

#----------------------------------------
# Data Sources
#----------------------------------------
data "azurerm_client_config" "current" {}
data "azurerm_subscription" "current" {}

data "azurerm_kubernetes_service_versions" "current" {
  location        = local.location
  include_preview = false
}
```

---

## terraform.tfvars (Production Example)

```hcl
# Project Configuration
project     = "myproject"
environment = "prod"
location    = "westeurope"
owner       = "platform-team"
cost_center = "CC-12345"

# Network Configuration
vnet_address_space = ["10.0.0.0/16"]
dns_servers        = ["10.0.0.4", "10.0.0.5"]  # Custom DNS
firewall_ip        = "10.0.100.4"  # Azure Firewall IP

# AKS Configuration
kubernetes_version     = "1.29"  # Or use latest from data source
aks_admin_group_ids    = ["00000000-0000-0000-0000-000000000000"]  # AAD Group

# Access Control
allowed_ip_ranges = [
  "203.0.113.0/24",  # Corporate IP range
  "198.51.100.0/24"  # VPN range
]

# Tags
tags = {
  project         = "myproject"
  environment     = "prod"
  cost_center     = "CC-12345"
  data_classification = "confidential"
  compliance      = "iso27001"
}
```

---

## Module Usage Reference

| Module | Path | Description |
|--------|------|-------------|
| **AKS** | `Modules/AKS` | Full AKS cluster with advanced features |
| **AKS_Nodepool** | `Modules/AKS_Nodepool` | Additional node pools |
| **VirtualNetwork** | `Modules/VirtualNetwork` | VNet, Subnets, NSG, Routes, Private Endpoints |
| **ACR** | `Modules/ACR` | Container Registry with geo-replication |
| **Keyvault** | `Modules/Keyvault` | Key Vault with RBAC |
| **StorageAccount** | `Modules/StorageAccount` | Storage with lifecycle management |
| **PrivateEndpoint** | `Modules/PrivateEndpoint` | Private Endpoints for PaaS |
| **ManagedIdentity** | `Modules/ManagedIdentity` | User Assigned Identities |
| **RoleAssignement** | `Modules/RoleAssignement` | RBAC Role Assignments |
| **VirtualMachines_Linux** | `Modules/VirtualMachines_Linux` | Linux VMs |
| **VirtualMachines_Windows** | `Modules/VirtualMachines_Windows` | Windows VMs |
| **NatGateway** | `Modules/NatGateway` | NAT Gateway |
| **PublicIP** | `Modules/PublicIP` | Public IP addresses |
| **VPN** | `Modules/VPN` | VPN Gateway |
| **Logic_Apps** | `Modules/Logic_Apps` | Azure Logic Apps |
| **K8S_Namespace** | `Modules/K8S_Namespace` | Kubernetes Namespaces |

---

## Production Checklist

### Security
- [ ] Private cluster enabled
- [ ] Azure AD RBAC enabled
- [ ] Local accounts disabled
- [ ] Azure Policy enabled
- [ ] Microsoft Defender enabled
- [ ] Host encryption enabled
- [ ] Network policies (Calico/Cilium)
- [ ] Private endpoints for PaaS
- [ ] Key Vault for secrets
- [ ] Workload Identity configured
- [ ] NSGs on all subnets

### High Availability
- [ ] Multi-zone deployment
- [ ] Multiple node pools
- [ ] Auto-scaling enabled
- [ ] System node pool separated
- [ ] PDB defined for workloads

### Operations
- [ ] Maintenance windows configured
- [ ] Log Analytics integrated
- [ ] Container Insights enabled
- [ ] Image cleaner enabled
- [ ] Upgrade settings configured

### Cost Optimization
- [ ] Spot instances for non-critical
- [ ] Auto-scaling boundaries set
- [ ] Right-sized VMs
- [ ] Reserved instances evaluated
