# Quick Start Guide: Infrastructure Specialist Agent with LangFuse

This guide will get you from zero to a fully monitored Infrastructure AI agent in 10 minutes.

## Prerequisites

- ✅ Python 3.13+
- ✅ Ollama running (http://20.10.192.136:11434)
- ✅ Ubuntu VM with Docker (for LangFuse)
- ✅ Terraform, Ansible, AWS CLI, Azure CLI installed

## Step 1: Install Agent (2 minutes)

```bash
# Navigate to agent directory
cd /Users/osavdi@greentube.com/Documents/Scripts/AI/Agent/InfrastructureSpecialist

# Install dependencies
pip install -r requirements.txt

# Install LangFuse SDK v3.x (compatible with server 3.144.0+)
pip install 'langfuse>=3.0.0'

# Verify installation
python -c "import requests; import dotenv; from langfuse import Langfuse; print('✅ Dependencies OK')"
```

## Step 2: Configure Agent (1 minute)

The `.env` file already exists with Ollama configuration. Verify it:

```bash
cat .env
```

Should contain:
```bash
OLLAMA_BASE_URL=http://20.10.192.136:11434/v1
OLLAMA_MODEL=qwen2.5-coder:32b
LANGFUSE_ENABLED=false  # We'll enable this after Step 3
```

## Step 3: Deploy LangFuse (5 minutes)

**On your Ubuntu VM** (where you want to run LangFuse):

```bash
# SSH to VM
ssh your-user@your-vm-ip

# Copy LangFuse deployment files from Mac to VM
# (Or create them manually from AI/LangFuse/)
```

**Then run the automated deployment**:

```bash
# On VM
mkdir -p ~/langfuse
cd ~/langfuse

# Create .env file (edit the values)
cat > .env << 'EOF'
POSTGRES_USER=langfuse
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=langfuse
NEXTAUTH_SECRET=$(openssl rand -base64 32)
SALT=$(openssl rand -base64 32)
NEXTAUTH_URL=http://YOUR_VM_IP:3000
LANGFUSE_PORT=3000
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-langfuse}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-langfuse}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-langfuse}"]
      interval: 10s
      timeout: 5s
      retries: 5

  langfuse-server:
    image: langfuse/langfuse:latest
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "${LANGFUSE_PORT:-3000}:3000"
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-langfuse}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-langfuse}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      SALT: ${SALT}
      NEXTAUTH_URL: ${NEXTAUTH_URL}
      TELEMETRY_ENABLED: ${TELEMETRY_ENABLED:-true}
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: ${LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES:-false}
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000/api/public/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local

networks:
  default:
    name: langfuse_network
EOF

# Generate secrets and update .env
POSTGRES_PASSWORD=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)
SALT=$(openssl rand -base64 32)
VM_IP=$(hostname -I | awk '{print $1}')

sed -i "s/\$(openssl rand -base64 32)/$POSTGRES_PASSWORD/1" .env
sed -i "s/\$(openssl rand -base64 32)/$NEXTAUTH_SECRET/2" .env
sed -i "s/\$(openssl rand -base64 32)/$SALT/3" .env
sed -i "s/YOUR_VM_IP/$VM_IP/" .env

# Start LangFuse
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for LangFuse to be ready..."
sleep 30

# Check status
docker compose ps
docker compose logs -n 20
```

**Open firewall** (if needed):
```bash
sudo ufw allow 3000/tcp
```

## Step 4: Get LangFuse API Keys (1 minute)

1. Open browser: `http://your-vm-ip:3000`
2. Create account (first user is admin)
3. Go to **Settings** → **API Keys**
4. Click **Create New Key**
5. Copy both keys:
   - Public Key: `pk-lf-xxxxxxxxxxxx`
   - Secret Key: `sk-lf-xxxxxxxxxxxx`

## Step 5: Connect Agent to LangFuse (1 minute)

**On your Mac**, update `.env`:

```bash
cd /Users/osavdi@greentube.com/Documents/Scripts/AI/Agent/InfrastructureSpecialist

# Update these lines in .env
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxx  # Your public key
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxx  # Your secret key
LANGFUSE_HOST=http://your-vm-ip:3000
```

**How it works** (Simplified Integration):
The agent uses LangFuse SDK v3.x with `@observe` decorators:
- `@observe(name="infrastructure_task")` - Auto-creates traces for each task
- `@observe(as_type="generation")` - Auto-tracks LLM calls with model info
- `@observe(as_type="span")` - Auto-tracks tool executions with input/output

No manual context updates needed - the decorator handles everything automatically! ✨

## Step 6: Test Agent (1 minute)

```bash
# Test without monitoring
python infrastructure_specialist.py

# In interactive mode, try:
# > List my infrastructure tools
# > What can you help me with?
# > exit
```

## Step 7: Verify Monitoring (1 minute)

1. Go back to LangFuse dashboard: `http://your-vm-ip:3000`
2. Click **Traces** in the sidebar
3. You should see your agent's execution traces
4. Click on a trace to see:
   - Full conversation flow
   - LLM generations with token counts
   - Tool executions with timing
   - Input/output at each step

## 🎉 Success!

You now have:
- ✅ Infrastructure Specialist AI agent running
- ✅ LangFuse monitoring all operations
- ✅ Dashboard to analyze performance
- ✅ Cost and usage tracking

## Next Steps

### Try Real Tasks

```bash
python infrastructure_specialist.py
```

**Example tasks**:
```
> Create a Terraform configuration for an AWS VPC with 2 public subnets

> Write an Ansible playbook to install Docker on Ubuntu

> List all my running EC2 instances

> Validate my Terraform code in ./terraform directory
```

### Explore LangFuse Dashboard

- **Traces**: See all agent executions
- **Sessions**: Group related tasks
- **Datasets**: Create test cases
- **Playground**: Test prompts
- **Analytics**: View usage statistics

### Optimize Performance

1. Check slow operations in LangFuse
2. Optimize prompts based on token usage
3. Set up alerts for errors
4. Create evaluation datasets

## Troubleshooting

### Agent can't reach Ollama
```bash
# Test Ollama connectivity
curl http://20.10.192.136:11434/api/tags

# If fails, update OLLAMA_BASE_URL in .env
```

### LangFuse not receiving traces
```bash
# Test LangFuse server health
curl http://your-vm-ip:3000/api/public/health

# Test authentication
python3 -c "
from langfuse import Langfuse
lf = Langfuse(
    public_key='pk-lf-xxx',
    secret_key='sk-lf-xxx',
    host='http://your-vm-ip:3000'
)
print('✅ Connected to LangFuse')
"

# Check agent logs for LangFuse errors
python infrastructure_specialist.py --mode task --task "test"
# Should see: "📊 LangFuse monitoring enabled: http://..."

# Verify SDK version (must be 3.x for server 3.144.0+)
pip show langfuse | grep Version
# Should show: Version: 3.11.x or higher

# If wrong version, reinstall:
pip uninstall -y langfuse
pip install 'langfuse>=3.0.0'
```
# Check .env has correct keys
cat .env | grep LANGFUSE

# Verify LangFuse is running
ssh your-vm-ip
docker compose ps

# Check agent logs for LangFuse errors
python infrastructure_specialist.py 2>&1 | grep -i langfuse
```

### LangFuse dashboard not loading
```bash
# Check services
docker compose ps

# View logs
docker compose logs langfuse-server
docker compose logs postgres

# Restart if needed
docker compose restart
```

### Token usage seems high
- Check **Traces** to see which prompts are large
- Optimize system prompts in code
- Use more efficient tool descriptions

## Configuration Reference

### Agent (.env)
```bash
# Required
OLLAMA_BASE_URL=http://20.10.192.136:11434/v1
OLLAMA_MODEL=qwen2.5-coder:32b
OLLAMA_TEMPERATURE=0.7

# Optional Monitoring
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=http://vm-ip:3000

# Safety
AGENT_AUTO_APPROVE_APPLY=false
AGENT_AUTO_APPROVE_DESTROY=false
```

### LangFuse (docker-compose.yml)
```yaml
# Change ports if needed
ports:
  - "3000:3000"  # LangFuse UI
  - "5432:5432"  # PostgreSQL (only if needed externally)
```

## Advanced: Production Deployment

See full guides:
- [Infrastructure Agent README](./README.md)
- [LangFuse Deployment Guide](../../LangFuse/README.md)

Covers:
- HTTPS/TLS setup
- Backup strategies
- High availability
- Kubernetes deployment
- OAuth integration
- Email notifications

## Support

- LangFuse docs: https://langfuse.com/docs
- Ollama docs: https://ollama.ai/docs
- Terraform: https://www.terraform.io/docs
- Ansible: https://docs.ansible.com/

---

**Total Setup Time**: ~10 minutes  
**Agent Status**: ✅ Running  
**Monitoring**: ✅ Enabled  
**Ready**: 🚀 Go build infrastructure!
