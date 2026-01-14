# Dashboard Fix - Quick Reference

## Problem
Two panels need fixing after instrumentation changes:
1. **Tool Usage Panel** - Old query doesn't work
2. **Model/Bot Name Panel** - Need to show which bots are being used

---

## Fix 1: Tool Usage Panel

**OLD QUERY (doesn't work):**
```traceql
{ resource.service.name = "openwebui" && span.span_type = "tool" } | count_over_time() by(span.tool.name)
```

**NEW QUERY (use this):**
```traceql
{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names
```

**Panel Type:** Time Series

**What it shows:** Tool invocation rate over time, split by tool name

---

## Fix 2: Model/Bot Name Panel

**QUERY:**
```traceql
{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name
```

**Panel Type:** Bar Gauge or Pie Chart

**What it shows:** Request count by bot (hal, glados, jarvis, marvin, bender, cortana)

---

## Available Span Attributes

| Attribute | What it contains |
|-----------|-----------------|
| `span.llm.model_name` | Bot/model name (hal, glados, jarvis, etc.) |
| `span.llm.base_model` | Underlying LLM (gemini-3-flash-preview) - only set when using bots |
| `span.llm.provider` | Provider name (gemini, openai, etc.) |
| `span.llm.tool_calls.count` | Number of tool calls |
| `span.llm.tool_calls.names` | Tool names (comma-separated) |
| `span.openinference.span.kind` | Always "LLM" for our traces |

---

## Important: Tool Call Format

OpenWebUI bots return tool calls **embedded in the content field as JSON**, not in a separate `tool_calls` field like OpenAI.

**Bot format:**
```json
{
  "content": "{\n  \"tool_calls\": [\n    {\"name\": \"pod_bay_doors\", \"parameters\": {\"action\": \"status\"}}\n  ]\n}"
}
```

**OpenAI format:**
```json
{
  "content": "...",
  "tool_calls": [
    {"function": {"name": "get_weather", "arguments": "{...}"}}
  ]
}
```

The instrumentation now handles BOTH formats by:
1. Checking for separate `tool_calls` field (OpenAI format)
2. Parsing `content` as JSON and extracting embedded `tool_calls` (bot format)
3. Converting bot format to OpenAI format for consistent processing

---

## Testing Tool Calls

**IMPORTANT**: Bot tools are only attached when using the **OpenWebUI UI**, not via direct API calls.

### To Generate Tool Call Traces:
1. **Use the UI**: Chat with bots at http://localhost:3000 (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
2. **Use test script**: `python3 load-gen-openai-tools-TEST.py` (sends explicit tool definitions)

### Load Gen Scripts:
- ✅ `load-gen-bots.py` - Generates bot traces WITHOUT tool calls (API direct)
- ✅ `load-gen-openai-tools-TEST.py` - Generates traces WITH tool calls (explicit tools)
- ✅ UI chats - Real bot tool calls (middleware attaches tools)

**Why?** OpenWebUI's middleware automatically attaches a bot's configured tools when requests come through the UI. Direct API calls don't trigger this middleware, so tools aren't included.

---

## Bonus Queries

**Most used tools (bar chart):**
```traceql
{ span.llm.tool_calls.count > 0 } | count by span.llm.tool_calls.names
```

**Tool calls by bot (table):**
```traceql
{ span.llm.tool_calls.count > 0 } | count by span.llm.model_name, span.llm.tool_calls.names
```

**Average latency by bot (bar chart):**
```traceql
{ span.openinference.span.kind = "LLM" } | avg(duration) by span.llm.model_name
```

**Bot to LLM mapping (table):**
```traceql
{ span.llm.base_model != nil } | select(span.llm.model_name, span.llm.base_model)
```

**All traces grouped by underlying LLM:**
```traceql
{ span.openinference.span.kind = "LLM" } | count by span.llm.base_model
```

---

That's it. Just update those two queries and you're good to go.
