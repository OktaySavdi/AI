# Infrastructure Specialist AI Agent 🤖

A lightweight AI agent specialized in Infrastructure as Code (IaC). Directly integrates with Ollama LLM to handle Terraform, Ansible, AWS CLI, Azure CLI, and multi-cloud infrastructure management.

## 🎯 Overview

**Agent Role**: Infrastructure Specialist - "The Builder"  
**Model**: qwen2.5-coder:32b (via Ollama)  
**Framework**: Direct Ollama API Integration (No AutoGen dependency)  
**Monitoring**: LangFuse v3.x with @observe decorators (optional)  
**Ollama Endpoint**: http://20.10.192.136:11434  
**LangFuse SDK**: v3.11.2+ (compatible with server 3.144.0+)  
**Python Version**: Python 3.13+ compatible

## ✨ Features

### Core Capabilities
- 🏗️ **Terraform Operations**: init, plan, apply, destroy, validate
- ⚙️ **Ansible Automation**: Playbooks and ad-hoc commands
- ☁️ **AWS Operations**: EC2, S3, EKS, VPC management
- 🔷 **Azure Operations**: VM, AKS, networking, storage
- 📁 **File Operations**: Read, write, manage IaC files
- ✅ **Code Validation**: Syntax checking and linting

### Supported Use Cases
- Infrastructure provisioning and management
- Multi-cloud deployments (AWS, Azure, GCP)
- Kubernetes cluster creation (AKS, EKS)
- Configuration management with Ansible
- Infrastructure code review and optimization
- Automated infrastructure workflows

## 📋 Prerequisites

### Required Tools
Install these tools on your system:

```bash
# Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# Ansible
pip install ansible
# or
brew install ansible  # macOS

# AWS CLI
brew install awscli  # macOS
# or
pip install awscli

# Azure CLI
brew install azure-cli  # macOS
# or
curl -L https://aka.ms/InstallAzureCli | bash
```

### Python Dependencies
Minimal dependencies - no heavy frameworks required!
```bash
pip install -r requirements.txt
# Installs: python-dotenv, requests, pyyaml, colorlog, rich
# Optional: langfuse>=3.0.0 (for monitoring)
```

### Ollama Setup
Ensure Ollama is running with the qwen2.5-coder:32b model:

```bash
# Check if model is available
curl http://20.10.192.136:11434/api/tags

# Pull the model if needed
curl http://20.10.192.136:11434/api/pull -d '{"name":"qwen2.5-coder:32b"}'
```

## 🚀 Installation

1. **Clone or navigate to the project**:
```bash
cd /Users/osavdi@greentube.com/Documents/Scripts/AI/Agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**:
Create or copy `.env` file:
```bash
# Copy the .env file (already exists in the directory)
cat .env

# Or configure from scratch
cp .env .env.local  # backup
```

**Required Configuration**:
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://20.10.192.136:11434/v1
OLLAMA_MODEL=qwen2.5-coder:32b

# LangFuse Monitoring (Optional)
LANGFUSE_ENABLED=false  # Set to true to enable monitoring
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_SECRET_KEY=your-secret-key
LANGFUSE_HOST=http://localhost:3000
```

4. **Setup LangFuse (Optional - for monitoring)**:
If you want to track agent performance, install LangFuse:

```bash
# Install LangFuse SDK v3.x (compatible with server 3.144.0+)
pip install 'langfuse>=3.0.0'

# Install LangFuse server on VM (see AI/LangFuse/README.md for full guide)
cd ../../LangFuse
./deploy.sh

# After deployment, get API keys from LangFuse dashboard:
# http://your-vm-ip:3000 -> Settings -> API Keys

# Add keys to .env file
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_HOST=http://your-vm-ip:3000
```

**LangFuse Integration Features**:
- ✅ Automatic trace creation with `@observe` decorators
- ✅ LLM call tracking (input, output, tokens, duration)
- ✅ Tool execution tracking (parameters, results, success/failure)
- ✅ Session management and user tracking
- ✅ Clean, maintainable code (3 decorators instead of 150+ lines)

5. **Make executable**:
```bash
chmod +x infrastructure_specialist.py
```

## 💻 Usage

### Interactive Mode (Recommended)

Start an interactive session with the agent:

```bash
python infrastructure_specialist.py --mode interactive
```

Example interactions:
```
🔧 You: Create a Terraform configuration for an AWS VPC with 2 subnets

🔧 You: Write an Ansible playbook to install Docker on Ubuntu servers

🔧 You: List all running EC2 instances in us-east-1

🔧 You: Create an AKS cluster in Azure with 3 nodes
```

### Single Task Mode

Execute a specific task:

```bash
python infrastructure_specialist.py --mode task --task "Create a Terraform module for an AWS S3 bucket with versioning enabled"
```

### Programmatic Usage

```python
from infrastructure_specialist import InfrastructureSpecialist

# Initialize agent
agent = InfrastructureSpecialist(config_path="config.json")

# Execute task
result = agent.execute_task(
    task="Create a Terraform configuration for an Azure VM",
    context={
        "cloud_provider": "azure",
        "resource_group": "my-rg",
        "region": "eastus"
    }
)

print(result)
```

