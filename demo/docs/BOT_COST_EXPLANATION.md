# Bot Cost Analysis — Multi-Provider Edition

## The Key Insight

6 bots, 3 providers, 6 different models — and costs vary **24x** between cheapest and most expensive. This is the real power of multi-provider LLM observability: **you can't optimize what you can't see**.

---

## Bot-to-Model Mapping

| Bot | Provider | Model | Input $/M | Output $/M | Blended $/M |
|-----|----------|-------|----------|-----------|-------------|
| HAL 9000 | OpenAI | `gpt-4o` | $2.50 | $10.00 | **$7.50** |
| JARVIS | OpenAI | `gpt-4o-mini` | $0.15 | $0.60 | **$0.45** |
| Marvin | Anthropic | `claude-sonnet-4-5` | $3.00 | $15.00 | **$11.00** |
| Bender | Anthropic | `claude-haiku-4-5` | $1.00 | $5.00 | **$3.67** |
| GLADOS | Google | `gemini-3-pro` | $2.00 | $12.00 | **$8.67** |
| Cortana | Google | `gemini-3-flash` | $0.50 | $3.00 | **$2.17** |

**Blended rate** assumes a 1:2 input:output token ratio (typical for chat):

```
blended = (input_rate + output_rate * 2) / 3
```

---

## Cost Tiers

```
TIER 1 — Premium          TIER 2 — Mid             TIER 3 — Economy
$11.00/M  Marvin (Sonnet)  $3.67/M  Bender (Haiku)  $0.45/M  JARVIS (gpt-4o-mini)
$8.67/M   GLADOS (gemini-3-pro)  $2.17/M  Cortana (gemini-3-flash)
$7.50/M   HAL (gpt-4o)
```

Marvin on Sonnet costs **24x more** per token than JARVIS on gpt-4o-mini.

---

## Two Layers of Cost Variance

### Layer 1: Model Pricing (the big one)

Different models have wildly different per-token costs. Sonnet costs 24x more than gpt-4o-mini per token. This is the primary cost driver and the one most teams miss without observability.

### Layer 2: Personality Verbosity (the subtle one)

Even on the same model, different system prompts produce different response lengths:

- **JARVIS** (concise personality): ~150-200 output tokens
- **Marvin** (depressed, verbose personality): ~400-500 output tokens

Marvin's verbosity on top of Sonnet's premium pricing creates a double cost multiplier.

---

## Grafana Dashboard — Estimated Cost Panel

### Setup: 6 TraceQL Queries + 6 Math Expressions

**Queries (A through F)** — total tokens per bot:

```
A: { resource.service.name = "openwebui" && span.llm.model_name = "hal" }     | sum_over_time(span.llm.token_count.total)
B: { resource.service.name = "openwebui" && span.llm.model_name = "jarvis" }  | sum_over_time(span.llm.token_count.total)
C: { resource.service.name = "openwebui" && span.llm.model_name = "marvin" }  | sum_over_time(span.llm.token_count.total)
D: { resource.service.name = "openwebui" && span.llm.model_name = "bender" }  | sum_over_time(span.llm.token_count.total)
E: { resource.service.name = "openwebui" && span.llm.model_name = "glados" }  | sum_over_time(span.llm.token_count.total)
F: { resource.service.name = "openwebui" && span.llm.model_name = "cortana" } | sum_over_time(span.llm.token_count.total)
```

**Math Expressions (G through L)** — apply blended $/M rate:

```
G: $A * 7.50  / 1000000    # HAL     (gpt-4o)           — $7.50/M blended
H: $B * 0.45  / 1000000    # JARVIS  (gpt-4o-mini)      — $0.45/M blended
I: $C * 11.00 / 1000000    # Marvin  (claude-sonnet-4-5) — $11.00/M blended
J: $D * 3.67  / 1000000    # Bender  (claude-haiku-4-5)  — $3.67/M blended
K: $E * 8.67  / 1000000    # GLADOS  (gemini-3-pro)       — $8.67/M blended
L: $F * 2.17  / 1000000    # Cortana (gemini-3-flash)    — $2.17/M blended
```

**Total estimated cost**:

```
M: $G + $H + $I + $J + $K + $L
```

### Panel Configuration

- **Panel type**: Time series (stacked) or Bar chart
- **Show**: Expressions G–L only (hide queries A–F)
- **Legend**: Use bot names as series labels
- **Unit**: Currency (USD)
- **Color scheme**: Warm palette — expensive bots in red, cheap in green

---

## Useful TraceQL Queries

### Token usage by bot
```traceql
{ span.openinference.span.kind = "LLM" }
| avg(span.llm.token_count.total) by span.llm.model_name
```

### Token usage by provider
```traceql
{ span.openinference.span.kind = "LLM" }
| sum(span.llm.token_count.total) by span.llm.provider
```

### Compare prompt vs completion tokens
```traceql
{ span.llm.model_name = "marvin" }
| avg(span.llm.token_count.prompt)

{ span.llm.model_name = "marvin" }
| avg(span.llm.token_count.completion)
```

---

## Demo Talking Points

### The Hook
"We have 6 AI bots running on 3 different LLM providers. Can you guess which one costs the most?"

### The Reveal
"Marvin — the depressed robot — running on Claude Sonnet. He costs 24x more per token than JARVIS on gpt-4o-mini. And his personality makes him verbose, so he uses MORE tokens too. It's a double hit."

### The Insight
"Without multi-provider observability, you'd just see a high API bill split across three vendors. With OpenTelemetry traces in Tempo, you can see exactly which bot, which model, which provider is driving cost — and make informed decisions about where to optimize."

### The Takeaway
"This is why vendor-neutral observability matters. You're not locked into one provider's dashboard. One set of traces, one query language, complete visibility across OpenAI, Anthropic, and Google."

---

## Real-World Parallels

This pattern applies to any production multi-model setup:

### Model Routing
- Route simple queries to cheap models (Haiku, gpt-4o-mini)
- Route complex queries to premium models (Sonnet, gpt-4o)
- **Observability shows if your routing logic is working**

### Cost Optimization
- Identify which agents are on expensive models unnecessarily
- A/B test moving a bot from Sonnet to Haiku — does quality suffer?
- **Observability gives you before/after data**

### Provider Comparison
- Same bot, different providers — which is faster? Cheaper? Better?
- **Observability makes provider evaluation data-driven**

---

## Summary

- **3 providers**: OpenAI, Anthropic, Google Gemini
- **6 unique models**: gpt-4o, gpt-4o-mini, claude-sonnet-4-5, claude-haiku-4-5, gemini-3-pro, gemini-3-flash
- **24x cost spread**: $0.45/M (economy) to $11.00/M (premium)
- **Two cost layers**: model pricing + personality verbosity
- **One observability platform**: OpenTelemetry → Grafana Cloud Tempo

This is why **multi-provider AI observability matters** — you can't optimize what you can't measure across all your vendors.
