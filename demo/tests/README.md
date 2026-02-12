# LLM Observability Demo - Test Suite

Comprehensive test suite for the LLM observability demo, including unit tests, integration tests, and dashboard query validation.

---

## 📋 **Test Structure**

```
demo/tests/
├── __init__.py                      # Package init
├── conftest.py                      # Pytest config and fixtures
├── test_unit_instrumentation.py     # Unit tests for LLM instrumentation
├── test_integration_traces.py       # Integration tests for tracing
├── test_dashboard_queries.py        # Dashboard query validation
├── requirements.txt                 # Test dependencies
└── README.md                        # This file
```

---

## 🚀 **Quick Start**

### **1. Install Dependencies**

**Option A: Automated Setup (Recommended)**

```bash
# From the demo/tests directory
./setup-tests.sh
```

This script will:
1. Install main project dependencies from `backend/`
2. Install test-specific dependencies
3. Verify everything works

**Option B: Manual Setup**

```bash
# Step 1: Install main project dependencies
cd ../../backend
pip install -e .

# Step 2: Install test dependencies
cd ../demo/tests
pip install -r requirements.txt

# Step 3: Verify
python3 -c "from open_webui.utils.telemetry.llm_instrumentation import LLMSpanManager; print('✅ OK')"
```

**Option C: Install Everything**

```bash
# From repo root (includes all deps + test deps)
pip install -e ".[dev]"
cd demo/tests
pip install -r requirements.txt
```

### **2. Set Environment Variables**

For integration and Tempo tests, set these environment variables:

```bash
# OpenWebUI credentials
export TEST_EMAIL="your-email@example.com"
export TEST_PASSWORD="your-password"

# Grafana Cloud Tempo (for dashboard query tests)
export GRAFANA_TEMPO_URL="https://tempo-prod-us-east-0.grafana.net"
export GRAFANA_TEMPO_TOKEN="your-base64-encoded-token"

# Optional: Override OpenWebUI URL (defaults to http://localhost:3000)
export OPENWEBUI_URL="http://localhost:3000"
```

### **3. Run Tests**

```bash
# Run all tests
pytest -v

# Run only unit tests (no external dependencies)
pytest -v -m "not integration and not tempo"

# Run only integration tests (requires running OpenWebUI)
pytest -v -m integration

# Run only Tempo query tests (requires Grafana Cloud)
pytest -v -m tempo

# Run specific test file
pytest -v test_unit_instrumentation.py

# Run with detailed output
pytest -v -s
```

---

## 🧪 **Test Categories**

### **1. Unit Tests** (`test_unit_instrumentation.py`)

**Purpose**: Test LLM instrumentation code in isolation

**Requirements**: None (uses in-memory tracer)

**What's tested**:
- ✅ LLMSpanManager context manager
- ✅ Span creation with OpenInference attributes
- ✅ Token usage extraction
- ✅ Input/output capture and truncation
- ✅ Tool call parsing (OpenAI + OpenWebUI formats)
- ✅ Provider detection from URLs
- ✅ Ollama format conversion
- ✅ Error handling

**Run**:
```bash
pytest -v test_unit_instrumentation.py
```

**Example output**:
```
test_unit_instrumentation.py::TestLLMSpanManager::test_basic_span_creation PASSED
test_unit_instrumentation.py::TestLLMSpanManager::test_set_usage PASSED
test_unit_instrumentation.py::TestLLMSpanManager::test_set_output_with_openai_tool_calls PASSED
test_unit_instrumentation.py::TestLLMSpanManager::test_set_output_with_embedded_tool_calls PASSED
...
```

---

### **2. Integration Tests** (`test_integration_traces.py`)

**Purpose**: Test end-to-end trace creation with live OpenWebUI

