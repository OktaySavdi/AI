# 🤖 AI Agents Collection

A comprehensive collection of AI-powered agents designed for DevOps, Infrastructure as Code (IaC), and Kubernetes operations. These agents leverage multiple LLM providers to automate and assist with various infrastructure and cloud management tasks.

---

## 📂 Projects Overview

| Project | Description | Key Features |
|---------|-------------|--------------|
| [ChatOPS](./ChatOPS) | Kubernetes ChatOps Assistant | Natural language to `kubectl` commands, secure execution |
| [CodeGeneration](./CodeGeneration) | AI-Powered Terraform Code Generator | Auto-generate & auto-fix Terraform configurations |
| [InfrastructureSpecialist](./InfrastructureSpecialist) | Infrastructure as Code AI Agent | Terraform, Ansible, AWS CLI, Azure CLI operations |
| [KubernetesChatbot](./KubernetesChatbot) | Kubernetes Knowledge Assistant | Fine-tuned LLM for K8s Q&A and troubleshooting |

---

## 🚀 ChatOPS

**Kubernetes ChatOps Assistant** that converts natural language queries into `kubectl` commands and executes them securely.

### Features
- 🧠 AI-powered command generation from natural language
- 🔍 Safe command execution (`get`, `describe`, `logs`, `create`)
- 🛡 Security: Blocks destructive commands (`delete`, `apply`, `edit`)
- 📊 Cluster health insights and status information
- 🔄 Session management with conversation history

### Quick Start
```bash
cd ChatOPS
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

[📖 Full Documentation](./ChatOPS/README.md)

---

## 🏗️ CodeGeneration

**AI-driven Terraform module generation and validation system** that creates, validates, and auto-corrects Terraform configurations.

### Features
- 🏗 Automated Terraform code generation
- 🔍 Auto-fixing of Terraform validation errors
- 🔄 Git integration (clone, modify, push)
- 🛠 CI/CD ready with `terraform validate` and `terraform fmt`

### Quick Start
```bash
cd CodeGeneration
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

[📖 Full Documentation](./CodeGeneration/README.md)

---

## ⚙️ InfrastructureSpecialist

**Lightweight AI agent** specialized in Infrastructure as Code, integrating directly with Ollama LLM for multi-cloud infrastructure management.

### Features
- 🏗️ Terraform operations (init, plan, apply, destroy, validate)
- ⚙️ Ansible automation (playbooks and ad-hoc commands)
- ☁️ AWS operations (EC2, S3, EKS, VPC)
- 🔷 Azure operations (VM, AKS, networking, storage)
- 📁 File operations for IaC management
- ✅ Code validation and syntax checking

### Quick Start
```bash
cd InfrastructureSpecialist
pip install -r requirements.txt
python3 infrastructure_specialist.py
```

[📖 Full Documentation](./InfrastructureSpecialist/README.md)

---

## 💬 KubernetesChatbot

**AI-powered chatbot** designed to answer Kubernetes-related questions using a fine-tuned LLM with a custom Kubernetes dataset.

### Features
- ✅ Fine-tuned LLM focused on Kubernetes knowledge
- ✅ Natural language chatbot interface
- ✅ Contextual understanding of K8s architecture & troubleshooting
- ✅ Flask-based web UI
- ✅ Docker deployment ready

### Quick Start
```bash
cd KubernetesChatbot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

[📖 Full Documentation](./KubernetesChatbot/README.md)

---

## 🤖 Supported AI Models

All projects support multiple AI model providers. Configure your preferred provider in the `.env` file:

| Provider | API Key Required | Endpoint Required |
|----------|------------------|-------------------|
| **OpenAI** | ✅ Yes | ❌ No |
| **Azure OpenAI** | ✅ Yes | ✅ Yes |
| **Google Gemini** | ✅ Yes | ❌ No |
| **Anthropic Claude** | ✅ Yes | ❌ No |
| **DeepSeek** | ✅ Yes | ❌ No |
| **Ollama** (local) | ❌ No | ✅ Yes |

---

## 🔧 Common Prerequisites

### Python Environment
```bash
# Install Python virtual environment
apt install python3.12-venv  # Ubuntu/Debian
brew install python@3.12     # macOS

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### Environment Variables
Each project requires a `.env` file with API keys and configurations. See individual project READMEs for specific requirements.

```env
# Example .env structure
MODEL_PROVIDER="azure_openai"  # Options: openai, gemini, deepseek, claude, azure_openai

# API Keys (configure based on your provider)
OPENAI_API_KEY="your-key"
AZURE_OPENAI_API_KEY="your-key"
GEMINI_API_KEY="your-key"
CLAUDE_API_KEY="your-key"
DEEPSEEK_API_KEY="your-key"
```

---

## 🐳 Docker Support

Most projects include Docker support for containerized deployment:

```bash
# Build and run (example for ChatOPS)
cd ChatOPS
docker build -t chatops-assistant .
docker run -p 5000:5000 --env-file .env chatops-assistant
```

---

## 📚 Documentation

Each project contains its own detailed README with:
- Installation instructions
- Configuration options
- Usage examples
- API documentation
- Troubleshooting guides

---

## 🛡️ Security Considerations

- **Never commit `.env` files** containing API keys
- ChatOPS blocks destructive Kubernetes commands by default
- Use read-only credentials where possible
- Review generated IaC code before applying to production

---

## 📄 License

See individual project directories for license information.

---

## 🤝 Contributing

Contributions are welcome! Please read the individual project documentation before submitting pull requests.
