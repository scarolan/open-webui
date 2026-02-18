#!/bin/bash
# Start the OpenWebUI LLM Observability Demo
# Runs preflight, starts containers, creates admin, configures bots
# Usage: ./start-demo.sh [--with-traffic]

set -e

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DEMO_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default credentials
OPENWEBUI_EMAIL="${OPENWEBUI_EMAIL:-team-se@grafana.com}"
OPENWEBUI_PASSWORD="${OPENWEBUI_PASSWORD:-open-sesame}"
OPENWEBUI_NAME="${OPENWEBUI_NAME:-Demo User}"

echo -e "${BLUE}OpenWebUI AI Observability Demo${NC}"
echo "================================================"
echo ""

########################################
# Step 1: Preflight
########################################
echo -e "${BLUE}[1/6] Running preflight checks...${NC}"
"$DEMO_DIR/scripts/preflight-check.sh"
echo ""

########################################
# Step 2: Start Docker stack
########################################
echo -e "${BLUE}[2/6] Starting Docker stack...${NC}"
docker compose down 2>/dev/null || true
docker compose up -d 2>&1 | grep -E "Creating|Started|Error" || true
echo -e "   ${GREEN}Containers started${NC}"
echo ""

########################################
# Step 3: Wait for OpenWebUI
########################################
echo -e "${BLUE}[3/6] Waiting for OpenWebUI to be ready...${NC}"
READY=0
for i in $(seq 1 40); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health 2>/dev/null || echo "000")
    if [ "$STATUS" = "200" ]; then
        echo -e "   ${GREEN}OpenWebUI ready (took ~$((i * 5))s)${NC}"
        READY=1
        break
    fi
    printf "   Waiting... (%ds)\r" $((i * 5))
    sleep 5
done
if [ "$READY" -eq 0 ]; then
    echo -e "${RED}OpenWebUI failed to start after 200s${NC}"
    echo "   Check logs: docker compose logs openwebui"
    exit 1
fi
echo ""

########################################
# Step 4: Create admin account
########################################
echo -e "${BLUE}[4/6] Creating admin account...${NC}"

# Try signing in first (account may already exist from persistent volume)
SIGNIN=$(curl -s -X POST http://localhost:3000/api/v1/auths/signin \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$OPENWEBUI_EMAIL\",\"password\":\"$OPENWEBUI_PASSWORD\"}" 2>/dev/null)

TOKEN=$(echo "$SIGNIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "None" ]; then
    echo -e "   ${GREEN}Signed in (existing account)${NC}"
else
    # Create new account
    SIGNUP=$(curl -s -X POST http://localhost:3000/api/v1/auths/signup \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$OPENWEBUI_EMAIL\",\"password\":\"$OPENWEBUI_PASSWORD\",\"name\":\"$OPENWEBUI_NAME\"}" 2>/dev/null)

    TOKEN=$(echo "$SIGNUP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

    if [ -n "$TOKEN" ] && [ "$TOKEN" != "None" ]; then
        echo -e "   ${GREEN}Admin account created${NC}"
    else
        echo -e "${RED}Failed to create account${NC}"
        echo "   Response: $SIGNUP"
        echo "   Try manually: open http://localhost:3000 and sign up"
        exit 1
    fi
fi
echo ""

########################################
# Step 5: Configure bots and tools
########################################
echo -e "${BLUE}[5/6] Configuring bots and tools...${NC}"
export OPENWEBUI_EMAIL OPENWEBUI_PASSWORD
python3 setup-bots.py 2>&1 | grep -E "✅|❌|⚠️|Setup Complete"
echo ""

########################################
# Step 6: Verify everything
########################################
echo -e "${BLUE}[6/6] Verifying setup...${NC}"

BOT_COUNT=$(curl -s http://localhost:3000/api/models \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(len([m for m in d.get('data',[]) if m['id'] in ['hal','marvin','bender','glados','jarvis','cortana']]))" 2>/dev/null || echo "0")

TOOL_COUNT=$(curl -s http://localhost:3000/api/v1/tools/ \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null | \
    python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

echo -e "   Bots: ${GREEN}$BOT_COUNT/6${NC}"
echo -e "   Tools: ${GREEN}$TOOL_COUNT/6${NC}"

if [ "$BOT_COUNT" -eq 6 ] && [ "$TOOL_COUNT" -eq 6 ]; then
    echo -e "   ${GREEN}All configured!${NC}"
else
    echo -e "   ${YELLOW}Some items may be missing. Check the UI.${NC}"
fi
echo ""

########################################
# Optional: Generate test traffic
########################################
if [[ "${1:-}" == "--with-traffic" ]]; then
    echo -e "${BLUE}Generating test traces...${NC}"
    python3 load-gen-bots.py 2>&1 | tail -10
    echo ""
fi

########################################
# Done!
########################################
echo "================================================"
echo -e "${GREEN}Demo is ready!${NC}"
echo "================================================"
echo ""
echo -e "   OpenWebUI:  ${GREEN}http://localhost:3000${NC}"
echo -e "   Email:       ${GREEN}$OPENWEBUI_EMAIL${NC}"
echo -e "   Password:    ${GREEN}$OPENWEBUI_PASSWORD${NC}"
echo ""
echo -e "   Bots:        HAL, Marvin, Bender, GLADOS, JARVIS, Cortana"
echo -e "   Tools:       39 custom functions across 6 tool sets"
echo ""
echo -e "${BLUE}Quick commands:${NC}"
echo "   make load-gen         Generate bot traces"
echo "   make test-smoke       Run smoke tests"
echo "   make test-telemetry   Run telemetry tests"
echo "   make stop             Stop the demo"
echo ""
echo -e "${BLUE}Grafana query:${NC}"
echo '   { span.openinference.span.kind = "LLM" }'
echo ""
