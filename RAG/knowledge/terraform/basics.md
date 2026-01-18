# Terraform Basics - Production Ready

**Terraform** is an Infrastructure as Code (IaC) tool by HashiCorp for provisioning and managing cloud resources.

> 📦 **Module Library**: https://github.com/OktaySavdi/Azure/tree/main/Modules

---

## Module Structure

Each module follows this standard structure:

```
Modules/
├── AKS/                    # Azure Kubernetes Service
├── ACR/                    # Azure Container Registry
├── AKS_Nodepool/           # AKS Node Pool management
├── Keyvault/               # Azure Key Vault
├── VirtualNetwork/         # VNet, Subnets, NSG, Route Tables
├── StorageAccount/         # Azure Storage
├── Resource_Group/         # Resource Groups
├── ManagedIdentity/        # User Assigned Identity
├── PrivateEndpoint/        # Private Endpoints
├── Private_DNS_Resolver/   # DNS Private Resolver
├── PublicIP/               # Public IP addresses
├── NatGateway/             # NAT Gateway
├── NetworkSecurityRule/    # NSG Rules
├── VirtualMachines_Linux/  # Linux VMs
├── VirtualMachines_Windows/# Windows VMs
├── RoleAssignement/        # RBAC Role Assignments
├── ServicePrincipal/       # Service Principal
├── Logic_Apps/             # Azure Logic Apps
├── VPN/                    # VPN Gateway
├── funtion_app_linux/      # Linux Function Apps
├── funtion_app_windows/    # Windows Function Apps
├── HarborProject/          # Harbor Registry Projects
├── K8S_Namespace/          # Kubernetes Namespaces
└── TanzuTKG/               # VMware Tanzu
```

---

## Production-Ready Provider Configuration

### versions.tf

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12.0"
    }
  }

  # Remote State Backend
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stterraformstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
    use_azuread_auth     = true
  }
}
```

### providers.tf

```hcl
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
    virtual_machine {
      delete_os_disk_on_deletion     = true
      graceful_shutdown              = true
      skip_shutdown_and_force_delete = false
    }
    log_analytics_workspace {
      permanently_delete_on_destroy = false
    }
  }

  # Optional: Use specific subscription
  # subscription_id = var.subscription_id
  # tenant_id       = var.tenant_id
}

provider "azuread" {
  tenant_id = var.tenant_id
}

provider "kubernetes" {
  host                   = module.aks.kube_config.host
  client_certificate     = base64decode(module.aks.kube_config.client_certificate)
  client_key             = base64decode(module.aks.kube_config.client_key)
  cluster_ca_certificate = base64decode(module.aks.kube_config.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = module.aks.kube_config.host
    client_certificate     = base64decode(module.aks.kube_config.client_certificate)
    client_key             = base64decode(module.aks.kube_config.client_key)
    cluster_ca_certificate = base64decode(module.aks.kube_config.cluster_ca_certificate)
  }
}
```

---

## Variable Types Reference

### variables.tf (Complete)

```hcl
#----------------------------------------
# Required Variables
#----------------------------------------
variable "project" {
  description = "Project name used in resource naming"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project))
    error_message = "Project name must be lowercase alphanumeric with hyphens only."
  }
}

variable "environment" {
  description = "Environment name (dev, stg, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "stg", "uat", "prod"], var.environment)
    error_message = "Environment must be one of: dev, stg, uat, prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westeurope"

  validation {
    condition = contains([
      "westeurope", "northeurope", "eastus", "eastus2",
      "westus", "westus2", "centralus", "germanywestcentral"
    ], var.location)
    error_message = "Location must be a valid Azure region."
  }
}

#----------------------------------------
# Networking Variables
#----------------------------------------
variable "vnet_address_space" {
  description = "CIDR block for VNet"
  type        = list(string)
  default     = ["10.0.0.0/16"]

  validation {
    condition     = alltrue([for cidr in var.vnet_address_space : can(cidrhost(cidr, 0))])
    error_message = "All values must be valid CIDR blocks."
  }
}

variable "subnets" {
  description = "Map of subnet configurations"
  type = map(object({
    subnet_name                               = string
    subnet_address_prefix                     = list(string)
    service_endpoints                         = optional(list(string), [])
    private_endpoint_network_policies_enabled = optional(bool, true)
    nsg_name                                  = optional(string, "")
    rt_name                                   = optional(string, "")
    private_endpoint_name                     = optional(string, "")
    delegations = optional(list(object({
      delegationname = string
      name           = string
      actions        = list(string)
    })), [])
    tags = optional(map(string), {})
  }))
  default = {}
}

#----------------------------------------
# AKS Variables
#----------------------------------------
variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = null
}

variable "sku_tier" {
  description = "AKS SKU tier (Free, Standard, Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Free", "Standard", "Premium"], var.sku_tier)
    error_message = "SKU tier must be Free, Standard, or Premium."
  }
}

variable "agents_size" {
  description = "VM size for default node pool"
  type        = string
  default     = "Standard_D4s_v5"
}

