# Deploy Open WebUI with Ollama on Azure VM

## Overview

Open WebUI is a self-hosted, feature-rich web interface for Ollama that provides a ChatGPT-like experience. This guide shows how to deploy it on your Azure VM alongside Ollama.

## Prerequisites

- Github address - https://github.com/open-webui/open-webui
- Azure VM with Ollama already running
- Docker installed on the VM
- Ollama running on port 11434

## Architecture

```
┌─────────────────────────────────────────┐
│         Azure VM (H100)                 │
│  ┌────────────┐      ┌───────────────┐ │
│  │   Ollama   │◄─────│  Open WebUI   │ │
│  │ :11434     │      │  :3000        │ │
│  └────────────┘      └───────────────┘ │
│       │                      │          │
│    GPU Access            Web UI         │
└─────────────────────────────────────────┘
              │
        Internet Access
```

## Deployment Steps

### 1. Deploy Open WebUI Container

SSH to your VM and run:

```bash
ssh azureuser@$VM_IP

# Run Open WebUI with Ollama integration
docker run -d \
  --name open-webui \
  --network host \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e WEBUI_AUTH=true \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main

# Check logs
docker logs open-webui
```

**Note:** Using `--network host` allows Open WebUI to easily connect to Ollama on localhost:11434.

### 2. Open Firewall Port

From your **local machine**, open port 3000:

```bash
az vm open-port \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --port 3000 \
  --priority 1002
```

### 3. Access Open WebUI

Open your browser and navigate to:

```
http://<VM_PUBLIC_IP>:3000 or http://<VM_PUBLIC_IP>:8080
```

**First-time Setup:**
1. Create an admin account (first user becomes admin)
2. Set your username and password
3. Login

## Alternative Deployment with Custom Port

If you prefer Open WebUI on a different port (e.g., 8080):

```bash
docker run -d \
  --name open-webui \
  -p 8080:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e WEBUI_AUTH=true \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

Then open port 8080 instead:

```bash
az vm open-port \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --port 8080 \
  --priority 1002
```

## Features

Open WebUI provides:

- **ChatGPT-like Interface**: Familiar chat experience
- **Model Switching**: Easily switch between Ollama models
- **Document Upload**: RAG support (upload PDFs, DOCX, etc.)
- **Conversation History**: All chats saved locally
- **Multi-user Support**: Create accounts for your team
- **API Access**: RESTful API for integrations
- **Dark Mode**: Beautiful UI with theme support
- **Code Highlighting**: Syntax highlighting for code blocks
- **Image Generation**: Integration with Stable Diffusion (optional)

## Configuration Options

### Enable/Disable User Registration

By default, anyone can sign up. To disable after creating your admin account:

```bash
docker stop open-webui
docker rm open-webui

docker run -d \
  --name open-webui \
  --network host \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e WEBUI_AUTH=true \
  -e ENABLE_SIGNUP=false \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

### Connect to External Ollama

If Ollama is running on a different machine:

```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://<OLLAMA_HOST>:11434 \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

## Usage Examples

### 1. Simple Chat

1. Select **qwen2.5:32b** from the model dropdown
2. Type your question: "Explain Kubernetes deployments"
3. Press Enter

### 2. Document Q&A (RAG)

1. Click the **📎 paperclip icon**
2. Upload a PDF or document
3. Ask questions about the document
4. Open WebUI will use embeddings + your model to answer

### 3. Code Generation

Ask for code directly:
- "Write a Python FastAPI endpoint that returns JSON"
- "Create a Kubernetes Deployment YAML for nginx"
- "Generate a Terraform module for Azure VM"

### 4. System Prompts

Create custom system prompts for specific tasks:

1. Click **Settings** → **Prompts**
2. Add custom prompts like:
   - "You are a Kubernetes expert..."
   - "You are a Python debugging assistant..."

## Management Commands

### View Logs

```bash
docker logs open-webui
docker logs -f open-webui  # Follow logs
```

### Restart Open WebUI

```bash
docker restart open-webui
```

### Update to Latest Version

```bash
docker pull ghcr.io/open-webui/open-webui:main
docker stop open-webui
docker rm open-webui

