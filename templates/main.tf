#--------------------------------------------------------------------------------------------------------
# service plan
#--------------------------------------------------------------------------------------------------------
resource "azurerm_service_plan" "service_plan" {
  name                = var.service_plan_name
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = var.os_type
  sku_name            = var.sku_name
  lifecycle {
    ignore_changes = [
      # Ignore changes to the 'tags' attribute
      tags,
    ]
  }
}

#--------------------------------------------------------------------------------------------------------
# linux function
#--------------------------------------------------------------------------------------------------------
resource "azurerm_linux_function_app" "linux_function_app" {
  count                      = var.os_type == "Linux" ? 1 : 0
  name                       = var.function_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.service_plan.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_primary_access_key
  public_network_access_enabled = false
  virtual_network_subnet_id  = var.subnet_name
  ftp_publish_basic_authentication_enabled = false
  
  dynamic "site_config" {
    for_each = var.site_config
    content {
      vnet_route_all_enabled            = true
      always_on                         = lookup(site_config.value, "always_on", null)
      api_definition_url                = lookup(site_config.value, "api_definition_url", null)
      api_management_api_id             = lookup(site_config.value, "api_management_api_id", null)
      app_command_line                  = lookup(site_config.value, "app_command_line", null)
      app_scale_limit                   = lookup(site_config.value, "app_scale_limit", null)
      default_documents                 = lookup(site_config.value, "default_documents", null)
      ftps_state                        = lookup(site_config.value, "ftps_state", "Disabled")
      health_check_path                 = lookup(site_config.value, "health_check_path", null)
      health_check_eviction_time_in_min = lookup(site_config.value, "health_check_eviction_time_in_min", null)
      http2_enabled                     = lookup(site_config.value, "http2_enabled", null)
      load_balancing_mode               = lookup(site_config.value, "load_balancing_mode", null)
      managed_pipeline_mode             = lookup(site_config.value, "managed_pipeline_mode", null)
      minimum_tls_version               = lookup(site_config.value, "minimum_tls_version", lookup(site_config.value, "min_tls_version", "1.2"))
      remote_debugging_enabled          = lookup(site_config.value, "remote_debugging_enabled", false)
      remote_debugging_version          = lookup(site_config.value, "remote_debugging_version", null)
      runtime_scale_monitoring_enabled  = lookup(site_config.value, "runtime_scale_monitoring_enabled", null)
      use_32_bit_worker                 = lookup(site_config.value, "use_32_bit_worker", null)
      websockets_enabled                = lookup(site_config.value, "websockets_enabled", false)

      application_insights_connection_string = lookup(site_config.value, "application_insights_connection_string", null)
      application_insights_key               = lookup(site_config.value, "application_insights_key", false)

      pre_warmed_instance_count = lookup(site_config.value, "pre_warmed_instance_count", null)
      elastic_instance_minimum  = lookup(site_config.value, "elastic_instance_minimum", null)
      worker_count              = lookup(site_config.value, "worker_count", null)

      # Replace the dynamic "ip_restriction" block with these static ip_restriction blocks
      ip_restriction {
        name        = "Allow Azure Monitor"
        service_tag = "AzureMonitor"
        priority    = 100
        action      = "Allow"
      }

      ip_restriction {
        name        = "Allow Action Group"
        service_tag = "ActionGroup"
        priority    = 110
        action      = "Allow"
      }

      ip_restriction {
        name                     = "Deny internet"
        ip_address               = "0.0.0.0/0"
        virtual_network_subnet_id = null
        priority                 = 120
        action                   = "Deny"
      }

      dynamic "application_stack" {
        for_each = lookup(site_config.value, "application_stack", null) == null ? [] : [site_config.value.application_stack]
        content {
          dotnet_version              = lookup(application_stack.value, "dotnet_version", null)
          java_version                = lookup(application_stack.value, "java_version", null)
          node_version                = lookup(application_stack.value, "node_version", null)
          python_version              = lookup(application_stack.value, "python_version", null)
          powershell_core_version     = lookup(application_stack.value, "powershell_core_version", null)
        }
      }

      # dynamic "application_stack" {
      #   for_each = lookup(site_config.value, "application_stack", null) == null ? [] : ["application_stack"]
      #   content {
      #     dynamic "docker" {
      #       for_each = lookup(site_config.value.application_stack, "docker", null) == null ? [] : ["docker"]
      #       content {
      #         registry_url      = docker.value.registry_url
      #         image_name        = docker.value.image_name
      #         image_tag         = docker.value.image_tag
      #         registry_username = docker.value.registry_username
      #         registry_password = docker.value.registry_password
      #       }
      #     }

      #     dotnet_version              = lookup(site_config.value.application_stack, "dotnet_version", null)
      #     use_dotnet_isolated_runtime = lookup(site_config.value.application_stack, "use_dotnet_isolated_runtime", null)
      #     java_version                = lookup(site_config.value.application_stack, "java_version", null)
      #     node_version                = lookup(site_config.value.application_stack, "node_version", null)
      #     python_version              = lookup(site_config.value.application_stack, "python_version", null)
      #     powershell_core_version     = lookup(site_config.value.application_stack, "powershell_core_version", null)
      #     use_custom_runtime          = lookup(site_config.value.application_stack, "use_custom_runtime", null)
      #   }
      # }
    }
  }
  
  lifecycle {
    ignore_changes = [
      sticky_settings,
      site_config,
      tags
    ]
  }
}