## 🛠️ Available Tools

### 1. Terraform Operations
```python
terraform_operations(
    operation="plan",  # init, plan, apply, destroy, validate, fmt
    working_dir="./terraform",
    var_file="variables.tfvars",
    auto_approve=False
)
```

### 2. Ansible Operations
```python
ansible_operations(
    operation_type="playbook",  # or "adhoc"
    playbook_path="./playbook.yml",
    inventory="hosts.ini",
    extra_vars={"env": "production"}
)
```

### 3. AWS Operations
```python
aws_operations(
    service="ec2",
    operation="describe-instances",
    parameters={"filters": [{"Name": "instance-state-name", "Values": ["running"]}]},
    region="us-east-1"
)
```

### 4. Azure Operations
```python
azure_operations(
    service="vm",
    operation="list",
    resource_group="my-resource-group",
    subscription="your-subscription-id"
)
```

### 5. File Operations
```python
file_operations(
    operation="write",  # read, write, append, delete, exists
    file_path="./main.tf",
    content="# Terraform configuration..."
)
```

### 6. Code Validation
```python
validate_code(
    code_type="terraform",  # or "ansible"
    file_path="./terraform"
)
```

## 📚 Example Use Cases

### Example 1: Create AWS Infrastructure

```bash
python infrastructure_specialist.py --mode interactive
```

```
You: Create a complete AWS infrastructure with:
- VPC with CIDR 10.0.0.0/16
- 2 public subnets
- 2 private subnets
- Internet Gateway
- NAT Gateway
- Route tables
Save it to ./aws-vpc directory
```

### Example 2: Deploy Kubernetes Cluster

```
You: Create Terraform code to deploy an AKS cluster in Azure with:
- 3 node pool
- Standard_D2s_v3 VM size
- Auto-scaling enabled (min: 2, max: 5)
- Network plugin: azure
- Resource group: aks-production-rg
```

### Example 3: Ansible Server Configuration

```
You: Write an Ansible playbook to:
- Install Docker and Docker Compose
- Configure firewall rules
- Set up log rotation
- Install monitoring agents (node_exporter)
Target: Ubuntu 22.04 servers
```

### Example 4: Multi-Cloud Resource Audit

```
You: List and compare:
- All running EC2 instances in AWS (all regions)
- All VMs in Azure (my-subscription)
Generate a summary report
```

## ⚙️ Configuration

### config.json Structure

```json
{
  "llm_config": {
    "model": "qwen2.5-coder:32b",
    "base_url": "http://20.10.192.136:11434/v1",
    "api_key": "ollama",
    "temperature": 0.7,
    "timeout": 600
  },
  "work_dir": "./iac_workspace",
  "max_consecutive_auto_reply": 10,
  "safety": {
    "require_confirmation_for_destructive_operations": true,
    "auto_approve_terraform_apply": false,
    "auto_approve_terraform_destroy": false
  }
}
```

### Environment Variables

```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Azure Credentials
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
az login

# Terraform Variables
export TF_VAR_environment="production"
```

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. **Use IAM roles** when possible instead of access keys
3. **Enable MFA** for cloud accounts
4. **Review plans** before applying infrastructure changes
5. **Use state locking** for Terraform (S3 + DynamoDB)
6. **Implement least privilege** access policies
7. **Enable CloudTrail/Activity Logs** for audit trails

## 🧪 Testing

### Test Terraform Tool
```bash
python -c "
from iac_tools import InfrastructureTools
tools = InfrastructureTools()
result = tools.terraform_operations('init', './test-dir')
print(result)
"
```

### Test Agent Connection
```bash
curl -X POST http://20.10.192.136:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder:32b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 🐛 Troubleshooting

### Issue: "Model not found"
```bash
# Pull the model
curl http://20.10.192.136:11434/api/pull -d '{"name":"qwen2.5-coder:32b"}'
```

### Issue: "Terraform not found"
```bash
# Install Terraform
brew install terraform
# Verify
terraform --version
```

### Issue: "AWS credentials not configured"
```bash
# Configure AWS CLI
aws configure
# Or use environment variables
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### Issue: "Agent times out"
Edit `config.json`:
```json
{
  "llm_config": {
    "timeout": 1200
  }
}
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│   User Interface (CLI/Interactive)      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Infrastructure Specialist Agent       │
│   (Lightweight Python Class)            │
│   - Task planning and execution         │
│   - Multi-step reasoning                │
│   - Tool orchestration                  │
│   - Direct LLM communication            │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   LLM (Ollama)                          │
│   Model: qwen2.5-coder:32b              │
│   Endpoint: http://20.10.192.136:11434  │
│   API: Direct REST calls (no SDK)       │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Infrastructure Tools (iac_tools.py)   │
├─────────────────────────────────────────┤
│  - Terraform Operations                 │
│  - Ansible Operations                   │
│  - AWS CLI Operations                   │
│  - Azure CLI Operations                 │
│  - File Operations                      │
│  - Code Validation                      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Cloud Providers & Tools               │
├─────────────────────────────────────────┤
│  AWS    Azure    GCP    Kubernetes      │
└─────────────────────────────────────────┘
```

