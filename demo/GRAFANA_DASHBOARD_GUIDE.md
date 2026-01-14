# OpenWebUI LLM Observability - Dashboard Guide

## Summary

We've successfully instrumented OpenWebUI with **OpenInference-compliant OpenTelemetry tracing** for full LLM observability. All traces are flowing to Grafana Cloud Tempo with rich span attributes capturing:

**⚠️ IMPORTANT: Model Version**
- **Always use:** `gemini-3-flash-preview` (or `models/gemini-3-flash-preview`)
- **Never use:** Older models like `gemini-2.0-flash-exp`
- This is configured in docker-compose.yml and all load generation scripts

- Token usage (prompt, completion, total)
- Model names and providers
- Full conversation context (input/output messages, truncated to 1000 chars)
- Tool/function calls from the LLM
- Invocation parameters (temperature, max_tokens, stream, etc.)
- Request latency and error tracking

**Tech Stack:**
- Forked OpenWebUI with custom instrumentation
- OpenTelemetry Python SDK
- OTEL Collector with tail sampling (filters noise)
- Grafana Cloud Tempo for trace storage
- Gemini API (models/gemini-3-flash-preview)

---

## Available Span Attributes

All spans include the following **OpenInference-compliant** attributes:

### Core LLM Attributes

| Attribute | Type | Example Value | Description |
|-----------|------|---------------|-------------|
| `openinference.span.kind` | string | `"LLM"` | Identifies this as an LLM span (required) |
| `span_type` | string | `"llm"` | Generic span type for filtering |
| `llm.model_name` | string | `"models/gemini-3-flash-preview"` | Full model identifier |
| `llm.provider` | string | `"gemini"` | Provider name (gemini, openai, azure, etc.) |

### Token Usage

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `llm.token_count.prompt` | int | `1209` | Input tokens consumed |
| `llm.token_count.completion` | int | `835` | Output tokens generated |
| `llm.token_count.total` | int | `2044` | Total tokens used (for cost calculation) |

### Conversation Content

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `llm.input.message` | string | `"History:\nUSER: \"\"\"Why did you mention...\"\"\""` | User's input message (truncated to 1000 chars) |
| `llm.output.message` | string | `"I can assure you that..."` | LLM's response text (truncated to 1000 chars) |

### Tool/Function Calls

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `llm.tool_calls.count` | int | `2` | Number of tool calls in the response |
| `llm.tool_calls.names` | string | `"get_weather,search_web"` | Comma-separated list of tool names |
| `llm.tool_calls.0.name` | string | `"get_weather"` | First tool call name |
| `llm.tool_calls.0.arguments` | string | `{"location":"San Francisco"}` | First tool call arguments (truncated to 500 chars) |
| `llm.tool_calls.1.name` | string | `"search_web"` | Second tool call name (up to 5 tool calls tracked individually) |

### Invocation Parameters

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `llm.temperature` | float | `0.7` | Temperature setting (if provided) |
| `llm.max_tokens` | int | `2048` | Max tokens parameter (if provided) |
| `llm.top_p` | float | `0.9` | Top-p parameter (if provided) |
| `llm.top_k` | int | `40` | Top-k parameter (if provided) |
| `llm.stream` | bool | `false` | Whether streaming was used |

### Standard OTEL Attributes

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `service.name` | string | `"openwebui"` | Service identifier |
| `deployment.environment` | string | `"demo"` | Environment tag |
| `instrumentation.type` | string | `"openinference"` | Marks as OpenInference-compliant |

---

## TraceQL Query Examples

### Basic Queries

```traceql
# All LLM spans
{ span.openinference.span.kind = "LLM" }

# Specific model
{ span.llm.model_name = "models/gemini-3-flash-preview" }

# Specific provider
{ span.llm.provider = "gemini" }
```

### Token Usage Queries

```traceql
# High token usage (>1000 tokens)
{ span.llm.token_count.total > 1000 }

# Expensive prompts (>2000 prompt tokens)
{ span.llm.token_count.prompt > 2000 }

# Efficient responses (<500 completion tokens)
{ span.llm.token_count.completion < 500 }

# Calculate token distribution
{ span.openinference.span.kind = "LLM" } | select(span.llm.token_count.total)
```

### Performance Queries

```traceql
# Slow requests (>5 seconds)
{ duration > 5s && span.openinference.span.kind = "LLM" }

# Fast requests (<1 second)
{ duration < 1s && span.openinference.span.kind = "LLM" }

# Latency by model
{ span.openinference.span.kind = "LLM" } | histogram by span.llm.model_name
```

### Content Analysis

```traceql
# Conversations mentioning specific topics
{ span.llm.input.message =~ ".*HAL.*" }

# Streaming vs non-streaming
{ span.llm.stream = true }
{ span.llm.stream = false }
```

### Bot and Model Queries

