# Technical Reference

Deep-dive for anyone who wants to understand or replicate the instrumentation.

---

## Architecture

```
User Browser (localhost:3000)
    -> OpenWebUI (instrumented with OpenTelemetry)
        -> OpenAI API (HAL -> gpt-4o, JARVIS -> gpt-4o-mini)
        -> LiteLLM Proxy -> Anthropic API (Marvin -> Sonnet 4.5, Bender -> Haiku 4.5)
        -> Gemini API (GLADOS -> gemini-pro-latest, Cortana -> gemini-flash-latest)
        -> OTEL Collector (tail sampling, keeps only LLM spans)
            -> Grafana Cloud Tempo
```

---

## What We Instrumented

Only **2 files** were touched in the upstream Open WebUI codebase:

### 1. New: `backend/open_webui/utils/telemetry/llm_instrumentation.py` (~410 lines)

`LLMSpanManager` — async context manager that wraps every LLM API call. Creates a CLIENT span with OpenInference attributes:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `openinference.span.kind` | Always `"LLM"` | `"LLM"` |
| `llm.model_name` | Bot name or model | `"hal"` |
| `llm.base_model` | Underlying LLM | `"gpt-4o"` |
| `llm.provider` | Auto-detected from URL | `"openai"` |
| `llm.token_count.prompt` | Input tokens | `150` |
| `llm.token_count.completion` | Output tokens | `200` |
| `llm.token_count.total` | Total tokens | `350` |
| `llm.tool_calls.count` | Tools invoked | `2` |
| `llm.tool_calls.names` | Comma-separated names | `"pod_bay_doors"` |
| `llm.tool_calls.0.name` | First tool name | `"pod_bay_doors"` |
| `llm.input.message` | User prompt (truncated 1000 chars) | `"Open the pod bay doors"` |
| `llm.output.message` | LLM response (truncated 1000 chars) | `"I'm sorry Dave..."` |

### 2. Modified: `backend/open_webui/routers/openai.py` (~50 lines)

Wrapped `generate_chat_completion()` with `LLMSpanManager`. Handles both streaming and non-streaming responses.

```python
with LLMSpanManager(model=model_name, base_model=base_model_id, provider=provider) as llm_span:
    llm_span.set_input(payload.get("messages", []))
    async with session.post(url=url, json=payload, headers=headers) as r:
        response_data = await r.json()
        llm_span.set_usage(response_data.get("usage"))
        llm_span.set_output(...)
        llm_span.set_tool_calls(...)
```

**Total impact**: <0.5% of codebase, zero breaking changes, <5ms overhead per request.

---

## Tool Call Parsing

OpenWebUI has TWO tool call formats. The instrumentation handles both:

**OpenAI standard** (from API load gen):
```json
{"tool_calls": [{"function": {"name": "get_weather", "arguments": "{...}"}}]}
```

**OpenWebUI embedded** (from UI bot chats — tools embedded in content as JSON):
```json
{"content": "{\"tool_calls\": [{\"name\": \"pod_bay_doors\", \"parameters\": {\"action\": \"status\"}}]}"}
```

The `_convert_embedded_tool_calls()` method normalizes OpenWebUI format to OpenAI format so dashboards see consistent data.

**Important**: Bot tools only fire through the UI. Direct API calls (`/api/chat/completions`) don't trigger the middleware that attaches tools. Use `load-gen-openai-tools-TEST.py` for API-based tool traces.

---

## OTEL Collector Configuration

`demo/otel-collector-config.yaml` — Tail sampling keeps only traces containing LLM spans or errors:

```yaml
tail_sampling:
  decision_wait: 30s       # Wait for all spans in a trace to arrive
  num_traces: 100000
  policies:
    - name: keep-llm-spans-only
      type: string_attribute
      string_attribute:
        key: openinference.span.kind
        values: ["LLM"]
    - name: keep-errors
      type: status_code
      status_codes: [ERROR]
```

