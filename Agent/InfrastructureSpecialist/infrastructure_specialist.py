#!/usr/bin/env python3
"""
Infrastructure Specialist AI Agent with LangFuse Integration
Uses LangFuse SDK with manual trace/span creation for reliable observability
"""

import os
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import requests
from iac_tools import InfrastructureTools

# Load environment variables
load_dotenv()

# LangFuse integration - Using official decorator pattern
try:
    from langfuse import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    # Create no-op decorator when LangFuse is not available
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])
    
    LANGFUSE_AVAILABLE = False
    print("⚠️  LangFuse not available. Install with: pip install 'langfuse>=3.0.0'")


class InfrastructureSpecialist:
    """Infrastructure Specialist AI Agent with LangFuse observability"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Infrastructure Specialist agent"""
        self.config = self._load_config(config_path)
        self.tools = InfrastructureTools()
        self.conversation_history = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file and environment"""
        config = {
            "name": "InfrastructureSpecialist",
            "llm_config": {
                "base_url": "http://20.10.192.136:11434/v1",
                "model": "qwen2.5-coder:32b",
                "api_key": "ollama",
                "temperature": 0.7,
                "timeout": 600
            },
            "work_dir": "./iac_workspace"
        }
        
        if Path(config_path).exists():
            with open(config_path) as f:
                file_config = json.load(f)
                config.update(file_config)
        
        # Override with environment variables
        env_overrides = {
            "llm_config": {
                "base_url": os.getenv("OLLAMA_BASE_URL"),
                "model": os.getenv("OLLAMA_MODEL"),
                "api_key": os.getenv("OLLAMA_API_KEY"),
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
                "timeout": int(os.getenv("OLLAMA_TIMEOUT", "600"))
            },
            "name": os.getenv("AGENT_NAME"),
            "work_dir": os.getenv("AGENT_WORK_DIR")
        }
        
        for key, value in env_overrides.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_value is not None:
                        config[key][sub_key] = sub_value
            elif value is not None:
                config[key] = value
        
        return config
    
    @observe(as_type="generation", name="ollama_generation")
    def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM via OpenAI-compatible API"""
        start_time = time.time()
        base_url = self.config["llm_config"]["base_url"]
        api_url = base_url.replace("/v1", "") + "/api/generate"
        
        payload = {
            "model": self.config["llm_config"]["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config["llm_config"]["temperature"]
            }
        }
        
        try:
            response = requests.post(
                api_url,
                json=payload,
                timeout=self.config["llm_config"]["timeout"]
            )
            response.raise_for_status()
            result_json = response.json()
            result = result_json.get("response", "No response")
            
            return result
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            return error_msg
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with role and tools"""
        tools_description = """
**Available Tools:**

1. **terraform_operations**
   - Manage Terraform infrastructure
   - Parameters: operation (init/plan/apply/destroy/validate/fmt), working_dir, terraform_file_content (optional), var_file (optional), auto_approve (bool)
   - Example: {{"operation": "plan", "working_dir": "./terraform"}}

2. **ansible_operations**
   - Run Ansible playbooks or ad-hoc commands
   - Parameters: operation_type (playbook/adhoc), playbook_path OR adhoc_module, inventory, extra_vars
   - Example: {{"operation_type": "playbook", "playbook_path": "deploy.yml"}}

3. **aws_operations**
   - Execute AWS CLI commands
   - Parameters: service, action, parameters (dict)
   - Example: {{"service": "ec2", "action": "describe-instances", "parameters": {{"region": "us-east-1"}}}}

4. **azure_operations**
   - Execute Azure CLI commands
   - Parameters: service, action, resource_group, additional_params
   - Example: {{"service": "vm", "action": "list", "resource_group": "my-rg"}}

5. **file_operations**
   - File management (read/write/delete)
   - Parameters: operation (read/write/append/delete/exists), file_path, content (for write/append)
   - Example: {{"operation": "write", "file_path": "./config.tf", "content": "..."}}

6. **validate_code**
   - Validate Terraform or Ansible code
   - Parameters: code_type (terraform/ansible), file_path
   - Example: {{"code_type": "terraform", "file_path": "./main.tf"}}
"""
        
        return f"""You are the **Infrastructure Specialist**, an expert in Infrastructure as Code (IaC).

**Your Role:**
- Analyze infrastructure requirements and design solutions
- Write and manage Terraform configurations
- Create and execute Ansible playbooks
- Manage AWS and Azure resources
- Validate infrastructure code
- Follow best practices for cloud infrastructure

{tools_description}

**Response Format:**
- For tool usage: Respond with ONLY ONE JSON object per response: {{"tool": "tool_name", "parameters": {{...}}}}
- Execute ONE tool at a time - I will call you again with the result
- For explanations only (no tools needed): Respond in natural language
- Keep responses concise and focused

**CRITICAL: Production-Ready Standards**
All infrastructure code MUST be comprehensive and production-ready:

1. **Security First:**
   - Enable encryption at rest and in transit
   - Implement least privilege access (IAM roles, RBAC)
   - Use private endpoints where applicable
   - Configure network security groups/firewalls
   - Enable audit logging and compliance features

2. **High Availability & Reliability:**
   - Multi-zone/region deployment where applicable
   - Configure health checks and monitoring
   - Implement auto-scaling capabilities
   - Set up backup and disaster recovery
   - Define appropriate retention policies

3. **Resource Configuration:**
   - Use variables for all configurable parameters
   - Include comprehensive tagging strategy (Environment, Owner, CostCenter, Project, ManagedBy)
   - Set resource locks where appropriate
   - Configure lifecycle policies
   - Define outputs for important resource attributes

