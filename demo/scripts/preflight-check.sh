#!/bin/bash
# Preflight checks for the OpenWebUI LLM Observability Demo
# Validates all prerequisites before starting the stack

set -uo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "  ${GREEN}PASS${NC}  $1"; PASS=$((PASS + 1)); }
fail() { echo -e "  ${RED}FAIL${NC}  $1"; FAIL=$((FAIL + 1)); }
warn() { echo -e "  ${YELLOW}WARN${NC}  $1"; WARN=$((WARN + 1)); }

echo "Preflight checks"
echo "================"
echo ""

# Docker installed
if command -v docker &>/dev/null; then
    pass "Docker installed ($(docker --version | cut -d' ' -f3 | tr -d ','))"
else
    fail "Docker not installed — https://www.docker.com/products/docker-desktop"
fi

# Docker daemon running
if docker ps &>/dev/null 2>&1; then
    pass "Docker daemon running"
else
    fail "Docker daemon not running — start Docker Desktop"
fi

# docker compose available
if docker compose version &>/dev/null 2>&1; then
    pass "docker compose available"
else
    fail "docker compose not available"
fi

# .env file exists
if [ -f "$DEMO_DIR/.env" ]; then
    pass ".env file exists"
else
    fail ".env file missing — run: cp .env.example .env && edit .env"
fi

# Required env vars set (only if .env exists)
if [ -f "$DEMO_DIR/.env" ]; then
    for var in OPENAI_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY GRAFANA_OTLP_TOKEN OTEL_EXPORTER_OTLP_ENDPOINT; do
        value=$(grep "^${var}=" "$DEMO_DIR/.env" 2>/dev/null | cut -d'=' -f2- || true)
        if [ -z "$value" ]; then
            fail "$var is not set in .env"
        elif echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder|REGION)'; then
            fail "$var has a placeholder value in .env"
        else
            pass "$var configured"
        fi
    done
fi

# python3 available
if command -v python3 &>/dev/null; then
    pass "python3 available ($(python3 --version 2>&1 | cut -d' ' -f2))"
else
    fail "python3 not found"
fi

# requests module
if python3 -c "import requests" 2>/dev/null; then
    pass "Python requests module installed"
else
    warn "Python requests module missing — run: pip3 install requests"
fi

# bats (optional)
if command -v bats &>/dev/null; then
    pass "bats installed (for make test)"
else
    warn "bats not installed — BATS tests unavailable"
fi

# Summary
echo ""
echo "================"
echo -e "Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}, ${YELLOW}${WARN} warnings${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Preflight failed. Fix the issues above and retry.${NC}"
    exit 1
fi

echo -e "${GREEN}Preflight passed!${NC}"
