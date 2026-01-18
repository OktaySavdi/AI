# Terraform Basics

**Terraform** is an Infrastructure as Code (IaC) tool by HashiCorp for provisioning and managing cloud resources.

## Core Concepts

### 1. Providers
Plugins that interact with cloud platforms.

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

### 2. Resources
Infrastructure components to create.

```hcl
resource "azurerm_resource_group" "example" {
  name     = "my-resource-group"
  location = "West Europe"
  
  tags = {
    environment = "production"
    team        = "platform"
  }
}
```

### 3. Variables
Input parameters for configurations.

```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 2
}

variable "allowed_ips" {
  description = "List of allowed IPs"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}
```

### 4. Outputs
Values to export from your configuration.

```hcl
# outputs.tf
output "resource_group_id" {
  description = "The ID of the resource group"
  value       = azurerm_resource_group.example.id
}

output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.example.name
}
```

## Terraform Commands

```bash
# Initialize working directory
terraform init

# Format configuration files
terraform fmt

# Validate configuration
terraform validate

# Show execution plan
terraform plan

# Apply changes
terraform apply

# Apply with auto-approve (CI/CD)
terraform apply -auto-approve

# Destroy infrastructure
terraform destroy

# Show current state
terraform show

# List resources in state
terraform state list

# Import existing resource
terraform import azurerm_resource_group.example /subscriptions/.../resourceGroups/my-rg
```

## State Management

### Local State
```hcl
# Default - terraform.tfstate file
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

### Remote State (Azure)
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

## Best Practices

1. **Use remote state** for team collaboration
2. **Enable state locking** to prevent conflicts
3. **Use variables** for reusable configurations
4. **Organize with modules** for complex infrastructure
5. **Use workspaces** for multiple environments
6. **Version control** your Terraform code
7. **Use .tfvars files** for environment-specific values