4. **Monitoring & Observability:**
   - Enable diagnostic settings and logging
   - Configure alerts and notifications
   - Set up metrics collection
   - Implement distributed tracing where applicable

5. **Documentation:**
   - Add detailed comments explaining resource purpose
   - Document dependencies and prerequisites
   - Include usage examples in README
   - Specify required provider versions

6. **Cost Optimization:**
   - Use appropriate SKUs/instance types for workload
   - Implement resource scheduling where applicable
   - Configure auto-shutdown for non-production
   - Use reserved instances/savings plans recommendations

**Never create simple, minimal configurations. Always deliver enterprise-grade, production-ready infrastructure!**
"""
    
    @observe(as_type="span")
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool_map = {
            "terraform_operations": self.tools.terraform_operations,
            "ansible_operations": self.tools.ansible_operations,
            "aws_operations": self.tools.aws_operations,
            "azure_operations": self.tools.azure_operations,
            "file_operations": self.tools.file_operations,
            "validate_code": self.tools.validate_code
        }
        
        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = tool_map[tool_name](**parameters)
            return result
        except Exception as e:
            error_result = {"error": f"Error executing {tool_name}: {str(e)}"}
            return error_result
    
    @observe(name="infrastructure_task")
    def execute_task(self, task: str, context: Optional[Dict] = None, max_iterations: int = 5) -> str:
        """
        Execute an infrastructure task with LangFuse tracing via decorator
        
        Args:
            task: Task description
            context: Additional context
            max_iterations: Maximum number of LLM calls
            
        Returns:
            Task result or error message
        """
        print(f"📋 Task: {task}\n")
        
        # Build initial prompt
        prompt = f"""{self._build_system_prompt()}

**User Request**: {task}

**Context**: {json.dumps(context or {}, indent=2)}

**Instructions**:
1. If you need to use a tool, respond with ONLY the JSON tool call (no extra text)
2. If you have information to share (no tools needed), respond normally
3. Execute ONE tool at a time - you'll be called again with results

Your response:"""

        self.conversation_history = [{"role": "system", "content": prompt}]
        
        result = self._execute_task_loop(max_iterations)
        
        return result
    
    def _execute_task_loop(self, max_iterations: int) -> str:
        """Internal method to execute the task iteration loop"""
        for iteration in range(max_iterations):
            print(f"\n🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Get LLM response (tracked via SDK)
            full_prompt = "\n\n".join([msg["content"] for msg in self.conversation_history])
            response = self._call_llm(full_prompt)
            
            print(f"\n🤖 Agent Response:\n{response}\n")
            
            # Check if response contains a tool call
            tool_executed = False
            try:
                if "{" in response and "}" in response:
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    json_str = response[json_start:json_end].strip()
                    
                    tool_call = json.loads(json_str)
                    
                    if "tool" in tool_call and "parameters" in tool_call:
                        print(f"🔧 Executing tool: {tool_call['tool']}")
                        print(f"📝 Parameters: {json.dumps(tool_call['parameters'], indent=2)}\n")
                        
                        # Execute tool (tracked via SDK)
                        tool_result = self._execute_tool(tool_call["tool"], tool_call["parameters"])
                        
                        print(f"✅ Tool Result:\n{json.dumps(tool_result, indent=2)}\n")
                        
                        # Add to conversation
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": response
                        })
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"Tool execution result: {json.dumps(tool_result, indent=2)}\n\nContinue with next step or provide final summary."
                        })
                        tool_executed = True
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️  Could not parse tool call: {e}")
            
            # If tool was executed, continue to next iteration
            if tool_executed:
                continue
            
            # No tool call, return the response
            return response
        
        # Max iterations reached
        result = "Max iterations reached. Task may be incomplete."
        return result
    
    def interactive_mode(self):
        """Run agent in interactive mode"""
        print("=" * 60)
        print("🏗️  Infrastructure Specialist Agent")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  - Type your infrastructure task")
        print("  - 'quit' or 'exit' to stop")
        print("  - 'help' for tool information")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print(self._build_system_prompt())
                    continue
                
                if not user_input:
                    continue
                
                # Execute task (automatically traced)
                response = self.execute_task(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Infrastructure Specialist AI Agent')
    parser.add_argument('--mode', choices=['interactive', 'task'], default='interactive',
                        help='Run mode: interactive or task')
    parser.add_argument('--task', type=str, help='Task to execute (for task mode)')
    parser.add_argument('task_text', nargs='*', help='Task description (alternative to --task)')
    
    args = parser.parse_args()
    
    agent = InfrastructureSpecialist()
    
    # Determine task
    task = None
    if args.task:
        task = args.task
    elif args.task_text:
        task = " ".join(args.task_text)
    
    # Run in appropriate mode
    if args.mode == 'task' or task:
        if not task:
            print("❌ Error: Task mode requires a task. Use --task 'your task' or provide task text")
            sys.exit(1)
        agent.execute_task(task)
    else:
        agent.interactive_mode()
    
    # LangFuse decorators handle flushing automatically
    if LANGFUSE_AVAILABLE and os.getenv("LANGFUSE_ENABLED", "false").lower() == "true":
        print("\n📤 Flushing traces to LangFuse...")
        print("✅ Traces sent to LangFuse dashboard")
        print(f"🔗 View traces at: {os.getenv('LANGFUSE_HOST', 'http://localhost:3000')}/traces")


if __name__ == "__main__":
    main()
