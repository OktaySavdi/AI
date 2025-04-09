# 🚀 Kubernetes ChatOps Assistant

This repository contains a **Kubernetes ChatOps Assistant** that leverages AI models to interpret natural language queries, generate `kubectl` commands, and execute them securely. The assistant provides explanations for the commands and troubleshooting guidance.

![ChatOps](https://github.com/user-attachments/assets/23901c74-08bd-45b9-93ef-3002807d6315)

## 📌 Features
- 🧠 **AI-Powered Command Generation**: Converts natural language queries into `kubectl` commands.
- 🔍 **Command Execution**: Executes safe Kubernetes commands (`get`, `describe`, `logs`) and returns results.
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

🤝 Contributing

Contributions and suggestions are welcome! Feel free to fork the repo and submit a pull request.