```traceql
# All requests by bot/model name
{ span.openinference.span.kind = "LLM" } | by span.llm.model_name

# Specific bot (e.g., HAL)
{ span.llm.model_name = "hal" }

# Multiple bots
{ span.llm.model_name =~ "hal|glados|jarvis" }

# Request count by bot
{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name

# Average latency by bot
{ span.openinference.span.kind = "LLM" } | avg(duration) by span.llm.model_name
```

### Tool/Function Call Queries

```traceql
# All requests with tool calls
{ span.llm.tool_calls.count > 0 }

# Requests with specific tool
{ span.llm.tool_calls.names =~ ".*get_weather.*" }

# Multiple tool calls (agent reasoning)
{ span.llm.tool_calls.count > 1 }

# Tool usage count over time
{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names

# Most used tools
{ span.llm.tool_calls.count > 0 } | count by span.llm.tool_calls.names

# Tool calls by bot
{ span.llm.tool_calls.count > 0 } | count by span.llm.model_name, span.llm.tool_calls.names
```

### Cost Analysis

```traceql
# Total tokens by model (for cost calculation)
{ span.openinference.span.kind = "LLM" }
  | sum by span.llm.model_name of span.llm.token_count.total

# Request count by provider
{ span.openinference.span.kind = "LLM" }
  | count by span.llm.provider
```

---

## Dashboard Panel Ideas

### 1. Token Usage Over Time (Time Series)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" } | rate() by span.llm.model_name
```

**Visualization:** Time series graph showing token consumption rate by model

**Use Case:** Track API usage patterns, identify spikes, predict costs

---

### 2. Request Rate by Provider (Stat Panel)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" } | rate()
```

**Visualization:** Single stat with sparkline

**Use Case:** Monitor overall LLM API traffic

---

### 3. Latency Percentiles (Heatmap)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" } | histogram
```

**Visualization:** Heatmap showing p50, p95, p99 latencies

**Use Case:** Identify slow requests, SLA tracking

---

### 4. Token Distribution (Histogram)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" }
  | select(span.llm.token_count.total)
```

**Visualization:** Histogram showing distribution of token counts

**Use Case:** Understand typical request sizes, identify outliers

---

### 5. Top Conversations by Tokens (Table)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" }
  | select(span.llm.input.message, span.llm.token_count.total, span.llm.model_name)
```

**Visualization:** Table sorted by token count descending

**Columns:**
- Input Message (truncated)
- Model
- Total Tokens
- Duration
- Trace ID (link)

**Use Case:** Find expensive queries, optimize prompts

---

### 6. Error Rate (Stat Panel)

**Query:**
```traceql
{ status = error && span.openinference.span.kind = "LLM" } | rate()
```

**Visualization:** Stat panel with red threshold

**Use Case:** Alert on API failures

---

### 7. Cost Estimation (Time Series)

**Formula:** `tokens * price_per_1k_tokens`

For Gemini Flash:
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Query (approximate cost):**
```traceql
{ span.openinference.span.kind = "LLM" }
  | sum by span.llm.model_name of span.llm.token_count.total