#--------------------------------------------------------------------------------------------------------
# Windows function
#--------------------------------------------------------------------------------------------------------
resource "azurerm_windows_function_app" "windows_function_app" {
  count                      = var.os_type == "Windows" ? 1 : 0
  name                       = var.function_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.service_plan.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_primary_access_key
  public_network_access_enabled = false
  virtual_network_subnet_id  = var.subnet_name
  ftp_publish_basic_authentication_enabled = false



  dynamic "site_config" {
    for_each = var.site_config
    content {
      vnet_route_all_enabled            = true
      always_on                         = lookup(site_config.value, "always_on", null)
      api_definition_url                = lookup(site_config.value, "api_definition_url", null)
      api_management_api_id             = lookup(site_config.value, "api_management_api_id", null)
      app_command_line                  = lookup(site_config.value, "app_command_line", null)
      app_scale_limit                   = lookup(site_config.value, "app_scale_limit", null)
      default_documents                 = lookup(site_config.value, "default_documents", null)
      ftps_state                        = lookup(site_config.value, "ftps_state", "Disabled")
      health_check_path                 = lookup(site_config.value, "health_check_path", null)
      health_check_eviction_time_in_min = lookup(site_config.value, "health_check_eviction_time_in_min", null)
      http2_enabled                     = lookup(site_config.value, "http2_enabled", null)
      load_balancing_mode               = lookup(site_config.value, "load_balancing_mode", null)
      managed_pipeline_mode             = lookup(site_config.value, "managed_pipeline_mode", null)
      minimum_tls_version               = lookup(site_config.value, "minimum_tls_version", lookup(site_config.value, "min_tls_version", "1.2"))
      remote_debugging_enabled          = lookup(site_config.value, "remote_debugging_enabled", false)
      remote_debugging_version          = lookup(site_config.value, "remote_debugging_version", null)
      runtime_scale_monitoring_enabled  = lookup(site_config.value, "runtime_scale_monitoring_enabled", null)
      use_32_bit_worker                 = lookup(site_config.value, "use_32_bit_worker", null)
      websockets_enabled                = lookup(site_config.value, "websockets_enabled", false)

      application_insights_connection_string = lookup(site_config.value, "application_insights_connection_string", null)
      application_insights_key               = lookup(site_config.value, "application_insights_key", false)

      pre_warmed_instance_count = lookup(site_config.value, "pre_warmed_instance_count", null)
      elastic_instance_minimum  = lookup(site_config.value, "elastic_instance_minimum", null)
      worker_count              = lookup(site_config.value, "worker_count", null)

      # Replace the dynamic "ip_restriction" block with these static ip_restriction blocks
      ip_restriction {
        name        = "Allow Azure Monitor"
        service_tag = "AzureMonitor"
        priority    = 100
        action      = "Allow"
      }

      ip_restriction {
        name        = "Allow Action Group"
        service_tag = "ActionGroup"
        priority    = 110
        action      = "Allow"
      }

      ip_restriction {
        name                     = "Deny internet"
        ip_address               = "0.0.0.0/0"
        virtual_network_subnet_id = null
        priority                 = 120
        action                   = "Deny"
      }

      dynamic "application_stack" {
        for_each = lookup(site_config.value, "application_stack", null) == null ? [] : [site_config.value.application_stack]
        content {
          dotnet_version              = lookup(application_stack.value, "dotnet_version", null)
          java_version                = lookup(application_stack.value, "java_version", null)
          node_version                = lookup(application_stack.value, "node_version", null)
          powershell_core_version     = lookup(application_stack.value, "powershell_core_version", null)
        }
      }

      // dynamic "application_stack" {
      //   for_each = lookup(site_config.value, "application_stack", null) == null ? [] : ["application_stack"]
      //   content {
      //     dotnet_version              = lookup(site_config.application_stack, "dotnet_version", null)
      //     use_dotnet_isolated_runtime = lookup(site_config.application_stack, "use_dotnet_isolated_runtime", null)

      //     java_version            = lookup(site_config.application_stack, "java_version", null)
      //     node_version            = lookup(site_config.application_stack, "node_version", null)
      //     powershell_core_version = lookup(site_config.application_stack, "powershell_core_version", null)

      //     use_custom_runtime = lookup(site_config.application_stack, "use_custom_runtime", null)
      //   }
      // }
    }
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to the 'tags' attribute
      tags,
    ]
  }
}

#--------------------------------------------------------------------------------------------------------
# private endpoint and DNS configuration
#--------------------------------------------------------------------------------------------------------
resource "azurerm_private_endpoint" "function_app_private_endpoint" {
  name                = var.pe_name
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.pe_subnet

  private_service_connection {
    name                           = "${var.function_name}-privateserviceconnection"
    is_manual_connection           = false
    private_connection_resource_id = var.os_type == "Linux" ? azurerm_linux_function_app.linux_function_app[0].id : azurerm_windows_function_app.windows_function_app[0].id
    subresource_names              = ["sites"]
  }

  private_dns_zone_group {
    name                 = "privatelink.azurewebsites.net"
    private_dns_zone_ids = ["/subscriptions/<subscription_id>/resourceGroups/<rg_name>/providers/Microsoft.Network/privateDnsZones/privatelink.azurewebsites.net"]
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}
