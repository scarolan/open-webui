# Tool Call Instrumentation Update - 2026-01-13

## Summary

Enhanced OpenInference instrumentation to explicitly capture tool/function calls from LLM responses as separate span attributes, making it easier to query and visualize tool usage in Grafana dashboards.

---

## Changes Made

### 1. Enhanced LLM Instrumentation (`/backend/open_webui/utils/telemetry/llm_instrumentation.py`)

**Added `set_tool_calls()` method** to extract and set tool call attributes:

```python
def set_tool_calls(self, tool_calls: Optional[list]):
    """Capture tool calls from LLM response"""
    # Extracts tool names and arguments
    # Sets span attributes:
    #   - llm.tool_calls.count (int)
    #   - llm.tool_calls.names (comma-separated string)
    #   - llm.tool_calls.0.name, llm.tool_calls.1.name, etc. (up to 5)
    #   - llm.tool_calls.0.arguments (truncated to 500 chars)
```

**Updated `set_output()` method** to accept optional `tool_calls` parameter:

```python
def set_output(self, content: Optional[str], tool_calls: Optional[list] = None):
    """Capture output response from LLM

    Args:
        content: LLM response text
        tool_calls: Optional list of tool calls from the response
    """
```

### 2. Updated OpenAI Router (`/backend/open_webui/routers/openai.py`)

**Non-streaming responses** - Extract tool_calls from message:

```python
if "message" in choice:
    message = choice["message"]
    content = message.get("content", "")
    tool_calls = message.get("tool_calls")
    llm_span.set_output(content, tool_calls=tool_calls)
```

**Streaming responses** - Accumulate tool_calls from delta:

```python
async def llm_stream_handler():
    accumulated_content = ""
    accumulated_tool_calls = []

    # Parse SSE chunks
    if "tool_calls" in delta:
        accumulated_tool_calls.extend(delta["tool_calls"])

    # Set at end of stream
    llm_span.set_output(accumulated_content, tool_calls=accumulated_tool_calls)
```

### 3. Updated Dashboard Guide (`/demo/GRAFANA_DASHBOARD_GUIDE.md`)

**Added new span attributes section:**

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `llm.tool_calls.count` | int | `2` | Number of tool calls in the response |
| `llm.tool_calls.names` | string | `"get_weather,search_web"` | Comma-separated list of tool names |
| `llm.tool_calls.0.name` | string | `"get_weather"` | First tool call name |
| `llm.tool_calls.0.arguments` | string | `{"location":"San Francisco"}` | First tool call arguments (truncated to 500 chars) |

**Added TraceQL query examples:**

```traceql
# All requests with tool calls
{ span.llm.tool_calls.count > 0 }

# Requests with specific tool
{ span.llm.tool_calls.names =~ ".*get_weather.*" }

# Tool usage count over time
{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names

# Most used tools
{ span.llm.tool_calls.count > 0 } | count by span.llm.tool_calls.names

# Tool calls by bot
{ span.llm.tool_calls.count > 0 } | count by span.llm.model_name, span.llm.tool_calls.names
```

**Added dashboard panel ideas:**
- Panel 8: Tool Call Tracking Over Time (time series by tool name)
- Panel 8b: Tool Call Details (table showing which bots use which tools)

---

## Answering Your Questions

### Q1: How to extract bot names?

**Answer:** Bot names are captured in `span.llm.model_name`

**Query to list all bots:**
```traceql
{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name
```

**Query for specific bot:**
```traceql
{ span.llm.model_name = "hal" }
```

**Panel visualization:**
- Bar gauge showing request count by bot
- Time series showing bot activity over time
- Table showing bot usage stats

### Q2: How to query tool usage?

**Old query (won't work):**
```traceql
{ resource.service.name = "openwebui" && span.span_type = "tool" } | count_over_time() by(span.tool.name)
```

**New query (correct):**
```traceql
{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names
```

**Why it changed:**
- We don't create separate spans for each tool call (span_type = "tool")
- Instead, we capture tool calls as attributes on the LLM span
- This is more efficient and follows OpenInference conventions

**Additional tool queries:**
```traceql
# Most used tools (bar chart)
{ span.llm.tool_calls.count > 0 } | count by span.llm.tool_calls.names

# Tools by bot (stacked bar chart)
{ span.llm.tool_calls.count > 0 } | count by span.llm.model_name, span.llm.tool_calls.names

# Multi-tool calls (complex agent behavior)
{ span.llm.tool_calls.count > 1 }
```

---

## Dashboard Recommendations

### Panel 1: Bot Activity
**Type:** Bar Gauge
**Query:** `{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name`
**Shows:** Which bots are most active

### Panel 2: Tool Usage Over Time
**Type:** Time Series
**Query:** `{ span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names`
**Shows:** Tool invocation rate over time, grouped by tool name

### Panel 3: Bot-Tool Matrix
**Type:** Table
**Query:** `{ span.llm.tool_calls.count > 0 } | select(span.llm.model_name, span.llm.tool_calls.names, span.llm.tool_calls.count)`
**Shows:** Which bots use which tools and how often

### Panel 4: Average Latency by Bot
**Type:** Bar Chart
**Query:** `{ span.openinference.span.kind = "LLM" } | avg(duration) by span.llm.model_name`
**Shows:** Performance comparison across bots

---

## Testing

After the container rebuild completes, generate some load:

```bash
cd /home/scarolan/git_repos/open-webui/demo
python3 load-gen-bots.py
```

Then in Tempo, run these queries to verify:

```traceql
# Check bot names are captured
{ span.openinference.span.kind = "LLM" } | by span.llm.model_name

# Check tool calls are captured
{ span.llm.tool_calls.count > 0 }

# Inspect a single trace with tool calls
{ span.llm.tool_calls.count > 0 } | limit 1
```

---

## Compatibility

**OpenInference Compliant:** Yes, follows semantic conventions for LLM observability

**Works with:**
- Grafana Tempo (TraceQL)
- Arize Phoenix (OpenInference native)
- Any OpenTelemetry-compatible tracing backend

**Response formats supported:**
- OpenAI-compatible APIs (OpenAI, Gemini, Azure OpenAI)
- Streaming and non-streaming responses
- Multiple tool calls per response (up to 5 tracked individually)

---

**Last Updated:** 2026-01-13
**Version:** v1.1 (Tool Call Enhancement)