**Requirements**:
- Running OpenWebUI instance (http://localhost:3000)
- Valid TEST_EMAIL and TEST_PASSWORD

**What's tested**:
- ✅ Basic LLM request creates trace
- ✅ Bot personality traces
- ✅ Tool call traces
- ✅ Streaming responses
- ✅ Multiple bot traces
- ✅ Error handling

**Run**:
```bash
# Start OpenWebUI first
cd demo
docker compose up -d

# Run integration tests
pytest -v -m integration test_integration_traces.py
```

**Example output**:
```
test_integration_traces.py::TestEndToEndTracing::test_basic_llm_trace_creation PASSED
✅ LLM request completed successfully
   Tokens used: 145

test_integration_traces.py::TestEndToEndTracing::test_bot_personality_trace PASSED
✅ Bot 'hal' responded successfully
...
```

---

### **3. Dashboard Query Tests** (`test_dashboard_queries.py`)

**Purpose**: Validate TraceQL queries used in Grafana dashboards

**Requirements**:
- GRAFANA_TEMPO_URL
- GRAFANA_TEMPO_TOKEN
- Existing traces in Tempo (run load-gen scripts first)

**What's tested**:
- ✅ Basic queries (all LLM traces, specific bots, tool calls)
- ✅ Aggregation queries (count by bot, rate, avg duration)
- ✅ Filter queries (high tokens, multiple tools, provider)
- ✅ Complex queries (multiple conditions)
- ✅ Query performance
- ✅ Attribute existence

**Run**:
```bash
# Generate some test traces first
python3 ../load-gen-bots.py
python3 ../load-gen-openai-tools-TEST.py

# Wait 30-60 seconds for traces to propagate

# Run dashboard query tests
pytest -v -m tempo test_dashboard_queries.py
```

**Example output**:
```
test_dashboard_queries.py::TestBasicQueries::test_all_llm_traces_query PASSED
✅ Query successful: All LLM traces
   Found 45 traces

test_dashboard_queries.py::TestBasicQueries::test_tool_calls_query PASSED
✅ Query successful: Traces with tool calls
   Found 12 traces with tools
...
```

---

## 🎯 **Test Markers**

Tests are organized with pytest markers:

| Marker | Description | Requirements |
|--------|-------------|--------------|
| (none) | Unit tests | None |
| `integration` | Integration tests | Running OpenWebUI |
| `tempo` | Tempo query tests | Grafana Cloud credentials |

**Run by marker**:
```bash
# Unit tests only
pytest -v -m "not integration and not tempo"

# Integration tests only
pytest -v -m integration

# Tempo tests only
pytest -v -m tempo

# Everything
pytest -v
```

---

## 📊 **Test Coverage**

### **What's Covered**

| Component | Unit Tests | Integration Tests | Query Tests |
|-----------|------------|-------------------|-------------|
| LLMSpanManager | ✅ | ✅ | - |
| Token capture | ✅ | ✅ | ✅ |
| Tool call parsing | ✅ | ✅ | ✅ |
| Bot personalities | ✅ | ✅ | ✅ |
| Provider detection | ✅ | - | ✅ |
| Input/output truncation | ✅ | - | - |
| Error handling | ✅ | ✅ | - |
| Streaming | - | ✅ | - |
| Dashboard queries | - | - | ✅ |

### **Code Coverage Report**

Generate coverage report:

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=../../backend/open_webui/utils/telemetry --cov-report=html

# Open report
open htmlcov/index.html
```

---

## 🐛 **Troubleshooting**

### **Import Errors**

If you get import errors for `open_webui` modules:

```bash
# Make sure you're running from the demo/tests directory
cd demo/tests

# Or add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../../backend"
```

### **Integration Tests Skipped**

If integration tests are skipped:

```bash
# Make sure OpenWebUI is running
docker compose -f ../docker-compose.yml ps

# Set credentials
export TEST_EMAIL="your-email@example.com"
export TEST_PASSWORD="your-password"
```

### **Tempo Tests Skipped**

If Tempo tests are skipped:

```bash
# Set Grafana Cloud credentials
export GRAFANA_TEMPO_URL="https://tempo-prod-us-east-0.grafana.net"
export GRAFANA_TEMPO_TOKEN="your-base64-token"

# Generate test data first
python3 ../load-gen-bots.py
sleep 60  # Wait for propagation
```

### **No Traces Found**

If query tests find no traces:

```bash
# Generate test traces
python3 ../load-gen.py
python3 ../load-gen-bots.py
python3 ../load-gen-openai-tools-TEST.py

# Wait for propagation
sleep 60

# Verify traces exist in Grafana UI
# Then run tests again
pytest -v -m tempo
```

---

## 📈 **Running Tests in CI/CD**

While you don't need GitHub Actions, here's how you could run tests in any CI system:

```bash
#!/bin/bash
# ci-test.sh

set -e

# 1. Start OpenWebUI stack
docker compose -f demo/docker-compose.yml up -d

# 2. Wait for services
sleep 30

# 3. Run unit tests (always pass, no deps)
pytest demo/tests/test_unit_instrumentation.py -v

# 4. Run integration tests (requires running services)
export TEST_EMAIL="test@example.com"
export TEST_PASSWORD="test-password"
pytest demo/tests/test_integration_traces.py -v -m integration

# 5. Generate test data
python3 demo/load-gen-bots.py

# 6. Wait for trace propagation
sleep 60

# 7. Run Tempo query tests (if credentials available)
if [ ! -z "$GRAFANA_TEMPO_URL" ]; then
    pytest demo/tests/test_dashboard_queries.py -v -m tempo
fi

# 8. Cleanup
docker compose -f demo/docker-compose.yml down
```

---

## 🎓 **Best Practices**

1. **Run unit tests frequently** - They're fast and don't need external dependencies
2. **Run integration tests before demos** - Ensures everything is working end-to-end
3. **Run Tempo tests after load generation** - Validates dashboard queries work
4. **Use markers to control test execution** - Skip slow tests during development
5. **Generate test data first** - Many tests need existing traces to validate

---

## 🔍 **Debugging Tests**

### **Verbose Output**

```bash
# Show print statements
pytest -v -s

# Show fixture setup
pytest -v --setup-show

# Stop on first failure
pytest -v -x
```

### **Run Single Test**

```bash
# Run specific test
pytest -v test_unit_instrumentation.py::TestLLMSpanManager::test_basic_span_creation

# Run specific test class
pytest -v test_unit_instrumentation.py::TestLLMSpanManager
```

### **Debug with pdb**

```python
# Add breakpoint in test
def test_something():
    import pdb; pdb.set_trace()
    # ... test code
```

```bash
# Run with pdb
pytest -v -s --pdb
```

---

## 📚 **Additional Resources**

- **Pytest Docs**: https://docs.pytest.org/
- **OpenTelemetry Python SDK**: https://opentelemetry-python.readthedocs.io/
- **TraceQL Docs**: https://grafana.com/docs/tempo/latest/traceql/
- **Grafana Tempo API**: https://grafana.com/docs/tempo/latest/api_docs/

---

## 💡 **Adding New Tests**

### **Add Unit Test**

```python
# In test_unit_instrumentation.py

@pytest.mark.asyncio
async def test_my_new_feature(self, in_memory_tracer):
    """Test my new feature"""
    tracer, exporter = in_memory_tracer

    async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
        # Your test logic
        pass

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    # Your assertions
```

### **Add Integration Test**

```python
# In test_integration_traces.py

@pytest.mark.integration
def test_my_integration(self, openwebui_url, auth_token):
    """Test my integration scenario"""
    response = requests.post(
        f"{openwebui_url}/api/chat/completions",
        headers={"Authorization": auth_token, "Content-Type": "application/json"},
        json={...}
    )

    assert response.status_code == 200
    # Your assertions
```

### **Add Dashboard Query Test**

```python
# In test_dashboard_queries.py

@pytest.mark.tempo
def test_my_query(self, tempo_query_helper):
    """Test my TraceQL query"""
    query = '{ span.llm.my_attribute = "value" }'
    results = tempo_query_helper(query)

    assert results is not None
    # Your assertions
```

---

**Happy Testing! 🎉**