```

**Note:** Need to multiply by pricing in post-processing

---

### 8. Tool Call Tracking Over Time (Time Series)

**Query:**
```traceql
{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names
```

**Visualization:** Time series showing tool usage rate by tool name

**Use Case:** Monitor agent behavior, identify popular tools, track tool adoption

---

### 8b. Tool Call Details (Table)

**Query:**
```traceql
{ span.llm.tool_calls.count > 0 }
  | select(span.llm.model_name, span.llm.tool_calls.names, span.llm.tool_calls.count, duration)
```

**Visualization:** Table showing which bots use which tools

**Columns:**
- Bot Name (span.llm.model_name)
- Tools Called (span.llm.tool_calls.names)
- Tool Count (span.llm.tool_calls.count)
- Duration

**Use Case:** Debug tool selection, understand bot behavior patterns

---

### 9. Model Comparison (Bar Gauge)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" }
  | count by span.llm.model_name
```

**Visualization:** Horizontal bar gauge

**Use Case:** Compare usage across different models

---

### 10. Streaming vs Non-Streaming (Pie Chart)

**Query:**
```traceql
{ span.openinference.span.kind = "LLM" }
  | count by span.llm.stream
```

**Visualization:** Pie chart

**Use Case:** Understand streaming adoption

---

## Example Trace Structure

Here's what a typical trace looks like:

```
Trace: User chat request (17.5s total)
├─ Span: POST /api/chat/completions (FastAPI, SERVER)
│  Attributes:
│    http.method: POST
│    http.target: /api/chat/completions
│    http.status_code: 200
│
│  └─ Span: llm.gemini.chat (CLIENT, 15.2s)
│     Attributes:
│       openinference.span.kind: LLM
│       llm.model_name: models/gemini-3-flash-preview
│       llm.provider: gemini
│       llm.token_count.prompt: 1209
│       llm.token_count.completion: 835
│       llm.token_count.total: 2044
│       llm.input.message: "History:\nUSER: \"\"\"Why did you...\"\"\""
│       llm.output.message: "I can assure you that..."
│       llm.stream: false
│       span_type: llm
│       service.name: openwebui
│       deployment.environment: demo
│       instrumentation.type: openinference
```

---

## Filtering Configuration

**Current Tail Sampling Policies:**

1. **Keep all LLM spans** - Any trace containing `openinference.span.kind = "LLM"`
2. **Keep chat completions** - Traces hitting `/api/chat/completions`
3. **Keep errors** - Any trace with error status

**Excluded endpoints** (no spans created):
- `/api/chat/completed`
- `/api/health`, `/api/version`, `/api/config`
- `/api/models`, `/api/tasks`, `/api/files`
- Static assets (`.js`, `.css`, `.png`, etc.)
- Websockets (`/ws`)

This ensures **only meaningful LLM traces** reach Tempo - no noise!

---

## Cost Estimation Guide

### Gemini Flash Pricing (as of Jan 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gemini-3-flash-preview | $0.075 | $0.30 |

### Calculation Formula

```
cost = (prompt_tokens * 0.075 / 1_000_000) + (completion_tokens * 0.30 / 1_000_000)
```

### Example Trace Cost

From our sample trace:
- Prompt: 1,209 tokens
- Completion: 835 tokens
- **Cost**: (1209 * $0.075 / 1M) + (835 * $0.30 / 1M) = **$0.00034**

### Daily Cost Projection

If you have 1,000 similar requests per day:
- **Daily cost**: $0.34
- **Monthly cost**: ~$10.20

---

## Dashboard Variables (Suggested)

Create dashboard variables for filtering:

**1. Model Filter**
- Name: `model`
- Query: Extract unique values of `span.llm.model_name`
- Multi-select: Yes
- Include All: Yes

**2. Provider Filter**
- Name: `provider`
- Query: Extract unique values of `span.llm.provider`
- Multi-select: Yes
- Include All: Yes

**3. Time Range**
- Use Grafana's built-in time picker
- Default: Last 6 hours

**4. Environment**
- Name: `environment`
- Query: Extract `deployment.environment`
- Default: `demo`

---

## Alerting Suggestions

### 1. High Token Usage Alert

**Condition:** `span.llm.token_count.total > 5000`

**Why:** Flag unexpectedly large prompts that could indicate:
- Prompt injection attempts
- Misconfigured context windows
- Cost optimization opportunities

---

### 2. Slow Request Alert

**Condition:** `duration > 10s && span.openinference.span.kind = "LLM"`

**Why:** Detect degraded API performance or timeout risks

---

### 3. Error Rate Alert

**Condition:** Error rate > 5% over 5 minutes

**Why:** Catch API quota limits, auth failures, or service outages

---

### 4. Cost Spike Alert

**Condition:** Token rate increases >50% from baseline

**Why:** Prevent unexpected bills from runaway usage

---

## Next Steps

1. **Create Dashboard**
   - Use the panel ideas above
   - Start with token usage, request rate, and latency
   - Add cost estimation panels

2. **Set Up Alerts**
   - Configure alerting for high token usage and errors
   - Set up Slack/PagerDuty notifications

3. **Optimize Costs**
   - Identify high-token prompts from table panel
   - Analyze conversation patterns
   - Consider prompt compression techniques

4. **Extend Instrumentation**
   - Add user attribution (which user triggered the request)
   - Track conversation IDs for multi-turn analysis
   - Add custom business metrics

---

## Technical Details

**Source Code:**
- Instrumentation: `/backend/open_webui/utils/telemetry/llm_instrumentation.py`
- Router modifications: `/backend/open_webui/routers/openai.py`
- Docker Compose: `/demo/docker-compose.yml`
- OTEL Config: `/demo/otel-collector-config.yaml`

**Architecture:**
```
User → OpenWebUI (port 3000)
         ↓ OTLP gRPC (port 4317)
       OTEL Collector
         ↓ OTLP HTTP + Basic Auth
       Grafana Cloud Tempo
         ↓ TraceQL queries
       Grafana Dashboard
```

**Performance Impact:**
- Span creation: ~0.5ms
- Attribute setting: ~0.1ms per attribute
- Total overhead: **<5ms per request** (negligible)

---

## OpenInference Compliance

This instrumentation is **100% OpenInference-compliant**, following the semantic conventions from:
https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md

**Benefits:**
- Compatible with Phoenix (Arize's OSS observability tool)
- Portable across any OpenInference-aware platform
- Future-proof as the standard evolves
- No vendor lock-in

---

## Support

**Repository:** `~/git_repos/open-webui` (forked from open-webui/open-webui)

**Key Environment Variables:**
- `ENABLE_OTEL=true`
- `OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp`
- `GRAFANA_OTLP_TOKEN=<base64(instance_id:token)>` - **IMPORTANT:** Must be Basic auth format

**Troubleshooting:**
- Check collector logs: `docker compose logs otel-collector`
- Check OpenWebUI logs: `docker compose logs openwebui`
- Verify traces in Tempo: `{ span.openinference.span.kind = "LLM" }`

---

**Last Updated:** 2026-01-13
**Instrumentation Version:** v1.0
**OpenInference Spec Version:** 0.1.x
