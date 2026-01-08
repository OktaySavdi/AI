# LangFuse Self-Hosted Deployment Guide 🔍

Complete guide for deploying LangFuse on a VM and integrating with your Infrastructure Specialist AI Agent.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Manual Installation](#manual-installation)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Agent Integration](#agent-integration)
- [Accessing Dashboard](#accessing-dashboard)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**LangFuse** is an open-source LLM observability platform for AI agents and applications.

**What you'll monitor:**
- 🔍 Agent conversations (step-by-step execution)
- 🛠️ Tool execution traces
- 💰 Cost tracking (tokens, API calls)
- ⚡ Performance metrics (latency, errors)
- 📊 Session analytics and replay

**Architecture (V3):**
```
┌─────────────────────────────────┐
│  Your AI Agent                  │
│  (infrastructure_specialist.py) │
└────────────┬────────────────────┘
             │ Sends traces via SDK
             ▼
┌─────────────────────────────────────────────────────┐
│  LangFuse Server (VM)                               │
│  ┌─────────────────┐  ┌──────────────────────┐     │
│  │ Web Server      │  │ Worker Container     │     │
│  │ (Port 3000)     │  │ (Async Queue Jobs)   │     │
│  │ - Web UI        │  │ - Ingestion Queue    │     │
│  │ - REST API      │  │ - OTEL Queue         │     │
│  └────────┬────────┘  └──────────┬───────────┘     │
│           └──────────┬────────────┘                 │
│                      │ Redis Queue (Port 6379)      │
│                      ▼                               │
│  ┌──────────────┐  ┌───────────┐  ┌──────────┐     │
│  │ PostgreSQL   │  │ ClickHouse│  │ MinIO    │     │
│  │ (Traces)     │  │ (Analytics)  │ (Storage)│     │
│  │ Port 5432    │  │ Port 8123 │  │ Port 9002│     │
│  └──────────────┘  └───────────┘  └──────────┘     │
└─────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### VM Requirements
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: 2+ cores
- **Disk**: 20GB+ free space
- **Network**: Open ports 3000 (LangFuse), 5432 (PostgreSQL)

### Software Requirements
```bash
# Option 1: Docker (Recommended)
docker --version  # >= 20.10
docker-compose --version  # >= 2.0

# Option 2: Manual
node --version  # >= 18.x
npm --version   # >= 9.x
postgresql --version  # >= 14
```

---

## 🐳 Quick Start (Docker Compose)

### Step 1: Prepare VM

```bash
# SSH into your VM
ssh user@your-vm-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### Step 2: Create Deployment Directory

```bash
# Create directory
mkdir -p ~/langfuse
cd ~/langfuse

# Download docker-compose.yml
wget https://raw.githubusercontent.com/langfuse/langfuse/main/docker-compose.yml

# Or create manually (see below)
```

### Step 3: Configure Environment

Create `.env` file:

```bash
cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=langfuse
POSTGRES_PASSWORD=your-secure-password-here
# URL-encoded password (special chars like / need encoding)
POSTGRES_PASSWORD_ENCODED=your-secure-password-here
POSTGRES_DB=langfuse
POSTGRES_PORT=5432

# ClickHouse Configuration (V3)
CLICKHOUSE_USER=langfuse
CLICKHOUSE_PASSWORD=langfuse_secure_password
CLICKHOUSE_DB=langfuse
CLICKHOUSE_PORT=8123

# LangFuse Configuration
NEXTAUTH_SECRET=$(openssl rand -hex 32)
NEXTAUTH_URL=http://your-vm-ip:3000
SALT=$(openssl rand -hex 32)

# Optional: Email notifications
# EMAIL_FROM=noreply@yourdomain.com
# SMTP_CONNECTION_URL=smtp://user:pass@smtp.example.com:587

# Optional: S3 for media storage
# S3_ENDPOINT=https://s3.amazonaws.com
# S3_ACCESS_KEY_ID=
# S3_SECRET_ACCESS_KEY=
# S3_BUCKET_NAME=langfuse-media
# S3_REGION=us-east-1
EOF

# Generate secure secrets (using hex to avoid special characters)
sed -i "s/NEXTAUTH_SECRET=.*/NEXTAUTH_SECRET=$(openssl rand -hex 32)/" .env
sed -i "s/SALT=.*/SALT=$(openssl rand -hex 32)/" .env

# Generate and encode PostgreSQL password
PG_PASS=$(openssl rand -hex 16)
PG_PASS_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PG_PASS', safe=''))")
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$PG_PASS/" .env
sed -i "s/POSTGRES_PASSWORD_ENCODED=.*/POSTGRES_PASSWORD_ENCODED=$PG_PASS_ENCODED/" .env

# Update VM IP
VM_IP=$(hostname -I | awk '{print $1}')
sed -i "s/your-vm-ip/$VM_IP/" .env
```

### Step 4: Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: langfuse-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - langfuse

  # ClickHouse Database (for V3 - optional for V2)
  clickhouse:
    image: clickhouse/clickhouse-server:24-alpine
    container_name: langfuse-clickhouse
    environment:
      CLICKHOUSE_DB: ${CLICKHOUSE_DB:-langfuse}
      CLICKHOUSE_USER: ${CLICKHOUSE_USER:-langfuse}
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:-langfuse_secure_password}
      CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    ports:
      - "${CLICKHOUSE_PORT:-8123}:8123"
      - "${CLICKHOUSE_NATIVE_PORT:-9000}:9000"
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
    healthcheck:
      test: ["CMD-SHELL", "clickhouse-client --query='SELECT 1' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 40s
    restart: unless-stopped
    networks:
      - langfuse

  # LangFuse Server (V2 - stable version)
  langfuse-server:
    image: langfuse/langfuse:2
    container_name: langfuse-server
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "3000:3000"
    environment:
      # Use encoded password to handle special characters
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD_ENCODED}@postgres:5432/${POSTGRES_DB}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      NEXTAUTH_URL: ${NEXTAUTH_URL}
      SALT: ${SALT}
      TELEMETRY_ENABLED: ${TELEMETRY_ENABLED:-true}
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: ${LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES:-false}
    restart: unless-stopped
    networks:
      - langfuse
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/public/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  clickhouse_data:
    driver: local

networks:
  langfuse:
    driver: bridge
EOF
```

**Note**: This configuration uses **Langfuse V2** (stable) with ClickHouse ready for future V3 upgrade.

### Step 5: Deploy LangFuse

```bash
# Start services
docker compose up -d

# Check logs
docker compose logs -f

# Wait for services to be healthy
docker compose ps

# Expected output:
# NAME                  STATUS              PORTS
# langfuse-postgres     Up (healthy)        0.0.0.0:5432->5432/tcp
# langfuse-server       Up (healthy)        0.0.0.0:3000->3000/tcp
```

### Step 6: Access Dashboard

```bash
# Get your VM IP
echo "LangFuse URL: http://$(hostname -I | awk '{print $1}'):3000"

# Open in browser
# http://YOUR_VM_IP:3000
```

**First Login:**
1. Go to `http://YOUR_VM_IP:3000`
2. Click "Sign Up"
3. Create admin account
4. Create a new project
5. Get API keys from Settings → API Keys

---

## 🔧 Manual Installation (Without Docker)

### Step 1: Install Dependencies

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install build tools
sudo apt install -y build-essential git
```

### Step 2: Setup PostgreSQL

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER langfuse WITH PASSWORD 'your-secure-password';
CREATE DATABASE langfuse OWNER langfuse;
GRANT ALL PRIVILEGES ON DATABASE langfuse TO langfuse;
\q
EOF
```

### Step 3: Clone and Build LangFuse

```bash
# Clone repository
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://langfuse:your-secure-password@localhost:5432/langfuse
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://$(hostname -I | awk '{print $1}'):3000
SALT=$(openssl rand -base64 32)
EOF

# Run database migrations
npm run db:migrate

# Build application
npm run build

# Start server
npm run start

# Or use PM2 for production
sudo npm install -g pm2
pm2 start npm --name langfuse -- start
pm2 save
pm2 startup
```

---

## ☸️ Kubernetes Deployment

### Step 1: Create Namespace

```bash
kubectl create namespace langfuse
```

### Step 2: Create Secret

```bash
kubectl create secret generic langfuse-secrets \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=nextauth-secret=$(openssl rand -base64 32) \
  --from-literal=salt=$(openssl rand -base64 32) \
  -n langfuse
```

### Step 3: Deploy PostgreSQL

```yaml
# postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: langfuse
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: langfuse
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: langfuse
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: postgres-password
        - name: POSTGRES_DB
          value: langfuse
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: langfuse
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

### Step 4: Deploy LangFuse

```yaml
# langfuse.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langfuse
  namespace: langfuse
spec:
  replicas: 2
  selector:
    matchLabels:
      app: langfuse
  template:
    metadata:
      labels:
        app: langfuse
    spec:
      containers:
      - name: langfuse
        image: langfuse/langfuse:latest
        env:
        - name: DATABASE_URL
          value: postgresql://langfuse:$(POSTGRES_PASSWORD)@postgres:5432/langfuse
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: postgres-password
        - name: NEXTAUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: nextauth-secret
        - name: NEXTAUTH_URL
          value: http://langfuse.example.com
        - name: SALT
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: salt
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /api/public/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/public/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: langfuse
  namespace: langfuse
spec:
  selector:
    app: langfuse
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f postgres.yaml
kubectl apply -f langfuse.yaml

# Check status
kubectl get pods -n langfuse
kubectl get svc -n langfuse
```

---

## 🔗 Agent Integration

### Step 1: Get API Keys

1. Go to LangFuse dashboard: `http://YOUR_VM_IP:3000`
2. Navigate to **Settings** → **API Keys**
3. Click **Create new API keys**
4. Copy:
   - **Public Key** (starts with `pk-lf-...`)
   - **Secret Key** (starts with `sk-lf-...`)

### Step 2: Update Agent Configuration

Add to your agent's `.env` file:

```bash
# LangFuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=http://YOUR_VM_IP:3000
```

### Step 3: Install Python SDK

```bash
cd /path/to/your/agent
pip install langfuse
```

### Step 4: Integrate with Agent

The agent code has been updated to support LangFuse. See the integration in `infrastructure_specialist.py`.

**Usage:**
```bash
# With monitoring enabled
LANGFUSE_ENABLED=true python3 infrastructure_specialist.py --mode interactive

# Without monitoring
LANGFUSE_ENABLED=false python3 infrastructure_specialist.py --mode interactive
```

---

## 📊 Accessing Dashboard

### Main Dashboard
- **URL**: `http://YOUR_VM_IP:3000`
- **Default Port**: 3000

### Key Features

1. **Traces View**
   - See all agent executions
   - Drill down into tool calls
   - View input/output for each step

2. **Sessions**
   - Group related traces
   - Track conversation flows
   - Analyze user interactions

3. **Metrics**
   - Token usage
   - Cost tracking
   - Latency analysis
   - Error rates

4. **Users**
   - Track agent users
   - Usage patterns
   - Performance by user

### Example Trace Structure

```
Session: "Infrastructure Task #123"
├── Trace: "Create AWS VPC"
│   ├── Span: "LLM Call" (tokens: 1234, cost: $0.02)
│   ├── Span: "Tool: terraform_operations"
│   │   └── Metadata: {operation: "plan", working_dir: "./vpc"}
│   └── Span: "LLM Call" (tokens: 567, cost: $0.01)
└── Metadata: {user: "oktay", duration: "45s", total_cost: "$0.03"}
```

---

## 🔥 Firewall Configuration

### UFW (Ubuntu)
```bash
sudo ufw allow 3000/tcp comment 'LangFuse Web UI'
sudo ufw allow 5432/tcp comment 'PostgreSQL'
sudo ufw reload
```

### iptables
```bash
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
sudo iptables-save
```

### Cloud Provider Security Groups
- **AWS**: Add inbound rule for port 3000 (HTTP)
- **Azure**: Add NSG rule for port 3000
- **GCP**: Add firewall rule for tcp:3000

---

## 🛡️ Production Hardening

### 1. Enable HTTPS

```bash
# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
cat > /etc/nginx/sites-available/langfuse << 'EOF'
server {
    listen 80;
    server_name langfuse.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/langfuse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d langfuse.yourdomain.com
```

### 2. Backup Strategy

```bash
# Automated PostgreSQL backup script
cat > /usr/local/bin/backup-langfuse.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/langfuse"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec langfuse-postgres pg_dump -U langfuse langfuse | gzip > \
  $BACKUP_DIR/langfuse_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "langfuse_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-langfuse.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-langfuse.sh" | crontab -
```

### 3. Monitoring

```bash
# Install monitoring tools
docker run -d --name=prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d --name=grafana \
  -p 3001:3000 \
  grafana/grafana
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to LangFuse

```bash
# Check if services are running
docker compose ps

# Check logs
docker compose logs langfuse-server
docker compose logs postgres

# Restart services
docker compose restart

# Check network
curl http://localhost:3000/api/public/health
```

### Issue: Database connection failed

```bash
# Check PostgreSQL
docker exec langfuse-postgres psql -U langfuse -d langfuse -c "\l"

# Reset database
docker compose down -v
docker compose up -d
```

### Issue: Password contains special characters

If your PostgreSQL password contains special characters (like `/`, `@`, `:`, etc.), they need to be URL-encoded:

```bash
# Encode password using Python
PASSWORD="your-password-with/special@chars"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PASSWORD', safe=''))")
echo "Encoded: $ENCODED"

# Update .env file
echo "POSTGRES_PASSWORD_ENCODED=$ENCODED" >> .env
```

### Issue: ClickHouse warnings about get_mempolicy

The warnings `get_mempolicy: Operation not permitted` are harmless and don't affect functionality. They occur due to missing kernel capabilities in containers.

### Issue: Port already in use

```bash
# Find process using port 3000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>

# Or use different port
# Edit docker-compose.yml: "3001:3000"
```

### Issue: High memory usage

```bash
# Check resource usage
docker stats

# Increase limits in docker-compose.yml
services:
  langfuse-server:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📚 Additional Resources

- **Official Docs**: https://langfuse.com/docs
- **GitHub**: https://github.com/langfuse/langfuse
- **Discord**: https://discord.gg/7NXusRtqYU
- **Self-Hosting Guide**: https://langfuse.com/docs/deployment/self-host

---

## 🎯 Next Steps

1. ✅ Deploy LangFuse on VM
2. ✅ Create admin account
3. ✅ Generate API keys
4. ✅ Configure agent with keys
5. ✅ Run test task
6. ✅ View traces in dashboard
7. ✅ Set up backups
8. ✅ Configure HTTPS (production)

---

**Deployed by**: Infrastructure Specialist Team  
**Last Updated**: January 2026  
**Support**: your-team@example.com
