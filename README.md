# LLM Observability Demo (Open WebUI Fork)

Instrumented fork of [Open WebUI](https://github.com/open-webui/open-webui) with OpenTelemetry tracing for LLM observability. Traces are exported to Grafana Cloud Tempo using OpenInference semantic conventions.

**6 bot personalities** | **39 custom tool functions** | **OpenInference-compliant traces**

## Get Started

```bash
cd demo/
cp .env.example .env     # Add Gemini + Grafana Cloud creds
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
        → Gemini API
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