variable "agents_count" {
  description = "Number of nodes in default pool (when autoscaling disabled)"
  type        = number
  default     = 3
}

variable "enable_auto_scaling" {
  description = "Enable autoscaling for default node pool"
  type        = bool
  default     = true
}

variable "agents_min_count" {
  description = "Minimum nodes when autoscaling enabled"
  type        = number
  default     = 2
}

variable "agents_max_count" {
  description = "Maximum nodes when autoscaling enabled"
  type        = number
  default     = 10
}

variable "node_pools" {
  description = "Additional node pools configuration"
  type = map(object({
    name                     = string
    vm_size                  = string
    node_count               = optional(number, 1)
    min_count                = optional(number)
    max_count                = optional(number)
    max_pods                 = optional(number, 110)
    os_disk_size_gb          = optional(number, 128)
    os_disk_type             = optional(string, "Managed")
    os_sku                   = optional(string, "Ubuntu")
    mode                     = optional(string, "User")
    priority                 = optional(string, "Regular")
    eviction_policy          = optional(string)
    enable_auto_scaling      = optional(bool, true)
    enable_host_encryption   = optional(bool, false)
    enable_node_public_ip    = optional(bool, false)
    vnet_subnet_id           = string
    availability_zones       = optional(list(string), ["1", "2", "3"])
    node_labels              = optional(map(string), {})
    node_taints              = optional(list(string), [])
    tags                     = optional(map(string), {})
  }))
  default = {}
}

#----------------------------------------
# Common Tags
#----------------------------------------
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

locals {
  # Computed common tags
  common_tags = merge(
    {
      project             = var.project
      environment         = var.environment
      managed_by          = "terraform"
      terraform_workspace = terraform.workspace
      created_date        = timestamp()
    },
    var.tags
  )

  # Resource naming convention
  name_prefix = "${var.project}-${var.environment}"
}
```

---

## Outputs Reference

### outputs.tf (Complete)

```hcl
#----------------------------------------
# Resource Group Outputs
#----------------------------------------
output "resource_group_id" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.main.id
}

output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource Group location"
  value       = azurerm_resource_group.main.location
}

#----------------------------------------
# Network Outputs
#----------------------------------------
output "vnet_id" {
  description = "Virtual Network ID"
  value       = module.vnet.vnet_id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = module.vnet.vnet_name
}

output "subnet_ids" {
  description = "Map of subnet names to IDs"
  value       = module.vnet.subnet_ids
}

#----------------------------------------
# AKS Outputs
#----------------------------------------
output "aks_cluster_id" {
  description = "AKS Cluster ID"
  value       = module.aks.aks_id
}

output "aks_cluster_name" {
  description = "AKS Cluster name"
  value       = module.aks.aks_name
}

output "aks_cluster_fqdn" {
  description = "AKS Cluster FQDN"
  value       = module.aks.cluster_fqdn
}

output "aks_kube_config" {
  description = "AKS kubeconfig (raw)"
  value       = module.aks.kube_config_raw
  sensitive   = true
}

output "aks_oidc_issuer_url" {
  description = "OIDC Issuer URL for workload identity"
  value       = module.aks.oidc_issuer_url
}

output "aks_node_resource_group" {
  description = "AKS node resource group"
  value       = module.aks.node_resource_group
}

output "aks_kubelet_identity" {
  description = "Kubelet identity object ID"
  value       = module.aks.kubelet_identity[0].object_id
}

#----------------------------------------
# Key Vault Outputs
#----------------------------------------
output "key_vault_id" {
  description = "Key Vault ID"
  value       = module.keyvault.key_vault_id
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = module.keyvault.key_vault_uri
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = module.keyvault.key_vault_name
}

#----------------------------------------
# ACR Outputs
#----------------------------------------
output "acr_id" {
  description = "ACR ID"
  value       = module.acr.acr_id
}

output "acr_login_server" {
  description = "ACR login server"
  value       = module.acr.login_server
}

output "acr_admin_username" {
  description = "ACR admin username"
  value       = module.acr.admin_username
  sensitive   = true
}
```

---

## Data Sources

```hcl
# Current Azure context
data "azurerm_client_config" "current" {}

data "azurerm_subscription" "current" {}

# Reference existing resources
data "azurerm_resource_group" "existing" {
  name = var.existing_resource_group_name
}

data "azurerm_virtual_network" "existing" {
  name                = var.existing_vnet_name
  resource_group_name = data.azurerm_resource_group.existing.name
}

data "azurerm_subnet" "existing" {
  name                 = var.existing_subnet_name
  virtual_network_name = data.azurerm_virtual_network.existing.name
  resource_group_name  = data.azurerm_resource_group.existing.name
}

# Get AKS versions
data "azurerm_kubernetes_service_versions" "current" {
  location        = var.location
  include_preview = false
}
```

---

## Terraform Commands Reference

### Basic Workflow

```bash
# Initialize (download providers and modules)
terraform init
terraform init -upgrade  # Upgrade providers to latest allowed versions
terraform init -reconfigure  # Reconfigure backend

