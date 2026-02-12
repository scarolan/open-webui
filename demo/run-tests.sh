#!/bin/bash
# Convenience script for running demo tests

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="unit"
VERBOSE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --tempo)
            TEST_TYPE="tempo"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v -s"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run-tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit          Run unit tests only (default)"
            echo "  --integration   Run integration tests (requires running OpenWebUI)"
            echo "  --tempo         Run Tempo query tests (requires Grafana Cloud)"
            echo "  --all           Run all tests"
            echo "  -v, --verbose   Verbose output"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run-tests.sh                    # Run unit tests"
            echo "  ./run-tests.sh --integration      # Run integration tests"
            echo "  ./run-tests.sh --all -v           # Run all tests with verbose output"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Header
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              LLM Observability Demo - Test Runner            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "tests" ]; then
    echo -e "${RED}❌ Error: tests/ directory not found${NC}"
    echo "   Please run this script from the demo/ directory"
    exit 1
fi

# Set PYTHONPATH to include backend (MUST be done before any imports)
BACKEND_PATH="$(cd .. && pwd)/backend"
export PYTHONPATH="${BACKEND_PATH}:${PYTHONPATH}"

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"

# Check pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${RED}❌ pytest not found${NC}"
    echo "   Install with: cd tests && pip install -r requirements.txt"
    exit 1
fi

# Check main project imports
if ! python3 -c "import sys; sys.path.insert(0, '${BACKEND_PATH}'); from open_webui.utils.telemetry.llm_instrumentation import LLMSpanManager" 2>/dev/null; then
    echo -e "${RED}❌ Main project dependencies not installed${NC}"
    echo "   Missing dependencies like 'typer', 'fastapi', etc."
    echo ""
    echo "   Fix with ONE of these options:"
    echo "   1. Quick fix: pip install typer fastapi aiohttp"
    echo "   2. Full setup: cd tests && ./setup-tests.sh"
    echo "   3. Full install: cd ${BACKEND_PATH} && pip install -e ."
    exit 1
fi

echo -e "${GREEN}✅ Dependencies OK${NC}"
echo ""

# Change to tests directory
cd tests

# Run tests based on type
case $TEST_TYPE in
    unit)
        echo -e "${BLUE}🧪 Running Unit Tests${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        pytest $VERBOSE -m "not integration and not tempo" test_unit_instrumentation.py
        ;;

    integration)
        echo -e "${BLUE}🔗 Running Integration Tests${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        # Check if OpenWebUI is running
        if ! curl -s http://localhost:3000/health >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  OpenWebUI doesn't appear to be running${NC}"
            echo "   Start it with: docker compose up -d"
            echo "   Continuing anyway..."
        fi

        # Check credentials
        if [ -z "$TEST_EMAIL" ] || [ -z "$TEST_PASSWORD" ]; then
            echo -e "${YELLOW}⚠️  TEST_EMAIL and TEST_PASSWORD not set${NC}"
            echo "   Tests may be skipped"
        fi

        pytest $VERBOSE -m integration test_integration_traces.py
        ;;

    tempo)
        echo -e "${BLUE}📊 Running Tempo Query Tests${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        # Check credentials
        if [ -z "$GRAFANA_TEMPO_URL" ] || [ -z "$GRAFANA_TEMPO_TOKEN" ]; then
            echo -e "${RED}❌ Grafana Cloud credentials not set${NC}"
            echo "   Set GRAFANA_TEMPO_URL and GRAFANA_TEMPO_TOKEN"
            exit 1
        fi

        echo -e "${YELLOW}💡 Make sure you've generated test data:${NC}"
        echo "   python3 ../load-gen-bots.py"
        echo "   python3 ../load-gen-openai-tools-TEST.py"
        echo "   (and wait 60s for propagation)"
        echo ""

        pytest $VERBOSE -m tempo test_dashboard_queries.py
        ;;

    all)
        echo -e "${BLUE}🎯 Running All Tests${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        # Unit tests
        echo ""
        echo -e "${BLUE}1️⃣  Unit Tests${NC}"
        pytest $VERBOSE -m "not integration and not tempo" test_unit_instrumentation.py

        # Integration tests
        echo ""
        echo -e "${BLUE}2️⃣  Integration Tests${NC}"
        if [ -z "$TEST_EMAIL" ] || [ -z "$TEST_PASSWORD" ]; then
            echo -e "${YELLOW}⚠️  Skipping (credentials not set)${NC}"
        else
            pytest $VERBOSE -m integration test_integration_traces.py
        fi

        # Tempo tests
        echo ""
        echo -e "${BLUE}3️⃣  Tempo Query Tests${NC}"
        if [ -z "$GRAFANA_TEMPO_URL" ] || [ -z "$GRAFANA_TEMPO_TOKEN" ]; then
            echo -e "${YELLOW}⚠️  Skipping (credentials not set)${NC}"
        else
            pytest $VERBOSE -m tempo test_dashboard_queries.py
        fi
        ;;
esac

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Tests Complete!                                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
