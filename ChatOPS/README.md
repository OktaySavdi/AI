# 🚀 Kubernetes ChatOps Assistant

This repository contains a **Kubernetes ChatOps Assistant** that leverages AI models to interpret natural language queries, generate `kubectl` commands, and execute them securely. The assistant provides explanations for the commands and troubleshooting guidance.

https://github.com/user-attachments/assets/01e02dad-b980-424c-ac88-94ba79f40398

## 📌 Features
- 🧠 **AI-Powered Command Generation**: Converts natural language queries into `kubectl` commands.
- 🔍 **Command Execution**: Executes safe Kubernetes commands (`get`, `describe`, `logs`, `create`) and returns results.
- 🛡 **Security**: Prevents destructive commands like `delete`, `apply`, or `edit`.
- 🔄 **Session Management**: Tracks conversation history and adapts to system prompt changes.
- 📊 **Cluster Insights**: Provides cluster health and status information.
- 🛠 **Multi-Model AI Support**: Works with OpenAI, Azure OpenAI, Gemini, Claude, and DeepSeek.

## 📂 Project Structure
```
📂 ChatOPS
│── 📂 static/             # Static assets (CSS, JS, etc.)
│── 📂 templates/          # HTML templates for the Flask app
│── 📂 kubeconfig/         # Kubernetes config file
│── 📂 logs/               # Application logs
│── 📂 db/                 # SQLite database for conversation history
│── 📄 app.py              # Main Flask application
│── 📄 .env                # Environment variables (model provider & keys)
│── 📄 requirements.txt    # Python dependencies
├── 📄 Dockerfile          # Docker container definition
├── 📄 .dockerignore       # Docker ignore rules
│── 📄 README.md           # Documentation (You're here!)
ℹ️ The dataset/ folder is only for reference — it's the data used during model fine-tuning and not required for runtime.
```

## 🔧 Installation & Setup

### 1️⃣ Install Required Packages
```sh
apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install --upgrade -q google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 app.py
```

### 2️⃣ Configure Environment Variables
Create a `.env` file in the project root and set the following variables:
```
# Select the model provider to use
MODEL_PROVIDER = "azure"  # Options: "openai", "gemini", "deepseek", "claude", "azure_openai"

# API Keys
OPENAI_API_KEY="your-openai-api-key"
GEMINI_API_KEY="your-gemini-api-key"
DEEPSEEK_API_KEY="your-deepseek-api-key"
CLAUDE_API_KEY="your-claude-api-key"
AZURE_OPENAI_API_KEY="your-azureopenai-api-key"

# Model Names
GEMINI_MODEL="tunedModels/k8schatbox-fs06ghlt6rvc" # https://ai.google.dev/gemini-api/docs/oauth
OPENAI_MODEL=gpt-4
DEEPSEEK_MODEL=deepseek-llm
CLAUDE_MODEL=claude-3-sonnet-2024-02-19

# Azure OpenAI Endpoint
AZURE_OPENAI_MODEL="<model_name>"
AZURE_OPENAI_DEPLOYMENT_NAME="k8s_chatbox"
AZURE_OPENAI_API_VERSION="<version>"
AZURE_OPENAI_ENDPOINT="<URL>"

# Logging Level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=DEBUG

# Kubeconfig Path
KUBECONFIG_PATH=kubeconfig/config
```

The application will start on `http://0.0.0.0:5000`.

## 🔍 How It Works
1. **Natural Language Query**: Users input queries like "Show me all pods in the default namespace."
2. **AI Processing**: The assistant converts the query into a `kubectl` command.
3. **Command Execution**: The command is executed, and the results are returned to the user.
4. **Explanation**: The assistant provides an explanation of the command and its output.

⚠️ Note:

If you plan to use or continue fine-tuning with Google Gemini, you'll need to implement OAuth 2.0 authentication as outlined in Google's documentation:

🔗 [Gemini OAuth Setup Guide](https://ai.google.dev/gemini-api/docs/oauth)

🐳 Docker Setup
```
docker build -t kubernetes-chatbot .
docker run -p 5000:5000 --env-file .env kubernetes-chatbot
```

## 🤖 Supported AI Models

The project supports multiple AI models for Terraform code generation and error fixing. You can configure the model provider in your `.env` file.

| Provider      | API Key Required | Model Name           | API Endpoint Required |
|--------------|----------------|----------------------|----------------------|
| **OpenAI**       | ✅ Yes         | `Fine-Tuning`   | ❌ No  |
| **Gemini**       | ✅ Yes         | `Fine-Tuning`   | ❌ No  |
| **DeepSeek**     | ✅ Yes         | `Fine-Tuning`   | ❌ No  |
| **Claude**       | ✅ Yes         | `Fine-Tuning`   | ❌ No  |
| **Azure OpenAI** | ✅ Yes         | `Fine-Tuning`   | ✅ Yes |

![2025-04-09 14_31_58-20 218 86 20_5000_api_k8s_status](https://github.com/user-attachments/assets/56af8050-a29a-4ac1-b35d-f767b16eaae1)
![2025-04-09 15_39_29-Kubernetes Agent Chatbot](https://github.com/user-attachments/assets/76f379ff-371a-4a8c-9d24-0f2163944fa7)
![2025-04-09 15_40_29-Kubernetes Agent Chatbot](https://github.com/user-attachments/assets/5031dbc3-bda5-4776-ba37-8fe23de78cd6)
![2025-04-09 15_47_10-Kubernetes Agent Chatbot](https://github.com/user-attachments/assets/b4e07427-d10e-4837-833b-e30d0f81b8f6)
![2025-04-09 15_50_08-Kubernetes Agent Chatbot](https://github.com/user-attachments/assets/67e0af74-ed32-45c1-840b-786822995dc8)
![2025-04-09 15_51_02-Kubernetes Agent Chatbot](https://github.com/user-attachments/assets/b78652a5-682d-4c33-93c7-6f0e71b7e61f)

🤝 Contributing

Contributions and suggestions are welcome! Feel free to fork the repo and submit a pull request.
