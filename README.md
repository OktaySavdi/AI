🤖 AI Projects by Oktay Savdi

This repository contains AI-powered tools and experiments developed for cloud infrastructure, DevOps automation, and Kubernetes operations leveraging large language models like OpenAI, Gemini, Claude, and DeepSeek.

---

## 📁 Repository Structure

### 🤖 Agent/

AI-powered agents for various DevOps and infrastructure automation tasks.

#### ☸️ ChatOPS
An AI-powered **Kubernetes assistant** that connects directly to your cluster and allows you to interact using **natural language**, without needing any knowledge of `kubectl` or CLI commands.

Built with a **fine-tuned large language model**, this assistant provides real-time insights about workloads, resources, errors, and general Kubernetes health, all via a simple chat interface.

- ✅ Fine-tuned on real-world Kubernetes datasets  
- ✅ Answers questions on architecture, workloads, and operations  
- ✅ Provides real-time insights using natural language  
- ✅ Flask-based web interface  
- ✅ Docker-compatible deployment  

📂 [`Agent/ChatOPS/`](Agent/ChatOPS/)

#### 🔨 CodeGeneration
An AI agent that automates Terraform module generation using fine-tuned LLMs. It simplifies cloud infrastructure provisioning through intelligent prompts, error correction, and GitOps workflows.

- ✅ Auto-generates Terraform modules 
- ✅ Fixes validation errors automatically 
- ✅ Integrates with GitHub/GitLab 
- ✅ Supports multiple LLMs (GPT-4, Gemini, DeepSeek, Claude, Azure OpenAI)

📂 [`Agent/CodeGeneration/`](Agent/CodeGeneration/)

#### 🏗️ InfrastructureSpecialist
An intelligent infrastructure specialist agent that helps with Infrastructure as Code (IaC) operations and cloud resource management.

- ✅ Infrastructure as Code assistance
- ✅ Cloud resource management
- ✅ Configuration management
- ✅ IaC tools integration

📂 [`Agent/InfrastructureSpecialist/`](Agent/InfrastructureSpecialist/)

#### ☸️ KubernetesChatbot
A chatbot application powered by a fine-tuned LLM, trained on Kubernetes knowledge. It answers questions about Kubernetes architecture, operations, and best practices via natural language.

- ✅ Fine-tuned on Kubernetes-specific datasets
- ✅ Natural language question answering
- ✅ Flask-based web UI
- ✅ Docker-compatible deployment

📂 [`Agent/KubernetesChatbot/`](Agent/KubernetesChatbot/)

---

### 🎯 Fine-Tuning/

Fine-tuning resources and tools for training custom AI models.

#### 🔓 Opensource
Tools and scripts for fine-tuning open-source language models with Kubernetes and cloud infrastructure datasets.

- ✅ Model fine-tuning with Unsloth
- ✅ GGUF conversion for optimized inference
- ✅ Custom training datasets
- ✅ Ollama Modelfile configurations
- ✅ Testing and validation scripts

📂 [`Fine-Tuning/Opensource/`](Fine-Tuning/Opensource/)

---

### 📊 Monitor/

Monitoring and observability solutions for AI applications.

#### 🔍 LangFuse
Deployment and configuration for LangFuse - an open-source LLM engineering platform for tracing, monitoring, and debugging AI applications.

- ✅ Docker Compose deployment
- ✅ LLM tracing and monitoring
- ✅ Performance analytics
- ✅ Quick deployment scripts

📂 [`Monitor/LangFuse/`](Monitor/LangFuse/)

---

### 🦙 Ollama/

Deployment guides and configurations for running Ollama - a platform for running large language models locally.

#### ☸️ DeployOnK8S
Instructions for deploying Ollama on Kubernetes clusters.

📂 [`Ollama/DeployOnK8S/`](Ollama/DeployOnK8S/)

#### 💻 DeployOnVM
Instructions for deploying Ollama on virtual machines.

📂 [`Ollama/DeployOnVM/`](Ollama/DeployOnVM/)

---

### 🌐 OpenWebUI/

Open WebUI deployment and configuration - a user-friendly web interface for interacting with LLMs.

- ✅ Web-based LLM interface
- ✅ Multi-model support
- ✅ Easy deployment

📂 [`OpenWebUI/`](OpenWebUI/)

---

## 🧠 Models Used

This repository makes use of several LLMs for experimentation and deployment:

- **OpenAI** (GPT-4) 
- **Gemini** 
- **DeepSeek** 
- **Claude** 
- **Azure OpenAI**
- **Ollama** (Local LLM runtime)