### Key Advantages of Simplified Architecture:
- ✅ **Lightweight**: No heavy AutoGen framework
- ✅ **Python 3.13 Compatible**: Works with latest Python
- ✅ **Easy to Debug**: Simple, readable code
- ✅ **Fast Startup**: Minimal dependencies
- ✅ **Direct Control**: Full control over LLM interactions

## 🔄 Workflow Example

```
User Request
    ↓
Agent analyzes request
    ↓
Agent plans steps
    ↓
Agent calls tools:
  - file_operations (create Terraform file)
  - terraform_operations (init)
  - terraform_operations (validate)
  - terraform_operations (plan)
  - [Wait for approval]
  - terraform_operations (apply)
    ↓
Agent reports results
    ↓
User receives output
```

## 📈 Performance Tips

1. **Use specific models for specific tasks**:
   - IaC code generation: `qwen2.5-coder:32b`
   - Complex reasoning: `deepseek-r1:14b`

2. **Optimize context**:
   - Provide clear, specific requirements
   - Include relevant constraints

3. **Leverage caching**:
   - Reuse initialized Terraform directories

## 📊 Monitoring & Observability

This agent integrates with **LangFuse** for comprehensive monitoring and observability.

### What LangFuse Tracks

- ✅ **LLM Calls**: All Ollama API calls with latency, token usage, and costs
- ✅ **Tool Executions**: Each Terraform/Ansible/AWS/Azure tool call with duration
- ✅ **Traces**: Complete task execution flows from start to finish
- ✅ **Sessions**: Group related tasks for analysis
- ✅ **Errors**: Automatic error tracking and debugging

### LangFuse Dashboard Features

1. **Traces View**:
   - See complete execution flow of each task
   - Drill down into each LLM generation and tool call
   - View input/output at each step
   - Identify bottlenecks and slow operations

2. **Sessions View**:
   - Track multiple related tasks in one session
   - Analyze conversation flow in interactive mode
   - Compare performance across sessions

3. **Metrics**:
   - Token usage per task/session/user
   - Cost tracking (if configured)
   - Latency distribution
   - Success/error rates

4. **Datasets & Evaluations**:
   - Create test datasets for common tasks
   - Run evaluations to track agent quality
   - Compare agent versions

### Setup LangFuse Monitoring

**Step 1: Deploy LangFuse** (see [AI/LangFuse/README.md](../../LangFuse/README.md))
```bash
cd ../../LangFuse
./deploy.sh
```

**Step 2: Get API Keys**
- Open LangFuse dashboard: `http://your-vm-ip:3000`
- Go to **Settings → API Keys**
- Create new key pair (public + secret)

**Step 3: Configure Agent**
Update `.env` file:
```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=http://your-vm-ip:3000
```

**Step 4: Run Agent**
```bash
python infrastructure_specialist.py
```

**Step 5: View Dashboard**
- Navigate to LangFuse dashboard
- Check **Traces** tab to see all task executions
- Use filters to find specific tools or time ranges

### Example Trace Structure

```
📊 Trace: infrastructure_task
├─ 🤖 Generation: ollama_generation (input: task description)
│  ├─ tokens: 150 prompt + 300 completion = 450 total
│  └─ duration: 2.3s
├─ 🔧 Span: tool_terraform_operations
│  ├─ input: {"action": "plan", "directory": "./terraform"}
│  ├─ output: {"success": true, "changes": 5}
│  └─ duration: 1.5s
├─ 🤖 Generation: ollama_generation (tool result analysis)
│  └─ duration: 1.8s
└─ ✅ Output: Infrastructure plan ready
   └─ total_duration: 5.6s
```

### Monitoring Best Practices

1. **Tag Your Tasks**: Add tags to traces for better filtering
2. **Use Sessions**: Group related operations for better analysis
3. **Set Up Alerts**: Configure alerts for errors or slow operations
4. **Regular Reviews**: Check dashboard weekly to optimize performance
5. **Cost Tracking**: Monitor token usage to optimize prompts

### Disable Monitoring

If you don't need monitoring:
```bash
# In .env file
LANGFUSE_ENABLED=false
```

Or uninstall LangFuse SDK:
```bash
pip uninstall langfuse
```
   - Cache Ansible facts

## 🤝 Contributing

To extend the agent with new capabilities:

1. Add new tool functions to `iac_tools.py`
2. Register tools in `infrastructure_specialist.py`
3. Update documentation

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **AutoGen Framework** by Microsoft Research
- **Ollama** for local LLM hosting
- **Qwen Team** for the qwen2.5-coder model
- **HashiCorp** for Terraform
- **Red Hat** for Ansible

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review AutoGen documentation: https://microsoft.github.io/autogen/
- Check Ollama docs: https://ollama.ai/

---

**Built with ❤️ for Infrastructure Automation**