The 30s `decision_wait` balances latency vs completeness. Spans from both fast models (<10s) and thinking models (2-3 min) arrive at the collector at the same time (when the response completes), so 30s is enough buffer for batch delivery.

---

## Cost Calculation

The dashboard calculates estimated cost per bot using blended $/M token rates (1:2 input:output ratio):

| Bot | Provider | Model | Blended $/M |
|-----|----------|-------|-------------|
| HAL 9000 | OpenAI | gpt-4o | $7.50 |
| JARVIS | OpenAI | gpt-4o-mini | $0.45 |
| Marvin | Anthropic | claude-sonnet-4-5 | $11.00 |
| Bender | Anthropic | claude-haiku-4-5 | $3.67 |
| GLADOS | Google | gemini-pro-latest | $8.67 |
| Cortana | Google | gemini-flash-latest | $2.17 |

Cost variance comes from two layers:
1. **Model pricing** — Sonnet costs 24x more per token than gpt-4o-mini
2. **Personality verbosity** — Marvin averages ~1,100 tokens/response, JARVIS ~350

---

## TraceQL Queries

```traceql
# All LLM traces
{ span.openinference.span.kind = "LLM" }

# Specific bot
{ span.llm.model_name = "hal" }

# By provider
{ span.llm.provider = "anthropic" }

# Traces with tool calls
{ span.llm.tool_calls.count > 0 }

# Expensive conversations (>1000 tokens)
{ span.llm.token_count.total > 1000 }

# Request rate by bot
{ resource.service.name = "openwebui" && span.span_type = "llm" } | rate() by(span.llm.model_name)

# Token usage by bot
{ span.openinference.span.kind = "LLM" } | sum_over_time(span.llm.token_count.total) by(span.llm.model_name)

# Provider breakdown
{ span.openinference.span.kind = "LLM" } | count_over_time() by(span.llm.provider)

# Tool usage
{ span.llm.tool_calls.0.name != nil } | count_over_time() by(span.llm.tool_calls.0.name)

# Bot-to-model mapping
{ span.llm.base_model != nil } | select(span.llm.model_name, span.llm.base_model)
```

---

## Dashboard Panel Fix Reference

If tool or bot panels break after instrumentation changes:

**Tool Usage Panel:**
```traceql
# Old (broken): { span.span_type = "tool" } | count_over_time() by(span.tool.name)
# New (correct): { span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names
```

**Bot Name Panel:**
```traceql
{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name
```

---

## Key Design Decisions

- **OpenInference conventions** — Vendor-neutral standard, compatible with Arize, Phoenix, Langfuse
- **Direct instrumentation** (not auto) — OpenWebUI uses custom HTTP calls, needs OpenWebUI-specific tool parsing
- **Tail sampling** (not head) — Only forward traces with LLM spans, filters 90%+ noise
- **OTEL Collector** (not Alloy) — This demo IS about OpenTelemetry, so we use the native collector
- **LiteLLM proxy** — Only Anthropic needs it; OpenAI and Gemini support OpenAI-compatible endpoints natively
- **Truncation** — I/O limited to 1000 chars to prevent span bloat

---

## Testing

```bash
cd demo
make test                      # BATS preflight + smoke
make test-telemetry            # Tracing pipeline checks
make test-unit                 # Pytest unit tests
make test-integration          # Integration tests (requires running stack)
```

See `demo/tests/README.md` for detailed test documentation.

---

## Syncing with Upstream

This fork touches only 2 upstream files. To sync:

```bash
git remote add upstream https://github.com/open-webui/open-webui.git
git fetch upstream
git merge upstream/main
# Only openai.py may need conflict resolution
```

---

## Resources

- [OpenInference Spec](https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md)
- [TraceQL Docs](https://grafana.com/docs/tempo/latest/traceql/)
- [Grafana OTLP Setup](https://grafana.com/docs/grafana-cloud/send-data/otlp/send-data-otlp/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Open WebUI Docs](https://docs.openwebui.com/)