# Re-run the docker run command from Step 1
```

### Backup Data

```bash
# Backup Open WebUI data volume
docker run --rm \
  -v open-webui:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/open-webui-backup.tar.gz /data

# Copy backup to local machine
scp azureuser@$VM_IP:~/open-webui-backup.tar.gz .
```

### Restore Data

```bash
# On VM
docker run --rm \
  -v open-webui:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/open-webui-backup.tar.gz -C /
```

## Troubleshooting

### Open WebUI Can't Connect to Ollama

**Symptom:** "Failed to fetch models from Ollama"

**Solution:**
```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/tags

# 2. Check Open WebUI can reach Ollama
docker exec open-webui curl http://localhost:11434/api/tags

# 3. If using --network host, ensure no firewall blocking
sudo ufw allow 11434
```

### Port 3000 Already in Use

```bash
# Find process using port 3000
sudo lsof -i :3000

# Kill the process or use a different port
docker run -d \
  --name open-webui \
  -p 8080:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

### Can't Access from Browser

```bash
# 1. Verify Open WebUI is running
docker ps | grep open-webui

# 2. Check Azure NSG/Firewall
az vm open-port \
  --resource-group AZ-RG-TEST-01 \
  --name azeus2-vm-llm-test-01 \
  --port 3000

# 3. Test locally on VM first
ssh azureuser@$VM_IP
curl http://localhost:3000
```

### Models Not Appearing

```bash
# Ensure Ollama has models pulled
docker exec ollama ollama list

# Restart Open WebUI
docker restart open-webui
```

## Security Considerations

### 1. Use HTTPS (Production)

For production, use a reverse proxy with SSL:

```bash
# Install Caddy (automatic HTTPS)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Configure Caddy
sudo tee /etc/caddy/Caddyfile <<EOF
your-domain.com {
    reverse_proxy localhost:3000
}
EOF

sudo systemctl restart caddy
```

### 2. Restrict Access

Use Azure NSG to limit access to specific IP addresses:

```bash
# Allow only your IP
az network nsg rule create \
  --resource-group AZ-RG-TEST-01 \
  --nsg-name <NSG_NAME> \
  --name AllowWebUI \
  --priority 1003 \
  --source-address-prefixes <YOUR_IP>/32 \
  --destination-port-ranges 3000 \
  --access Allow \
  --protocol Tcp
```

### 3. Disable Public Signup

Set `ENABLE_SIGNUP=false` after creating your accounts.

### Continue.dev Integration

You can use Open WebUI's API in Continue:

```yaml
models:
  - name: Qwen via Open WebUI
    provider: openai
    model: qwen2.5:32b
    apiBase: http://<VM_IP>:3000/ollama/v1
    apiKey: not-needed
```

## Monitoring

### Health Check

```bash
# Check container health
docker inspect open-webui | jq '.[0].State.Health'

# Check API endpoint
curl http://localhost:3000/health
```

### Resource Usage

```bash
# Check container stats
docker stats open-webui

# Check disk usage
docker system df
du -sh /var/lib/docker/volumes/open-webui
```

## References

- **GitHub**: https://github.com/open-webui/open-webui
- **Documentation**: https://docs.openwebui.com
- **Discord**: https://discord.gg/5rJgQTnV4s

## Quick Reference

| Action | Command |
|--------|---------|
| Start Open WebUI | `docker start open-webui` |
| Stop Open WebUI | `docker stop open-webui` |
| View logs | `docker logs open-webui` |
| Restart | `docker restart open-webui` |
| Access URL | `http://<VM_IP>:3000` |
| Check models | Settings → Models |
| Backup data | See "Backup Data" section |
