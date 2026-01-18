🤖 Kubernetes Chatbot – LLM-Powered Knowledge Assistant
This project is an AI-powered chatbot application designed to answer Kubernetes-related questions using a fine-tuned large language model (LLM). It enables users to interact in natural language and receive context-aware responses based on Kubernetes architecture, configuration, and operations.

🧠 The underlying model has been fine-tuned on a custom Kubernetes dataset, improving its accuracy and relevance for real-world use cases.

https://github.com/user-attachments/assets/94e269d6-6a64-461f-88f7-491ba1c85de6

![2025-03-31 14_02_00-Kubernetes Agent Chatbot - Work - Microsoft​ Edge](https://github.com/user-attachments/assets/d43ee038-8f60-482e-8b28-3560eb0dfe4c)

![2025-03-28 14_49_11-k8s_chatbox _ Google AI Studio](https://github.com/user-attachments/assets/93fb49e3-e4e1-4943-b414-3cb53eaebdba)


🚀 Features
```
✅ Fine-tuned LLM focused on Kubernetes knowledge
✅ Natural language chatbot interface
✅ Contextual understanding of K8s architecture & troubleshooting
✅ Flask-based web UI for fast interaction
✅ Simple Docker deployment
```
📁 Project Structure
```
KubernetesChatbot/
├── app.py               # Main Flask application
├── dataset/             # Sample dataset used for fine-tuning (optional)
├── db/                  # Stores conversation history or metadata
├── logs/                # Logging output from app activity
├── static/              # CSS, JavaScript, and static assets
├── templates/           # HTML templates for frontend
├── .env                 # Environment variables (model provider & keys)
├── .dockerignore        # Docker ignore rules
├── Dockerfile           # Docker container definition
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
ℹ️ The dataset/ folder is only for reference — it's the data used during model fine-tuning and not required for runtime.
```
🛠️ Technologies Used
```
Python
Flask
HuggingFace Transformers
Kubernetes-specific training data
```
🔧 Installation & Setup
```
1️⃣ Install Required Packages
git clone https://github.com/your-username/KubernetesChatbot.git
cd KubernetesChatbot
apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install --upgrade -q google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 app.py
```
### 2️⃣ Configure Environment Variables
Create a `.env` file (or modify the existing one) and set API keys:
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
```
⚠️ Note:

If you plan to use or continue fine-tuning with Google Gemini, you'll need to implement OAuth 2.0 authentication as outlined in Google's documentation:

🔗 [Gemini OAuth Setup Guide](https://ai.google.dev/gemini-api/docs/oauth)

🐳 Docker Setup
```
docker build -t kubernetes-chatbot .
docker run -p 5000:5000 --env-file .env kubernetes-chatbot
```
💬 Sample Questions
```
"How do I configure a HorizontalPodAutoscaler in Kubernetes?"
"What's the difference between a ConfigMap and a Secret?"
"How can I debug a CrashLoopBackOff issue in my pod?"
```
🎯 Use Cases
```
Kubernetes Q&A assistant for developers and platform teams
Onboarding and internal knowledge sharing
Faster troubleshooting and reduced documentation search
Foundation for internal platform intelligence
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
