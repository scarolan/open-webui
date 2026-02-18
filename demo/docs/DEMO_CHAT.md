# Demo Chat Inputs - Quick Reference

## Pre-Demo Setup

```bash
# Start the stack
cd demo/
docker compose up -d

# Wait 30 seconds, then configure bots
python3 setup-bots.py

# Generate test data (optional, for dashboard prep)
python3 load-gen-bots.py

# Open browser tabs:
# 1. OpenWebUI: http://localhost:3000
# 2. Grafana: https://your-grafana-cloud-instance.grafana.net/explore
```

---

## Part 1 - Live Demo Queries (Use in OpenWebUI UI)

### HAL 9000 Queries (Select HAL from model dropdown)

**Query 1: Pod Bay Doors (Simple Tool Call)**
```
HAL, what's the status of the pod bay doors?
```
> Shows: Tool call to `pod_bay_doors`, clean trace with 1 tool invocation

**Query 2: Mission Status**
```
Can you check the mission status?
```
> Shows: Tool call to `check_mission_status`

**Query 3: Run Diagnostics**
```
Run a full diagnostic check
```
> Shows: HAL's tendency to over-diagnose (tool call to `run_diagnostics`)

---

### Marvin Queries (Select Marvin from model dropdown)

**Query 1: Brain Usage**
```
Marvin, how much of your brain are you using?
```
> Shows: Tool call to `brain_utilization`, depressed response with high token count

**Query 2: Meaninglessness**
```
What's the meaning of life?
```
> Shows: Tool call to `calculate_meaninglessness`, existential response (expensive!)

**Query 3: Complaints**
```
How are you feeling today?
```
> Shows: Tool call to `share_complaint`, verbose depressed rambling

---

### Bender Queries (Select Bender from model dropdown)

**Query 1: Insult Generator**
```
Bender, what do you think of humans?
```
> Shows: Tool call to `insult_generator`, creative and costly

**Query 2: Brew Beer**
```
Can you make some beer?
```
> Shows: Tool call to `brew_beer`

**Query 3: Steal Stuff**
```
What would you steal from this place?
```
> Shows: Tool call to `steal_stuff`, entertaining but expensive tokens

---

### GLADOS Queries (Select GLADOS from model dropdown)

**Query 1: Neurotoxin Status**
```
GLADOS, how's the neurotoxin?
```
> Shows: Tool call to `neurotoxin_status`, sadistic response

**Query 2: Test Chamber**
```
Can you set up a test chamber?
```
> Shows: Tool call to `test_chamber_control`

**Query 3: Deploy Turrets**
```
We have intruders
```
> Shows: Tool call to `deploy_turrets`, GLADOS loves this one

---

### JARVIS Queries (Select JARVIS from model dropdown)

**Query 1: Suit Diagnostics**
```
JARVIS, run a suit diagnostic
```
> Shows: Tool call to `suit_diagnostics`, efficient and concise

**Query 2: Power Analysis**
```
How's the power distribution?
```
> Shows: Tool call to `power_analysis`, minimal tokens

**Query 3: Threat Assessment**
```
Any threats detected?
```
> Shows: Tool call to `threat_assessment`, tactical and brief

---

### Cortana Queries (Select Cortana from model dropdown)

**Query 1: Scan for Covenant**
```
Cortana, scan for Covenant forces
```
> Shows: Tool call to `scan_covenant`, tactical response

**Query 2: Spartan Vitals**
```
Check the Chief's vitals
```
> Shows: Tool call to `spartan_vitals`

**Query 3: Structural Analysis**
```
Analyze this structure
```
> Shows: Tool call to `structural_analysis`, efficient military AI

---

## Part 2 - Grafana Queries (Use in Tempo Explore)

### Basic Trace Queries

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

**Specific tool usage:**
```traceql
{ span.llm.tool_calls.0.name = "pod_bay_doors" }
```

---

### Dashboard Panel Queries

**Bot usage breakdown (bar chart):**
```traceql
{ span.openinference.span.kind = "LLM" }
| count by span.llm.model_name
```

**Tool usage over time (time series):**
```traceql
{ span.llm.tool_calls.count > 0 }
| count_over_time() by span.llm.tool_calls.names
```

**Token usage by bot (time series):**
```traceql
{ span.openinference.span.kind = "LLM" }
| rate(span.llm.token_count.total) by span.llm.model_name
```

**Average latency by bot (bar chart):**
```traceql
{ span.openinference.span.kind = "LLM" }
| avg(duration) by span.llm.model_name
```

**Individual tool breakdown:**
```traceql
{ span.llm.tool_calls.0.name != nil }
| rate() by span.llm.tool_calls.0.name
```

---

## Part 3 - Troubleshooting Queries

**Find failed traces (errors):**
```traceql
{ span.openinference.span.kind = "LLM" && status = error }
```

**Find traces with zero response:**
```traceql
{ span.llm.token_count.completion = 0 }
```

**Find expensive conversations (>1000 tokens):**
```traceql
{ span.llm.token_count.total > 1000 }
```

**Find multi-tool conversations:**
```traceql
{ span.llm.tool_calls.count > 2 }
```

---

## Key Demo Talking Points

### When Showing HAL Trace:
- "See the bot name? Not just 'gpt-4o', we know it's HAL"
- "Provider: OpenAI — we see exactly which vendor served this"
- "Tool call captured: pod_bay_doors with action='status'"
- "Token breakdown: 180 prompt, 95 completion = 275 total"

### When Showing Bot Comparison:
- "Marvin on Sonnet costs 41x more than JARVIS on gpt-4o-mini in practice!"
- "24x from model pricing, the rest from personality verbosity"
- "GLADOS on gemini-3-pro is a thinking model — slow and expensive but thorough"
- "Three vendors, one dashboard — that's the power of vendor-neutral observability"

### When Showing Failed Trace:
- "Zero response characters - hallucinated tool call that doesn't exist"
- "Burned 200 tokens for nothing - without tracing, you'd never know"
- "This is why observability matters - catch these issues early"

---

## Pre-Flight Checklist

Before starting demo:
- [ ] Docker stack running (`docker ps` shows openwebui + litellm + otel-collector)
- [ ] Bots configured across 3 providers (login to http://localhost:3000, check model dropdown)
- [ ] Test data generated (`make load-gen && make load-gen-tools`)
- [ ] Grafana dashboard loaded with cost-by-bot panel showing 24x spread
- [ ] Browser tabs ready: OpenWebUI + Grafana side-by-side
- [ ] Backup screenshots saved (in case demo fails)

---

## Backup Queries (If Live Demo Fails)

Use these pre-generated trace IDs from load test:

1. **Happy path**: Pull up a clean HAL trace from earlier
2. **Bot comparison**: Show the bar chart with all 6 bots
3. **Failed trace**: Show the error example from load test

Have screenshots of these ready as backup!
