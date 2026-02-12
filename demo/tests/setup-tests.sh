#!/bin/bash
# Setup script for installing test dependencies

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Test Dependencies Setup                                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found${NC}"
    echo "   Please run this script from the demo/tests/ directory"
    exit 1
fi

# Step 1: Install main project dependencies
echo -e "${BLUE}📦 Step 1: Installing main project dependencies...${NC}"
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment!${NC}"
    echo "   Consider creating one:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to backend and install
cd ../../backend
if [ -f "pyproject.toml" ]; then
    echo -e "${BLUE}Installing from pyproject.toml...${NC}"
    pip install -e . --quiet
    echo -e "${GREEN}✅ Main project dependencies installed${NC}"
else
    echo -e "${RED}❌ pyproject.toml not found in backend/${NC}"
    exit 1
fi

# Step 2: Install test dependencies
cd ../demo/tests
echo ""
echo -e "${BLUE}📦 Step 2: Installing test dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Test dependencies installed${NC}"

# Step 3: Verify installation
echo ""
echo -e "${BLUE}🔍 Step 3: Verifying installation...${NC}"

# Check if imports work
python3 -c "
import pytest
import opentelemetry
from open_webui.utils.telemetry.llm_instrumentation import LLMSpanManager
print('✅ All imports successful')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Verification successful${NC}"
else
    echo -e "${RED}❌ Import verification failed${NC}"
    echo "   Try manually installing dependencies:"
    echo "   cd ../../backend && pip install -e ."
    exit 1
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Complete!                                             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Set environment variables (for integration/Tempo tests):"
echo "     export TEST_EMAIL='your-email@example.com'"
echo "     export TEST_PASSWORD='your-password'"
echo "     export GRAFANA_TEMPO_URL='https://tempo-prod-us-east-0.grafana.net'"
echo "     export GRAFANA_TEMPO_TOKEN='your-base64-token'"
echo ""
echo "  2. Run tests:"
echo "     cd .."
echo "     ./run-tests.sh"
echo ""
