# 🚀 AI-Powered Terraform Code Generator

This repository contains an **AI-driven Terraform module generation and validation system**, utilizing **OpenAI, Gemini, DeepSeek, Claude, and Azure OpenAI** to create and auto-correct Terraform configurations.

## 📌 Features
```
- 🏗 Automated Terraform Code Generation**: AI generates Terraform configurations based on structured prompts.
- 🔍 Auto-Fixing of Terraform Errors**: Errors detected during validation are automatically corrected.
- 🔄 Git Integration: Clones repositories, modifies files, and pushes changes to GitHub/GitLab.
- 🏗 Multi-Model AI Support: Works with OpenAI (GPT-4), Gemini, DeepSeek, Claude, and Azure OpenAI.
- 🛠 CI/CD Ready: Runs Terraform validation (`terraform validate`) and format checks (`terraform fmt`).
```
## 📂 Project Structure
```
📂 ai-terraform-generator 
│── 📂 git_repo/ # Cloned Git repository (Terraform modules live here) 
│── 📄 main.py # Entry point (Runs AI workflow) 
│── 📄 .env # API Keys and Configurations 
│── 📄 prompt.txt # AI prompt structure for Terraform generation 
│── 📄 requirements.txt # Python dependencies 
│── 📄 README.md # Documentation (You're here!)
```

## 🔧 Installation & Setup

### 1️⃣ Install Required Packages
```sh
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 2️⃣ Configure Environment Variables
Create `a .env` file (or modify the existing one) and set API keys:
```
# Select the model provider to use
MODEL_PROVIDER = "azure_openai"  # Options: "openai", "gemini", "deepseek", "claude", "azure_openai"

# API Keys
OPENAI_API_KEY="your-openai-api-key"
GENAI_API_KEY="your-gemini-api-key"
DEEPSEEK_API_KEY="your-deepseek-api-key"
CLAUDE_API_KEY="your-claude-api-key"
AZURE_OPENAI_API_KEY="your-azureopenai-api-key"

# Model Names
GEMINI_MODEL=gemini-2.0-flash
OPENAI_MODEL=gpt-4
DEEPSEEK_MODEL=deepseek-llm
CLAUDE_MODEL=claude-3-sonnet-2024-02-19

# Azure OpenAI Endpoint
AZURE_OPENAI_MODEL="<model_name>"
AZURE_OPENAI_DEPLOYMENT_NAME="<deployment_name>"
AZURE_OPENAI_API_VERSION="<version>"
AZURE_OPENAI_ENDPOINT="<URL>"
```
### 3️⃣ Run the AI Terraform Workflow
```
python3 main.py
```
🔥 How It Works
```
1️⃣ Clones the Git Repository
2️⃣ Generates Terraform Code using AI models
3️⃣ Validates & Fixes Errors with terraform validate
4️⃣ Updates and Saves Code if fixes are needed
5️⃣ Pushes to GitLab/GitHub
```
📜 AI Prompt System
```
prompt.txt guides AI generation with structured rules.
Ensures variable consistency, best practices, and format correctness.
Auto-fix logic improves Terraform code when errors occur.
```
## 🤖 Supported AI Models

The project supports multiple AI models for Terraform code generation and error fixing. You can configure the model provider in your `.env` file.

| Provider      | API Key Required | Model Name           | API Endpoint Required |
|--------------|----------------|----------------------|----------------------|
| **OpenAI**       | ✅ Yes         | `gpt-4`              | ❌ No  |
| **Gemini**       | ✅ Yes         | `gemini-2.0-flash`   | ❌ No  |
| **DeepSeek**     | ✅ Yes         | `deepseek-llm`       | ❌ No  |
| **Claude**       | ✅ Yes         | `claude-3-sonnet`    | ❌ No  |
| **Azure OpenAI** | ✅ Yes         | Custom Deployment    | ✅ Yes |

🛠 Troubleshooting
```
Error: Terraform validation failed?
→ Check terraform validate output in logs. AI should auto-fix errors.

Issue with AI response?
→ Verify API keys in .env and ensure the correct model is set.
```
🎯 Future Improvements
```
Implement CI/CD pipeline for automated testing.
```








