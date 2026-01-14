# OpenWebUI LLM Observability Demo

> **Instrumented OpenWebUI fork with OpenTelemetry tracing for LLM observability**

This demo showcases OpenInference-compliant LLM observability using OpenWebUI with bot personalities and tool calls. Traces are exported to Grafana Cloud Tempo for visualization.

## 🎯 What This Demo Shows

- **LLM Request Tracing**: Capture every LLM API call with full context
- **Token Usage Tracking**: Monitor prompt, completion, and total tokens
- **Tool Call Instrumentation**: Track which tools/functions are invoked
- **Bot Personality Tracking**: Distinguish between different AI personalities (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
- **Multi-Format Support**: Handles both OpenAI tool format AND OpenWebUI embedded format
- **Grafana Cloud Integration**: Real-time dashboards in Tempo

---

## 📋 Prerequisites

- **Docker** & **Docker Compose** installed
- **Gemini API Key**: [Get one here](https://aistudio.google.com/app/apikey)
- **Grafana Cloud Account**: [Free tier available](https://grafana.com/auth/sign-up/create-user)
- **Grafana Cloud OTLP Credentials**: Configure in Settings → Connections → OpenTelemetry

---

## 🚀 Quick Start (5 minutes)

### 1. Clone This Fork

```bash
git clone https://github.com/YOUR-USERNAME/open-webui.git
cd open-webui/demo
```

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Fill in:
- `GEMINI_API_KEY`: Your Gemini API key
- `GRAFANA_OTLP_TOKEN`: Base64-encoded `instance_id:token` (see below)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Your Grafana Cloud OTLP endpoint

**Getting OTLP credentials:**
1. Go to your Grafana Cloud stack
2. Navigate to **Settings → Connections → Add Connection**
3. Select **OpenTelemetry (OTLP)**
4. Copy the endpoint URL and generate a token
5. Encode: `echo -n "INSTANCE_ID:TOKEN" | base64`

### 3. Start the Stack

```bash
docker compose up -d
```

Wait ~30 seconds for services to start, then open:
- **OpenWebUI**: http://localhost:3000
- **Sign up**: Create an account (first user becomes admin)

### 4. Test It Out

1. **Chat with bots**: Select HAL, Marvin, or Bender and send a message
2. **Watch tools fire**: You'll see superscript indicators when bots use tools
3. **Check Grafana**: Wait 30-60 seconds, then search Tempo for traces

---

## 🔍 Understanding the Instrumentation

### What Gets Captured

Every LLM API call creates a trace with:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `span.llm.model_name` | Bot or model name | `hal`, `marvin`, `gemini-2.0-flash-exp` |
| `span.llm.base_model` | Underlying LLM (for bots) | `gemini-3-flash-preview` |
| `span.llm.provider` | LLM provider | `gemini`, `openai`, `anthropic` |
| `span.llm.token_count.prompt` | Input tokens | `150` |
| `span.llm.token_count.completion` | Output tokens | `200` |
| `span.llm.token_count.total` | Total tokens | `350` |
| `span.llm.tool_calls.count` | Number of tools invoked | `2` |
| `span.llm.tool_calls.names` | Comma-separated tool list | `pod_bay_doors,run_diagnostics` |
| `span.llm.tool_calls.0.name` | First tool name | `pod_bay_doors` |
| `span.llm.tool_calls.0.arguments` | Tool arguments (truncated) | `{"action": "status"}` |
| `span.llm.input.message` | User prompt (truncated to 1000 chars) | `"HAL, open the pod bay doors"` |
| `span.llm.output.message` | LLM response (truncated to 1000 chars) | `"I'm sorry Dave..."` |

### Tool Call Formats Supported

**1. OpenAI Format** (when tools are explicitly passed):
```json
{
  "tool_calls": [
    {
      "function": {"name": "get_weather", "arguments": "{...}"},
      "type": "function"
    }
  ]
}
```

**2. OpenWebUI Bot Format** (embedded in content):
```json
{
  "content": "{\"tool_calls\": [{\"name\": \"pod_bay_doors\", \"parameters\": {...}}]}"
}
```

The instrumentation automatically detects and parses both formats!

---

## 📊 Grafana Dashboard Queries

### Basic Queries

**All LLM traces:**
```traceql
{ span.openinference.span.kind = "LLM" }
```

**Specific bot:**
```traceql
{ span.llm.model_name = "hal" }
```

**Traces with tool calls:**
```traceql
{ span.llm.tool_calls.count > 0 }
```

### Dashboard Panel Queries

**Bot Usage (Bar Gauge):**
```traceql
{ span.openinference.span.kind = "LLM" }
| count by span.llm.model_name
```

**Tool Usage Over Time (Time Series):**
```traceql
{ span.llm.tool_calls.count > 0 }
| count_over_time() by span.llm.tool_calls.names
```

**Individual Tool Breakdown (Bar Chart):**
```traceql
{ span.llm.tool_calls.0.name != nil }
| rate() by span.llm.tool_calls.0.name
```

**Token Usage by Bot (Time Series):**
```traceql
{ span.openinference.span.kind = "LLM" }
| rate(span.llm.token_count.total) by span.llm.model_name
```

**Average Latency by Bot (Bar Chart):**
```traceql
{ span.openinference.span.kind = "LLM" }
| avg(duration) by span.llm.model_name
```

See [DASHBOARD_FIX_SUMMARY.md](./DASHBOARD_FIX_SUMMARY.md) for complete query reference.

---

## 🤖 Bot Personalities

The demo includes 6 pre-configured bot personalities, each with custom tools:

| Bot | Personality | Tools |
|-----|-------------|-------|
| **HAL 9000** | Ominous spaceship AI | `pod_bay_doors`, `run_diagnostics`, `check_mission_status`, `voice_stress_analysis` |
| **Marvin** | Depressed robot | `brain_utilization`, `calculate_meaninglessness`, `probability_of_doom`, `share_complaint` |
| **Bender** | Alcoholic robot | `insult_generator`, `steal_stuff`, `brew_beer`, `bend_things` |
| **GLADOS** | Sadistic test AI | `neurotoxin_status`, `test_chamber_control`, `deploy_turrets`, `cake_management` |
| **JARVIS** | Tony Stark's AI | `suit_diagnostics`, `power_analysis`, `threat_assessment`, `reroute_power` |
| **Cortana** | Halo tactical AI | `scan_covenant`, `spartan_vitals`, `structural_analysis`, `tactical_assessment` |

---

## 🧪 Testing & Load Generation

### Load Gen Scripts

**Purpose**: Generate test traces for dashboard development

| Script | Description | Tool Calls? |
|--------|-------------|-------------|
| `load-gen-bots.py` | Queries real bots via API | ❌ No (tools only attach via UI) |
| `load-gen-openai-tools-TEST.py` | Sends explicit tool definitions | ✅ Yes (generic tools) |

### Important: Tool Call Limitation

**Bot tools ONLY attach when using the OpenWebUI UI**, not via direct API calls. This is because OpenWebUI's middleware automatically injects a bot's tools during the UI request flow.

**To generate real tool call traces:**
1. ✅ **Use the UI**: Chat with bots at http://localhost:3000
2. ✅ **Use test script**: `python3 load-gen-openai-tools-TEST.py` (generic tools)
3. ❌ **Direct API**: Won't include bot-specific tools

### Running Load Gen

```bash
# Bot traces without tools (good for bot name/token tracking)
python3 load-gen-bots.py

# Generic tool call traces (for testing tool instrumentation)
python3 load-gen-openai-tools-TEST.py
```

---

## 🔧 Architecture

### Stack Components

```
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                           │
│                    http://localhost:3000                     │
└───────────────────────────────┬─────────────────────────────┘
                                │
                ┌───────────────▼───────────────┐
                │   OpenWebUI (Instrumented)    │
                │  - Bot personalities          │
                │  - Tool management            │
                │  - OTEL instrumentation       │
                └───────────────┬───────────────┘
                                │
                ┌───────────────▼───────────────┐
                │    Gemini API (Google)        │
                │  - gemini-3-flash-preview     │
                └───────────────┬───────────────┘
                                │
                                │ OTLP/gRPC
                                │
                ┌───────────────▼───────────────┐
                │  Grafana Cloud (Tempo)        │
                │  - Trace storage              │
                │  - TraceQL queries            │
                │  - Dashboards                 │
                └───────────────────────────────┘
```

### Instrumentation Flow

1. **User sends message** → OpenWebUI UI
2. **Middleware attaches bot tools** (if using bot)
3. **LLMSpanManager starts span** → Sets bot name, provider
4. **HTTP request to Gemini** → aiohttp auto-instrumented
5. **Response parsed** → Extracts tokens, tool calls (both formats)
6. **Span attributes set** → All OpenInference fields
7. **Span exported to Tempo** → Via OTLP gRPC

---

## 📁 Key Files Modified

### Instrumentation Core
- **`backend/open_webui/utils/telemetry/llm_instrumentation.py`**: LLM span manager with OpenInference attributes
- **`backend/open_webui/routers/openai.py`**: Main chat endpoint with span creation

### Configuration
- **`docker-compose.yml`**: Stack definition with OTEL config
- **`.env.example`**: Template for credentials

### Documentation
- **`demo/README.md`**: This file
- **`demo/DASHBOARD_FIX_SUMMARY.md`**: TraceQL query reference
- **`demo/GRAFANA_DASHBOARD_GUIDE.md`**: Dashboard setup guide

### Testing
- **`demo/load-gen-bots.py`**: Bot load generator
- **`demo/load-gen-openai-tools-TEST.py`**: Tool call test generator

---

## 🐛 Troubleshooting

### No Traces Appearing in Tempo

1. **Check OTLP endpoint**: Ensure endpoint URL is correct in `.env`
2. **Verify token**: Test with `echo $GRAFANA_OTLP_TOKEN | base64 -d`
3. **Check container logs**: `docker logs openwebui-instrumented`
4. **Wait longer**: Initial export can take 60-90 seconds
5. **Test query**: `{ resource.service.name = "openwebui" }`

### Tool Calls Not Showing Up

1. **Use the UI**: Tool calls ONLY work through the UI, not API
2. **Check bot has tools**: Go to Admin → Tools, verify bot has tools assigned
3. **Look for debug logs**: `docker logs openwebui-instrumented | grep "🔍\|✅ Found embedded"`
4. **Verify query**: `{ span.llm.tool_calls.count > 0 }`

### Container Won't Start

1. **Check port 3000**: `ss -tulpn | grep :3000`
2. **Remove old containers**: `docker compose down && docker compose up -d`
3. **Check environment**: `docker compose config` to validate .env

### Dashboard Shows "No Data"

1. **Check time range**: Ensure dashboard covers last 5-15 minutes
2. **Test simple query**: `{ span.openinference.span.kind = "LLM" }` in Explore
3. **Verify attributes exist**: Look at a single trace to see what attributes are set
4. **Check for typos**: Attribute names are case-sensitive

---

## 🎓 Learning Resources

- **OpenInference Spec**: https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md
- **TraceQL Docs**: https://grafana.com/docs/tempo/latest/traceql/
- **Grafana OTLP Setup**: https://grafana.com/docs/grafana-cloud/send-data/otlp/send-data-otlp/
- **OpenTelemetry Python**: https://opentelemetry.io/docs/languages/python/

---

## 💡 Demo Tips

### For Customer Demos

1. **Start with bot chat**: Show different personalities responding
2. **Highlight tool indicators**: Point out the superscript tool calls
3. **Switch to Grafana**: Show trace appearing 30s later
4. **Drill down**: Show token counts, tool calls, latency
5. **Show dashboard**: Pre-built panels showing patterns

### Key Talking Points

- ✅ **Zero code changes for basic tracing** (if using standard OTEL)
- ✅ **Rich context capture** (tokens, tools, I/O)
- ✅ **Works with any LLM provider** (Gemini, OpenAI, Anthropic, etc.)
- ✅ **OpenInference standard** (portable to other observability tools)
- ✅ **Production-ready** (tail sampling, attribute limits, error handling)

---

## 🤝 Contributing

This is a demo fork. For production use:
1. Fork from latest `open-webui/open-webui`
2. Cherry-pick instrumentation commits
3. Add your own bot personalities
4. Customize dashboards for your use case

---

## 📄 License

This fork maintains the original OpenWebUI license (MIT). See main repo for details.

---

## 🙋 Support

- **OpenWebUI Issues**: https://github.com/open-webui/open-webui/issues
- **Grafana Cloud Support**: https://grafana.com/support/
- **This Fork**: File issues in your fork's repo

---

**Built with ❤️ for Grafana Solutions Engineers**
