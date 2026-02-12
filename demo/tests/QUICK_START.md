# Quick Start - Running Tests

**✅ Fixed and working!**

---

## 🚀 **Fastest Way to Run Tests**

```bash
cd /home/scarolan/git_repos/open-webui/demo/tests

# Run unit tests (21 tests, <1 second)
python3 runtests.py

# Run integration tests
python3 runtests.py --integration

# Run Tempo query tests
python3 runtests.py --tempo

# Run everything
python3 runtests.py --all
```

---

## 📦 **One-Time Setup** (Already Done!)

The following dependencies are already installed:
- ✅ pytest
- ✅ pytest-asyncio
- ✅ opentelemetry-api
- ✅ opentelemetry-sdk
- ✅ typer
- ✅ fastapi
- ✅ aiohttp
- ✅ uvicorn
- ✅ pydantic

---

## ✅ **Test Results**

```
============================= 21 passed in 0.13s ==============================
```

**All unit tests passing!**

What's tested:
- ✅ LLMSpanManager context manager
- ✅ Token usage capture
- ✅ Tool call parsing (OpenAI + OpenWebUI formats)
- ✅ Provider detection
- ✅ Format conversion
- ✅ Input/output truncation
- ✅ Error handling

---

## 📋 **For Integration/Tempo Tests**

Set environment variables:

```bash
# Integration tests
export TEST_EMAIL="your-email@example.com"
export TEST_PASSWORD="your-password"

# Tempo query tests
export GRAFANA_TEMPO_URL="https://tempo-prod-us-east-0.grafana.net"
export GRAFANA_TEMPO_TOKEN="your-base64-token"
```

---

## 🎯 **Quick Commands**

| Command | What It Does | Time |
|---------|--------------|------|
| `python3 runtests.py` | Run unit tests | <1s |
| `python3 runtests.py -v` | Verbose output | <1s |
| `python3 runtests.py --help` | Show help | instant |

---

**All fixed! Tests are working! 🎉**