# Format and validate
terraform fmt -recursive
terraform validate

# Plan
terraform plan
terraform plan -out=tfplan                    # Save plan to file
terraform plan -var-file=prod.tfvars          # Use specific variables file
terraform plan -target=module.aks             # Plan specific resource
terraform plan -destroy                       # Plan destruction

# Apply
terraform apply
terraform apply tfplan                        # Apply saved plan
terraform apply -auto-approve                 # Skip approval (CI/CD)
terraform apply -var-file=prod.tfvars
terraform apply -parallelism=10               # Increase parallelism

# Destroy
terraform destroy
terraform destroy -target=module.aks          # Destroy specific resource
terraform destroy -auto-approve
```

### State Management

```bash
# List resources in state
terraform state list
terraform state list module.aks

# Show specific resource
terraform state show module.aks.azurerm_kubernetes_cluster.main

# Move resource (rename)
terraform state mv module.old_name module.new_name

# Remove from state (without destroying)
terraform state rm module.aks.azurerm_kubernetes_cluster.main

# Import existing resource
terraform import module.rg.azurerm_resource_group.main /subscriptions/xxx/resourceGroups/my-rg

# Pull remote state
terraform state pull > terraform.tfstate.backup

# Push state (dangerous!)
terraform state push terraform.tfstate.backup

# Replace provider
terraform state replace-provider hashicorp/azurerm registry.terraform.io/hashicorp/azurerm
```

### Workspace Management

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new prod
terraform workspace new stg

# Select workspace
terraform workspace select prod

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete stg
```

### Output Commands

```bash
# Show all outputs
terraform output

# Show specific output
terraform output aks_cluster_name

# Get raw value (for scripting)
terraform output -raw aks_kube_config > ~/.kube/config

# JSON format
terraform output -json
```

### Debug and Troubleshoot

```bash
# Enable debug logging
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform.log

# Graph dependencies
terraform graph | dot -Tpng > graph.png

# Show providers
terraform providers

# Lock providers
terraform providers lock -platform=linux_amd64 -platform=darwin_amd64

# Force unlock state
terraform force-unlock LOCK_ID
```

---

## Remote State Configuration

### Azure Storage Backend (Production)

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stterraformstate"
    container_name       = "tfstate"
    key                  = "${var.project}/${var.environment}/terraform.tfstate"
    use_azuread_auth     = true
    subscription_id      = "xxx-xxx-xxx"
    tenant_id            = "xxx-xxx-xxx"
  }
}
```

### Create State Storage

```bash
#!/bin/bash
RG_NAME="rg-terraform-state"
SA_NAME="stterraformstate$(openssl rand -hex 4)"
LOCATION="westeurope"
CONTAINER_NAME="tfstate"

# Create resource group
az group create --name $RG_NAME --location $LOCATION

# Create storage account
az storage account create \
  --name $SA_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --sku Standard_GRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false

# Create container
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $SA_NAME

# Enable versioning
az storage account blob-service-properties update \
  --account-name $SA_NAME \
  --resource-group $RG_NAME \
  --enable-versioning true

# Lock storage account
az lock create \
  --name "TerraformStateLock" \
  --lock-type CanNotDelete \
  --resource-group $RG_NAME \
  --resource-name $SA_NAME \
  --resource-type Microsoft.Storage/storageAccounts
```

---

## Best Practices

### Code Organization

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── stg/
│   └── prod/
├── modules/            # Local modules or git submodule
│   └── -> github.com/OktaySavdi/Azure/Modules
├── shared/
│   ├── versions.tf     # Shared provider versions
│   └── data.tf         # Shared data sources
└── README.md
```

### Production Checklist

- [ ] Remote state with locking enabled
- [ ] State encryption at rest
- [ ] Provider versions pinned
- [ ] Terraform version pinned
- [ ] Variables validated with `validation` blocks
- [ ] Sensitive outputs marked `sensitive = true`
- [ ] Resources tagged consistently
- [ ] Lifecycle rules defined where needed
- [ ] Import blocks for existing resources
- [ ] Moved blocks for refactoring
- [ ] Pre-commit hooks for fmt/validate
- [ ] CI/CD pipeline with plan review

### Naming Conventions

| Resource | Pattern | Example |
|----------|---------|--------|
| Resource Group | `rg-{project}-{env}` | `rg-myapp-prod` |
| Virtual Network | `vnet-{project}-{env}` | `vnet-myapp-prod` |
| Subnet | `snet-{purpose}` | `snet-aks`, `snet-db` |
| AKS Cluster | `aks-{project}-{env}` | `aks-myapp-prod` |
| Key Vault | `kv-{project}-{env}` | `kv-myapp-prod` |
| Storage Account | `st{project}{env}` | `stmyappprod` |
| ACR | `acr{project}{env}` | `acrmyappprod` |
