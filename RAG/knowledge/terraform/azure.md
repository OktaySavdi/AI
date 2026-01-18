# Terraform Azure Resources

Complete examples for deploying Azure resources with Terraform.

## Resource Group

```hcl
resource "azurerm_resource_group" "example" {
  name     = "rg-${var.project}-${var.environment}"
  location = var.location
  
  tags = var.tags
}
```

## Virtual Network

```hcl
resource "azurerm_virtual_network" "example" {
  name                = "vnet-${var.project}-${var.environment}"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  address_space       = ["10.0.0.0/16"]
  
  tags = var.tags
}

resource "azurerm_subnet" "example" {
  name                 = "subnet-app"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

## Azure Kubernetes Service (AKS)

```hcl
resource "azurerm_kubernetes_cluster" "example" {
  name                = "aks-${var.project}-${var.environment}"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "${var.project}-${var.environment}"
  kubernetes_version  = "1.28"

  default_node_pool {
    name                = "system"
    node_count          = 3
    vm_size             = "Standard_D4s_v3"
    vnet_subnet_id      = azurerm_subnet.aks.id
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
    
    node_labels = {
      "nodepool" = "system"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    service_cidr      = "10.100.0.0/16"
    dns_service_ip    = "10.100.0.10"
  }

  tags = var.tags
}

# Additional node pool
resource "azurerm_kubernetes_cluster_node_pool" "workload" {
  name                  = "workload"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_D8s_v3"
  node_count            = 2
  enable_auto_scaling   = true
  min_count             = 1
  max_count             = 10
  vnet_subnet_id        = azurerm_subnet.aks.id
  
  node_labels = {
    "nodepool" = "workload"
  }
  
  node_taints = [
    "workload=true:NoSchedule"
  ]
  
  tags = var.tags
}
```

## Azure Container Registry (ACR)

```hcl
resource "azurerm_container_registry" "example" {
  name                = "acr${var.project}${var.environment}"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "Premium"
  admin_enabled       = false

  georeplications {
    location                = "North Europe"
    zone_redundancy_enabled = true
    tags                    = var.tags
  }

  tags = var.tags
}

# Attach ACR to AKS
resource "azurerm_role_assignment" "aks_acr" {
  principal_id                     = azurerm_kubernetes_cluster.example.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.example.id
  skip_service_principal_aad_check = true
}
```

## Storage Account

```hcl
resource "azurerm_storage_account" "example" {
  name                     = "st${var.project}${var.environment}"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 30
    }
    
    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}
```

## Key Vault

```hcl
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "example" {
  name                        = "kv-${var.project}-${var.environment}"
  location                    = azurerm_resource_group.example.location
  resource_group_name         = azurerm_resource_group.example.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 90
  purge_protection_enabled    = true
  enable_rbac_authorization   = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = var.allowed_ips
  }

  tags = var.tags
}
```

## Variables File

```hcl
# variables.tf
variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, stg, prod)"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "West Europe"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    managed_by = "terraform"
  }
}

variable "allowed_ips" {
  description = "Allowed IP addresses"
  type        = list(string)
  default     = []
}
```

## Outputs

```hcl
# outputs.tf
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.example.name
}

output "aks_kube_config" {
  value     = azurerm_kubernetes_cluster.example.kube_config_raw
  sensitive = true
}

output "acr_login_server" {
  value = azurerm_container_registry.example.login_server
}

output "key_vault_uri" {
  value = azurerm_key_vault.example.vault_uri
}
```
