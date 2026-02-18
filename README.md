# LLM Observability Demo (Open WebUI Fork)

Instrumented fork of [Open WebUI](https://github.com/open-webui/open-webui) with OpenTelemetry tracing for LLM observability. Traces are exported to Grafana Cloud Tempo using OpenInference semantic conventions.

**6 bot personalities** | **3 LLM providers** | **39 custom tool functions** | **OpenInference-compliant traces**

<p>
<img src="demo/docs/images/openwebui-dashboard-screenshot1.png" width="48%" alt="Grafana Dashboard" />
<img src="demo/docs/images/openwebui-chatbot-screenshot2.png" width="48%" alt="OpenWebUI Chatbot" />
</p>

## Get Started

```bash
cd demo/
cp .env.example .env     # Add OpenAI, Anthropic, Gemini + Grafana Cloud creds
make start               # Preflight, docker compose up, bots configured
```

Then open http://localhost:3000 and chat with HAL 9000, Marvin, Bender, GLADOS, JARVIS, or Cortana.

See **[demo/README.md](demo/README.md)** for full setup instructions, Makefile targets, and architecture details.

## What's Different From Upstream

This fork adds two files to the Open WebUI codebase:

| File | Change |
|------|--------|
| `backend/open_webui/routers/openai.py` | **Modified** — LLMSpanManager wrapper around chat completions |
| `backend/open_webui/utils/telemetry/llm_instrumentation.py` | **Added** — OpenInference span manager |

Everything else lives in the `demo/` directory and doesn't touch upstream code.

## Architecture

```
User Browser (localhost:3000)
    → OpenWebUI (instrumented with LLMSpanManager)
        → OpenAI API (HAL → gpt-4o, JARVIS → gpt-4o-mini)
        → LiteLLM Proxy → Anthropic API (Marvin → Sonnet, Bender → Haiku)
        → Gemini API (GLADOS → gemini-3-pro, Cortana → gemini-3-flash)
        → OTEL Collector (tail sampling, LLM spans only)
            → Grafana Cloud Tempo
```

## Quick Reference

| Command | What it does |
|---------|-------------|
| `make start` | Full automated startup |
| `make test` | Run BATS preflight + smoke tests |
| `make load-gen` | Generate 33 bot trace requests |
| `make stop` | Stop containers |
| `make clean` | Stop + remove volumes |

Run all commands from the `demo/` directory.

---

> **Note**: This is a fork of [open-webui/open-webui](https://github.com/open-webui/open-webui). For upstream documentation, see [docs.openwebui.com](https://docs.openwebui.com/).
