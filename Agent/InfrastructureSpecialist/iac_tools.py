#!/usr/bin/env python3
"""
Infrastructure Tools Module
============================
Provides tools for Terraform, Ansible, AWS, Azure, and file operations.
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
import shlex


class InfrastructureTools:
    """Collection of infrastructure automation tools"""
    
    def __init__(self):
        """Initialize tools with safety checks"""
        self._check_prerequisites()
    
    def _check_prerequisites(self):
        """Check if required tools are installed"""
        tools = {
            "terraform": "Terraform",
            "ansible": "Ansible",
            "aws": "AWS CLI",
            "az": "Azure CLI"
        }
        
        self.available_tools = {}
        for cmd, name in tools.items():
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self.available_tools[cmd] = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.available_tools[cmd] = False
                print(f"⚠️  Warning: {name} not found. Some operations will be unavailable.")
    
    def _execute_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: int = 300,
        env: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute shell command safely
        
        Args:
            command: Command to execute
            working_dir: Working directory
            timeout: Command timeout in seconds
            env: Environment variables
            
        Returns:
            Dict with execution results
        """
        try:
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Create working directory if it doesn't exist
            if working_dir:
                Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=exec_env
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "return_code": -1,
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "return_code": -1,
                "command": command
            }
    
    # ==================== TERRAFORM OPERATIONS ====================
    
    def terraform_operations(
        self,
        operation: str,
        working_dir: str,
        terraform_file_content: Optional[str] = None,
        var_file: Optional[str] = None,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """Execute Terraform operations"""
        
        if not self.available_tools.get("terraform"):
            return {
                "success": False,
                "error": "Terraform is not installed or not found in PATH"
            }
        
        # Create working directory
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        
        # Write Terraform file if content provided
        if terraform_file_content:
            main_tf = Path(working_dir) / "main.tf"
            main_tf.write_text(terraform_file_content)
        
        # Build command based on operation
        commands = {
            "init": "terraform init",
            "validate": "terraform validate",
            "fmt": "terraform fmt",
            "plan": f"terraform plan{' -var-file=' + var_file if var_file else ''}",
            "apply": f"terraform apply{' -auto-approve' if auto_approve else ''}{' -var-file=' + var_file if var_file else ''}",
            "destroy": f"terraform destroy{' -auto-approve' if auto_approve else ''}{' -var-file=' + var_file if var_file else ''}",
            "output": "terraform output -json",
            "show": "terraform show -json"
        }
        
        if operation not in commands:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Valid operations: {', '.join(commands.keys())}"
            }
        
        command = commands[operation]
        result = self._execute_command(command, working_dir=working_dir, timeout=600)
        
        return {
            "operation": operation,
            "working_dir": working_dir,
            **result
        }
    
    # ==================== ANSIBLE OPERATIONS ====================
    
    def ansible_operations(
        self,
        operation_type: str,
        playbook_path: Optional[str] = None,
        inventory: str = "localhost,",
        module: Optional[str] = None,
        args: Optional[str] = None,
        extra_vars: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute Ansible operations"""
        
        if not self.available_tools.get("ansible"):
            return {
                "success": False,
                "error": "Ansible is not installed or not found in PATH"
            }
        
        if operation_type == "playbook":
            if not playbook_path:
                return {
                    "success": False,
                    "error": "playbook_path is required for playbook operation"
                }
            
            command = f"ansible-playbook -i {inventory} {playbook_path}"
            
            if extra_vars:
                vars_str = json.dumps(extra_vars)
                command += f" --extra-vars '{vars_str}'"
        
        elif operation_type == "adhoc":
            if not module:
                return {
                    "success": False,
                    "error": "module is required for adhoc operation"
                }
            
            command = f"ansible {inventory} -m {module}"
            
            if args:
                command += f" -a '{args}'"
            
            if extra_vars:
                vars_str = json.dumps(extra_vars)
                command += f" --extra-vars '{vars_str}'"
        else:
            return {
                "success": False,
                "error": f"Unknown operation_type: {operation_type}. Use 'playbook' or 'adhoc'"
            }
        
        result = self._execute_command(command, timeout=600)
        
        return {
            "operation_type": operation_type,
            **result
        }
    
    # ==================== AWS OPERATIONS ====================
    
    def aws_operations(
        self,
        service: str,
        operation: str,
        parameters: Optional[Dict] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute AWS CLI operations"""
        
        if not self.available_tools.get("aws"):
            return {
                "success": False,
                "error": "AWS CLI is not installed or not found in PATH"
            }
        
        # Build AWS command
        command = f"aws {service} {operation}"
        
        # Add parameters
        if parameters:
            for key, value in parameters.items():
                if isinstance(value, bool):
                    if value:
                        command += f" --{key}"
                elif isinstance(value, (list, dict)):
                    command += f" --{key} '{json.dumps(value)}'"
                else:
                    command += f" --{key} {shlex.quote(str(value))}"
        
        # Add region
        if region:
            command += f" --region {region}"
        
        # Add profile
        if profile:
            command += f" --profile {profile}"
        
        # Output as JSON for parsing
        command += " --output json"
        
        result = self._execute_command(command, timeout=300)
        
        # Try to parse JSON output
        if result["success"] and result["stdout"]:
            try:
                result["parsed_output"] = json.loads(result["stdout"])
            except json.JSONDecodeError:
                pass
        
        return {
            "service": service,
            "operation": operation,
            **result
        }
    
    # ==================== AZURE OPERATIONS ====================
    
    def azure_operations(
        self,
        service: str,
        operation: str,
        parameters: Optional[Dict] = None,
        resource_group: Optional[str] = None,
        subscription: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute Azure CLI operations"""
        
        if not self.available_tools.get("az"):
            return {
                "success": False,
                "error": "Azure CLI is not installed or not found in PATH"
            }
        
        # Build Azure command
        command = f"az {service} {operation}"
        
        # Add resource group
        if resource_group:
            command += f" --resource-group {resource_group}"
        
        # Add subscription
        if subscription:
            command += f" --subscription {subscription}"
        
        # Add parameters
        if parameters:
            for key, value in parameters.items():
                if isinstance(value, bool):
                    if value:
                        command += f" --{key}"
                elif isinstance(value, (list, dict)):
                    command += f" --{key} '{json.dumps(value)}'"
                else:
                    command += f" --{key} {shlex.quote(str(value))}"
        
        # Output as JSON
        command += " --output json"
        
        result = self._execute_command(command, timeout=300)
        
        # Try to parse JSON output
        if result["success"] and result["stdout"]:
            try:
                result["parsed_output"] = json.loads(result["stdout"])
            except json.JSONDecodeError:
                pass
        
        return {
            "service": service,
            "operation": operation,
            **result
        }
    
    # ==================== FILE OPERATIONS ====================
    
    def file_operations(
        self,
        operation: str,
        file_path: str,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform file operations"""
        
        try:
            path = Path(file_path)
            
            if operation == "read":
                if not path.exists():
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
                content = path.read_text()
                return {
                    "success": True,
                    "operation": "read",
                    "file_path": file_path,
                    "content": content
                }
            
            elif operation == "write":
                if content is None:
                    return {
                        "success": False,
                        "error": "content is required for write operation"
                    }
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return {
                    "success": True,
                    "operation": "write",
                    "file_path": file_path,
                    "message": f"File written successfully: {file_path}"
                }
            
            elif operation == "append":
                if content is None:
                    return {
                        "success": False,
                        "error": "content is required for append operation"
                    }
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'a') as f:
                    f.write(content)
                return {
                    "success": True,
                    "operation": "append",
                    "file_path": file_path,
                    "message": f"Content appended to file: {file_path}"
                }
            
            elif operation == "delete":
                if path.exists():
                    path.unlink()
                    return {
                        "success": True,
                        "operation": "delete",
                        "file_path": file_path,
                        "message": f"File deleted: {file_path}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
            
            elif operation == "exists":
                return {
                    "success": True,
                    "operation": "exists",
                    "file_path": file_path,
                    "exists": path.exists()
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"File operation failed: {str(e)}"
            }
    
    # ==================== CODE VALIDATION ====================
    
    def validate_code(
        self,
        code_type: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Validate IaC code"""
        
        if code_type == "terraform":
            if not self.available_tools.get("terraform"):
                return {
                    "success": False,
                    "error": "Terraform is not installed"
                }
            
            # Run terraform fmt to check formatting
            fmt_result = self._execute_command(
                "terraform fmt -check -diff",
                working_dir=file_path if Path(file_path).is_dir() else str(Path(file_path).parent)
            )
            
            # Run terraform validate
            validate_result = self._execute_command(
                "terraform validate",
                working_dir=file_path if Path(file_path).is_dir() else str(Path(file_path).parent)
            )
            
            return {
                "code_type": "terraform",
                "file_path": file_path,
                "formatting": {
                    "success": fmt_result["success"],
                    "output": fmt_result["stdout"],
                    "errors": fmt_result["stderr"]
                },
                "validation": {
                    "success": validate_result["success"],
                    "output": validate_result["stdout"],
                    "errors": validate_result["stderr"]
                },
                "overall_success": fmt_result["success"] and validate_result["success"]
            }
        
        elif code_type == "ansible":
            if not self.available_tools.get("ansible"):
                return {
                    "success": False,
                    "error": "Ansible is not installed"
                }
            
            # Run ansible-playbook syntax check
            result = self._execute_command(
                f"ansible-playbook --syntax-check {file_path}"
            )
            
            return {
                "code_type": "ansible",
                "file_path": file_path,
                "success": result["success"],
                "output": result["stdout"],
                "errors": result["stderr"]
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown code_type: {code_type}. Use 'terraform' or 'ansible'"
            }
