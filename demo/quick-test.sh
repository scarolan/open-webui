#!/bin/bash
# Quick startup test script for OpenWebUI demo
# Works on macOS and Linux

set -e  # Exit on error

echo "🚀 OpenWebUI Demo - Quick Startup Test"
echo "======================================="
echo ""

# Check Docker is available
echo "1️⃣ Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    echo "   👉 Install Docker Desktop:"
    echo "      macOS/Windows: https://www.docker.com/products/docker-desktop"
    echo "      Linux: https://docs.docker.com/engine/install/"
    exit 1
fi
docker --version
echo "✅ Docker is available"
echo ""

# Check .env exists and has required vars
echo "2️⃣ Checking .env configuration..."
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "   👉 Copy .env.example to .env and configure it"
    exit 1
fi

required_vars=("GEMINI_API_KEY" "GRAFANA_OTLP_TOKEN" "OTEL_EXPORTER_OTLP_ENDPOINT")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        echo "❌ Missing ${var} in .env"
        exit 1
    fi
done
echo "✅ .env is configured"
echo ""

# Start services
echo "3️⃣ Starting docker services..."
docker compose up -d
echo "✅ Services started"
echo ""

# Wait for services
echo "4️⃣ Waiting 30 seconds for services to initialize..."
sleep 30
echo ""

# Check services are running
echo "5️⃣ Checking service status..."
docker compose ps
echo ""

# Test OpenWebUI endpoint
echo "6️⃣ Testing OpenWebUI endpoint..."
if curl -s -f http://localhost:3000/health > /dev/null; then
    echo "✅ OpenWebUI is responding at http://localhost:3000"
else
    echo "⚠️  OpenWebUI health check failed (might still be starting up)"
fi
echo ""

echo "======================================="
echo "✅ Docker stack is running!"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Sign up/log in (first user becomes admin)"
echo "   3. Run: python3 setup-bots.py"
echo "   4. Run: python3 load-gen-bots.py"
echo "   5. Check Grafana Cloud for traces"
echo ""
echo "📖 Full test guide: STARTUP_TEST.md"
echo "🎤 Demo materials: DEMO_README.md"
echo ""
