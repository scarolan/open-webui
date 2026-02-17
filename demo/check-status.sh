#!/bin/bash
# Quick status check for OpenWebUI demo

echo "🔍 OpenWebUI Demo Status Check"
echo "================================"
echo ""

# Get auth token
echo "🔑 Authenticating..."
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"sean.carolan@grafana.com","password":"open-sesame"}' | jq -r '.token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi
echo "✅ Authenticated"
echo ""

# Check models
echo "📋 Checking models..."
MODELS=$(curl -s http://localhost:3000/api/models \
  -H "Authorization: Bearer $TOKEN")

MODEL_COUNT=$(echo "$MODELS" | jq '.data | length')
echo "Found $MODEL_COUNT models:"
echo "$MODELS" | jq -r '.data[] | "  - \(.id) (\(.name))"'
echo ""

# Check tools
echo "🔧 Checking tools..."
TOOLS=$(curl -s http://localhost:3000/api/v1/tools \
  -H "Authorization: Bearer $TOKEN")

TOOL_COUNT=$(echo "$TOOLS" | jq '. | length')
echo "Found $TOOL_COUNT tools:"
echo "$TOOLS" | jq -r '.[] | "  - \(.name)"' | head -10
echo ""

# Check connections
echo "🔌 Checking API connections..."
CONFIGS=$(curl -s http://localhost:3000/api/v1/configs \
  -H "Authorization: Bearer $TOKEN")

echo "$CONFIGS" | jq '.openai // "No OpenAI config"'
echo ""

echo "================================"
echo "✅ Status check complete"
