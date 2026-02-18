# Dashboards

This directory is reserved for exported Grafana dashboard JSON files.

## Key TraceQL Queries

Use these in Grafana Cloud Tempo (Explore > TraceQL):

```traceql
# All LLM traces
{ span.openinference.span.kind = "LLM" }

# Specific bot
{ span.llm.model_name = "hal" }

# Traces with tool calls
{ span.llm.tool_calls.count > 0 }

# Bot usage breakdown
{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name

# Token usage over time
{ span.openinference.span.kind = "LLM" } | rate(span.llm.token_count.total) by span.llm.model_name

# Average latency by bot
{ span.openinference.span.kind = "LLM" } | avg(duration) by span.llm.model_name
```

## Import / Export

**Export a dashboard:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_SA_TOKEN" \
  "https://YOUR-STACK.grafana.net/api/dashboards/uid/DASHBOARD_UID" \
  | jq '.dashboard' > dashboards/llm-observability.json
```

**Import a dashboard:**
Upload the JSON file via Grafana UI: Dashboards > New > Import > Upload JSON file.
