#!/bin/bash
set -e

# LangFuse Deployment Script
# Automates the deployment of LangFuse on a VM

echo "🚀 LangFuse Deployment Script"
echo "=============================="
echo ""

VM_IP="20.10.192.136"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Please do not run as root${NC}"
   exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo -e "${YELLOW}⚠️  Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker Compose not found. Installing...${NC}"
    sudo apt install -y docker-compose-plugin
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose found${NC}"
fi

# Step 2: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        
        # Generate secrets (using hex to avoid special characters)
        NEXTAUTH_SECRET=$(openssl rand -hex 32)
        SALT=$(openssl rand -hex 32)
        ENCRYPTION_KEY=$(openssl rand -hex 32)
        POSTGRES_PASSWORD=$(openssl rand -hex 16)
        
        # URL-encode password for DATABASE_URL
        POSTGRES_PASSWORD_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$POSTGRES_PASSWORD', safe=''))" 2>/dev/null || echo "$POSTGRES_PASSWORD")
        
        # Generate service passwords
        CLICKHOUSE_PASSWORD=$(openssl rand -hex 16)
        REDIS_AUTH=$(openssl rand -hex 16)
        MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)
        
        # Update .env
        sed -i "s|NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=$NEXTAUTH_SECRET|" .env
        sed -i "s|SALT=.*|SALT=$SALT|" .env
        sed -i "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|" .env
        sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|" .env
        sed -i "s|POSTGRES_PASSWORD_ENCODED=.*|POSTGRES_PASSWORD_ENCODED=$POSTGRES_PASSWORD_ENCODED|" .env
        sed -i "s|CLICKHOUSE_PASSWORD=.*|CLICKHOUSE_PASSWORD=$CLICKHOUSE_PASSWORD|" .env
        sed -i "s|REDIS_AUTH=.*|REDIS_AUTH=$REDIS_AUTH|" .env
        sed -i "s|MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD|" .env
        sed -i "s|NEXTAUTH_URL=.*|NEXTAUTH_URL=http://$VM_IP:3000|" .env
        
        echo -e "${GREEN}✅ .env file created with secure secrets${NC}"
        echo -e "${YELLOW}📝 Note: NEXTAUTH_URL set to http://$VM_IP:3000${NC}"
    else
        echo -e "${RED}❌ .env.example not found. Please create it first.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Step 3: Pull latest images
echo ""
echo "📥 Pulling latest Docker images..."
docker compose pull

# Step 4: Start services
echo ""
echo "🚀 Starting LangFuse services..."
docker compose up -d

# Step 5: Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker compose ps | grep -q "healthy"; then
        echo -e "${GREEN}✅ Services are healthy${NC}"
        break
    fi
    echo -n "."
    sleep 5
    WAITED=$((WAITED + 5))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${RED}❌ Services did not become healthy in time${NC}"
    echo "Check logs with: docker compose logs"
    exit 1
fi

# Step 6: Display access information
echo ""
echo "================================================================"
echo -e "${GREEN}🎉 LangFuse V3 deployed successfully!${NC}"
echo "================================================================"
echo ""
echo "📊 Dashboard URL: http://$VM_IP:3000"
echo "🗄️  MinIO Console: http://$VM_IP:9001"
echo "📦 Components: Web Server, Worker, PostgreSQL, ClickHouse, Redis, MinIO"
echo "💰 Cost tracking: Enabled with ClickHouse analytics"
echo "⚙️  Queue processing: Enabled (15 async workers)"
echo ""
echo "📝 Next steps:"
echo "  1. Open http://$VM_IP:3000 in your browser"
echo "  2. Click 'Sign Up' to create an admin account"
echo "  3. Create a new project"
echo "  4. Go to Settings → API Keys to generate keys"
echo "  5. Add keys to your agent's .env file"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs:    docker compose logs -f"
echo "  - Stop:         docker compose stop"
echo "  - Start:        docker compose start"
echo "  - Restart:      docker compose restart"
echo "  - Remove:       docker compose down"
echo "  - Full reset:   docker compose down -v"
echo ""
echo "================================================================"

# Step 7: Optional firewall configuration
if command_exists ufw && sudo ufw status | grep -q "Status: active"; then
    echo ""
    read -p "Configure firewall to allow port 3000? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo ufw allow 3000/tcp comment 'LangFuse'
        sudo ufw reload
        echo -e "${GREEN}✅ Firewall configured${NC}"
    fi
fi

echo ""
echo "✅ Deployment complete!"
