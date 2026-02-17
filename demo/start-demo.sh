#!/bin/bash
# OpenWebUI Demo - Complete Startup Script
# Works on macOS and Linux

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 OpenWebUI AI Observability Demo - Startup${NC}"
echo "================================================"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo "📱 Detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "🐧 Detected: Linux"
else
    echo -e "${YELLOW}⚠️  Unknown OS: $OSTYPE${NC}"
    echo "   Continuing anyway..."
fi
echo ""

# Check Docker is available
echo -e "${BLUE}1️⃣ Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    if [[ "$OS" == "mac" ]]; then
        echo "   👉 Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    else
        echo "   👉 For WSL2: Start Docker Desktop on Windows"
        echo "   👉 For Linux: Install Docker Engine"
    fi
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✅ Docker found: $DOCKER_VERSION${NC}"

# Check Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker daemon not running${NC}"
    if [[ "$OS" == "mac" ]]; then
        echo "   👉 Start Docker Desktop application"
    else
        echo "   👉 Start Docker Desktop (Windows) or Docker daemon (Linux)"
    fi
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon is running${NC}"
echo ""

# Check .env exists
echo -e "${BLUE}2️⃣ Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "   👉 Copy .env.example to .env:"
    echo "      cp .env.example .env"
    echo "      nano .env  # Edit with your credentials"
    exit 1
fi

# Verify required environment variables
required_vars=("GEMINI_API_KEY" "GRAFANA_OTLP_TOKEN" "OTEL_EXPORTER_OTLP_ENDPOINT")
missing_vars=()
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing or empty required variables in .env:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "   👉 Edit .env and add these credentials:"
    echo "      nano .env"
    exit 1
fi

echo -e "${GREEN}✅ .env is properly configured${NC}"
echo ""

# Start services
echo -e "${BLUE}3️⃣ Starting Docker services...${NC}"
docker compose down 2>/dev/null || true  # Clean stop any existing
docker compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    echo "   👉 Check logs with: docker compose logs"
    exit 1
fi
echo ""

# Wait for services
echo -e "${BLUE}4️⃣ Waiting for services to initialize...${NC}"
echo "   (This takes about 30 seconds)"
for i in {30..1}; do
    echo -ne "   ${i}s remaining...\r"
    sleep 1
done
echo -e "${GREEN}✅ Services should be ready${NC}"
echo ""

# Check service status
echo -e "${BLUE}5️⃣ Verifying services...${NC}"
docker compose ps
echo ""

OPENWEBUI_RUNNING=$(docker compose ps | grep openwebui-instrumented | grep -c "Up" || echo "0")
OTEL_RUNNING=$(docker compose ps | grep otel-collector | grep -c "Up" || echo "0")

if [ "$OPENWEBUI_RUNNING" -eq "0" ]; then
    echo -e "${RED}❌ OpenWebUI container not running${NC}"
    echo "   👉 Check logs: docker logs openwebui-instrumented"
    exit 1
fi

if [ "$OTEL_RUNNING" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  OTEL Collector not running${NC}"
    echo "   Traces won't export to Grafana Cloud"
    echo "   👉 Check logs: docker logs otel-collector"
fi

echo -e "${GREEN}✅ Core services are running${NC}"
echo ""

# Test OpenWebUI endpoint
echo -e "${BLUE}6️⃣ Testing OpenWebUI endpoint...${NC}"
max_retries=10
retry=0
while [ $retry -lt $max_retries ]; do
    if curl -s -f http://localhost:3000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OpenWebUI is responding at http://localhost:3000${NC}"
        break
    else
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            echo -ne "   Waiting for OpenWebUI... (attempt $retry/$max_retries)\r"
            sleep 3
        else
            echo -e "${YELLOW}⚠️  OpenWebUI health check failed${NC}"
            echo "   Container might still be starting up"
            echo "   Try opening http://localhost:3000 in your browser anyway"
        fi
    fi
done
echo ""

# Success summary
echo "================================================"
echo -e "${GREEN}✅ Docker stack is running!${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo ""
echo "1. Open OpenWebUI in your browser:"
if [[ "$OS" == "mac" ]]; then
    echo "   ${GREEN}open http://localhost:3000${NC}"
else
    echo "   ${GREEN}http://localhost:3000${NC}"
fi
echo ""
echo "2. Sign up / log in"
echo "   (First user becomes admin automatically)"
echo ""
echo "3. Configure bots and tools:"
echo "   ${GREEN}python3 setup-bots.py${NC}"
echo "   (Will prompt for your OpenWebUI email/password)"
echo ""
echo "4. Generate test traces:"
echo "   ${GREEN}python3 load-gen-bots.py${NC}"
echo "   (Generates 85+ traces for Grafana)"
echo ""
echo "5. View traces in Grafana Cloud:"
echo "   - Go to Explore → Tempo"
echo "   - Query: ${GREEN}{ span.openinference.span.kind = \"LLM\" }${NC}"
echo "   - Should see traces within 60 seconds"
echo ""
echo "================================================"
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   - Full guide: ${GREEN}STARTUP_TEST.md${NC}"
echo "   - Lightning talk script: ${GREEN}LIGHTNING_TALK.md${NC}"
echo "   - Speaker notes: ${GREEN}SPEAKER_NOTES.md${NC}"
echo "   - Demo queries: ${GREEN}DEMO_CHAT.md${NC}"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo "   - View logs: ${GREEN}docker compose logs -f${NC}"
echo "   - Stop services: ${GREEN}docker compose down${NC}"
echo "   - Restart: ${GREEN}docker compose restart${NC}"
echo ""
echo "🎤 Ready to demo! Good luck!"
echo ""
