#!/bin/bash

# OpenWebUI Load Generation Script
# Generates diverse LLM traces for dashboard development

OPENWEBUI_URL="http://localhost:3000"
MODEL="gemini-2.0-flash-exp"

# Array of diverse prompts (varied lengths for different token counts)
PROMPTS=(
    "What is 2+2?"
    "Explain quantum entanglement in simple terms."
    "Write a haiku about observability."
    "What are the key differences between REST and GraphQL APIs?"
    "Describe the architecture of a microservices system with detailed explanations of service discovery, load balancing, and circuit breakers."
    "List 5 programming languages."
    "Explain how Docker containers differ from virtual machines, including memory overhead, startup time, and isolation mechanisms."
    "What is Kubernetes?"
    "Write a detailed guide on implementing distributed tracing in a polyglot microservices environment using OpenTelemetry."
    "Hello!"
    "Explain the CAP theorem with real-world examples of AP and CP systems."
    "What time is it?"
    "Compare and contrast Prometheus pull-based monitoring versus push-based systems like Graphite."
    "Tell me a joke."
    "Describe the differences between sampling strategies in distributed tracing: head-based, tail-based, and adaptive sampling."
    "What is the meaning of life?"
    "Explain how to optimize Grafana dashboard queries for large-scale time series data."
    "Count to 10."
    "What are the trade-offs between using PromQL aggregations versus recording rules?"
    "Why is the sky blue?"
)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting OpenWebUI Load Generation${NC}"
echo -e "${BLUE}Target: $OPENWEBUI_URL${NC}"
echo -e "${BLUE}Model: $MODEL${NC}"
echo -e "${BLUE}Requests: ${#PROMPTS[@]}${NC}"
echo ""

# Counter for requests
count=0
total=${#PROMPTS[@]}

# Send requests
for prompt in "${PROMPTS[@]}"; do
    ((count++))

    echo -e "${YELLOW}[$count/$total]${NC} Sending: ${prompt:0:60}..."

    # Send chat completion request
    response=$(curl -s -X POST "$OPENWEBUI_URL/api/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$MODEL\",
            \"messages\": [
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"stream\": false
        }")

    # Check if request succeeded
    if echo "$response" | grep -q "choices"; then
        # Extract token usage if available
        tokens=$(echo "$response" | jq -r '.usage.total_tokens // "N/A"' 2>/dev/null)
        echo -e "${GREEN}✓${NC} Response received (${tokens} tokens)"
    else
        echo -e "${YELLOW}⚠${NC} Response received (unknown format)"
    fi

    # Small delay between requests to avoid rate limiting
    sleep 2
done

echo ""
echo -e "${GREEN}✅ Load generation complete!${NC}"
echo -e "${BLUE}Generated $total traces${NC}"
echo ""
echo -e "${YELLOW}Wait 10-30 seconds for traces to appear in Tempo${NC}"
echo -e "${YELLOW}Then query: { span.openinference.span.kind = \"LLM\" }${NC}"
