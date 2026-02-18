# "Your AI Has Multiple Personalities... And They're All Spending Your Money" - Lightning Talk
**10 Minutes | OpenWebUI Multi-Provider Observatory Demo | Grafana Cloud**

---

## Talk Structure (7 mins content + 3 mins Q&A)

### Slide 1: Title Slide (0:00-0:30)
**Visual**: OpenWebUI logo + Six bot avatars (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana) + Three provider logos (OpenAI, Anthropic, Google) + Grafana logo
**Title**: "Your AI Has Multiple Personalities... And They're All Spending Your Money"
**Subtitle**: "A 7-Minute Journey into Multi-Provider AI Observability with Temperamental Robots"

**Talk Track**:
> "Hey folks! Quick question - how many of you have deployed AI agents or chatbots? [pause for hands] Awesome. Now keep your hand up if you're using MORE than one LLM provider. [pause] And keep your hand up if you can tell me EXACTLY which of your agents is the most expensive to run. [pause - most hands drop] Yeah, thought so. Today I'm going to show you why multi-provider AI observability matters - using six robot personalities spread across OpenAI, Anthropic, and Google Gemini. Spoiler: the cost difference between our cheapest and most expensive bot is 24x. And without observability, you'd never know which one is burning your budget."

---

### Slide 2: The Problem (0:30-1:30)
**Visual**: Split screen - "What You Built" vs "What's Actually Happening"
- Left: Simple chatbot interface, user sends message
- Right: Chaos - three different API providers, thinking models burning tokens, fast models being efficient, no visibility

**Talk Track**:
> "So you built some AI assistants. Maybe you're using OpenAI for some, Anthropic for others, Google Gemini for the rest. Different models for different use cases. You deployed them. Users love them. Then three things happen:
>
> 1. Your cloud bill arrives and it's split across THREE vendors - and the total is... concerning
> 2. Users complain that 'GLADOS is way slower than JARVIS' - and you realize one's on a thinking model and one's on a fast model, but you have no data
> 3. Your boss asks 'Which provider should we consolidate on?' and you're just guessing
>
> Traditional observability doesn't cut it here. You can see HTTP requests, sure. You can see 'an API call went to api.openai.com.' But you CAN'T see:
> - WHICH bot personality made that call on WHICH provider
> - Whether the thinking model was worth 24x the cost of the fast one
> - Why Marvin on Claude Sonnet used 1,100 tokens to say he's depressed
> - Whether your routing to expensive vs cheap models makes sense
>
> You're flying blind across three vendor dashboards with no unified view."

---

### Slide 3: The Demo App (1:30-2:00)
**Visual**: Architecture diagram showing 3 providers + 6 bot cards with their models
- HAL 9000: OpenAI gpt-4o ($7.50/M) — pod_bay_doors, run_diagnostics
- JARVIS: OpenAI gpt-4o-mini ($0.45/M) — suit_diagnostics, threat_assessment
- Marvin: Anthropic claude-sonnet-4-5 ($11.00/M) — brain_utilization, probability_of_doom
- Bender: Anthropic claude-haiku-4-5 ($3.67/M) — insult_generator, brew_beer
- GLADOS: Google gemini-3-pro ($8.67/M) — neurotoxin_status, deploy_turrets
- Cortana: Google gemini-3-flash ($2.17/M) — scan_covenant, spartan_vitals

**Talk Track**:
> "Let me show you what we built. This is an instrumented OpenWebUI fork with six bot personalities, each on a DIFFERENT model from a DIFFERENT provider:
>
> On OpenAI: HAL 9000 on gpt-4o, JARVIS on gpt-4o-mini.
> On Anthropic via LiteLLM: Marvin the depressed robot on Claude Sonnet - our most expensive model. Bender on Claude Haiku.
> On Google: GLADOS on gemini-3-pro - a thinking model that deliberates before responding. Cortana on gemini-3-flash.
>
> Six bots, three providers, six unique models, 39 custom tool functions. The blended cost per million tokens ranges from 45 CENTS for JARVIS to ELEVEN DOLLARS for Marvin. That's a 24x spread. Let's see what that looks like in practice."

---

### Slide 4: Live Demo Part 1 - The Happy Path (2:00-3:30)
**Visual**: Screen share split - OpenWebUI chat + Grafana Tempo

**Talk Track**:
> "Let me chat with HAL on gpt-4o. I'll ask: 'HAL, what's the status of the pod bay doors?'
>
> [Type query, hit send]
>
> Watch what HAL does - see that tool call indicator? He's executing the `pod_bay_doors` function.
>
> Now flip over to Grafana. [Switch to dashboard] Look at this trace:
>
> 1. **Model Name**: `hal` - we know WHICH bot, not just 'gpt-4o made a call'
> 2. **Base Model**: `gpt-4o` — the underlying LLM
> 3. **Provider**: `openai` — which vendor served this request
> 4. **Token Usage**: 180 prompt, 95 completion = 275 total
> 5. **Tool Calls**: 1 tool invoked - `pod_bay_doors`
> 6. **Estimated Cost**: ~$0.002 for this conversation
>
> That's the happy path. But here's where it gets really interesting — the COST comparison across providers."

---

### Slide 5: Live Demo Part 2 - The Money Shot (3:30-5:00)
**Visual**: Grafana dashboard showing multi-provider cost comparison

**Talk Track**:
> "Now let's look at the data from our load test — all six bots answering similar questions. This is the estimated cost panel.
>
> [Pull up cost-by-bot panel]
>
> Look at this. Marvin on Claude Sonnet: $0.074. GLADOS on gemini-3-pro: $0.038. And JARVIS on gpt-4o-mini? $0.0018. Marvin costs FORTY TIMES what JARVIS costs. Why?
>
> Two reasons: First, model pricing. Sonnet costs $11 per million tokens. gpt-4o-mini costs 45 cents. That's the 24x multiplier right there. Second, personality. Marvin's system prompt tells him to be verbose and existential — he averages 1,100 tokens per response. JARVIS is trained to be concise — 350 tokens.
>
> [Pull up provider breakdown]
>
> And look at the provider view — Anthropic is our most expensive vendor because Marvin is on Sonnet. Google is in the middle because GLADOS is on a thinking model that deliberates before every response. OpenAI is cheapest because JARVIS is on mini.
>
> The critical insight: without vendor-neutral observability, you'd have three separate dashboards — OpenAI's usage page, Anthropic's console, Google's billing — and NO way to compare them side by side. One TraceQL query, one dashboard, complete visibility across all three."

---

### Slide 6: The Superpowers (5:00-6:00)
**Visual**: Dashboard with four key metric panels highlighted
- Cost per bot by provider (bar chart — Marvin towers over others)
- Token usage by provider (pie chart)
- Tool call patterns (time series)
- Thinking model vs fast model latency comparison

**Talk Track**:
> "So what does multi-provider AI observability actually give you? Four superpowers:
>
> 1. **Cross-Vendor Cost Attribution** - You see EXACTLY which bot on WHICH provider costs what. Marvin on Sonnet: $0.074 per session. JARVIS on gpt-4o-mini: $0.0018. That's data you can act on. Should Marvin really be on a premium thinking model? Maybe Haiku is good enough for existential depression.
>
> 2. **Thinking Model Economics** - GLADOS on gemini-3-pro thinks before responding. It's slower, it's more expensive, but is it BETTER? With traces, you can compare quality vs cost vs latency across thinking and fast models and make informed routing decisions.
>
> 3. **Tool Usage Across Providers** - Do tools work differently on different models? Does HAL on gpt-4o use tools differently than Cortana on gemini-3-flash? You can see it.
>
> 4. **Vendor-Neutral Debugging** - When something fails, you don't check three dashboards. You see: 'Bot: Marvin. Provider: Anthropic. Model: Sonnet. Input: Why are we here? Tokens: 1,100. Cost: $0.012.' One trace, complete context, regardless of provider."

---

### Slide 7: How This Actually Works (6:00-6:45)
**Visual**: Architecture diagram
- OpenWebUI → OpenAI API / LiteLLM (Anthropic) / Gemini API
- → OpenTelemetry SDK → OTEL Collector (tail sampling) → Grafana Cloud Tempo
- OpenInference semantic conventions layer

**Talk Track**:
> "Quick implementation note - this isn't magic. It's three open standards plus a lightweight proxy:
>
> 1. **OpenTelemetry SDK** - industry standard, vendor-neutral observability
> 2. **OpenInference semantic conventions** - LLM-specific attributes: model name, tokens, tool calls, provider
> 3. **LiteLLM** - translates OpenAI-format requests to Anthropic's API, so all three providers look the same to our app
> 4. **Grafana Cloud Tempo** - stores and queries traces with TraceQL
>
> The code changes? About 100 lines. We wrapped each LLM API call with a span manager that auto-detects the provider from the endpoint URL and captures everything. The OTEL Collector does tail sampling to keep only LLM spans — filters out 90% of noise.
>
> Total setup time? `make start`. Docker compose brings up OpenWebUI, LiteLLM, and the collector. One command configures all three providers and six bots."

---

### Slide 8: The Takeaway (6:45-7:30)
**Visual**: Three key points with icons
- 24x cost spread across 3 providers
- Thinking models vs fast models: know the tradeoff
- One dashboard, three vendors, complete visibility

**Talk Track**:
> "Here's my hot take: If you're using multiple LLM providers without unified observability, you're basically managing three separate blind spots.
>
> You don't know:
> - That your thinking model costs 24x your fast model
> - Whether that premium model is actually delivering better results
> - Which provider is fastest, cheapest, or most reliable
> - Why your API bill doubled last month — was it OpenAI? Anthropic? Gemini?
>
> And in production with hundreds of conversations per day across multiple providers, that's terrifying.
>
> The good news? OpenTelemetry doesn't care which LLM provider you use. One instrumentation, one collector, one dashboard. Vendor-neutral observability for a multi-vendor world.
>
> Marvin might be depressed, but at least you'll know his depression costs exactly $11 per million tokens on Claude Sonnet — and you can decide if Claude Haiku's depression is good enough at $3.67."

---

### Slide 9: Call to Action (7:30-8:00)
**Visual**: QR code + GitHub repo link + Grafana Cloud trial link

**Talk Track**:
> "If you want to try this yourself - everything I showed you is open source. Scan this QR code for the GitHub repo. Six bots, three providers, 39 custom tools, load generators, and a pre-built Grafana dashboard — all included.
>
> Grafana Cloud has a free tier — scan the second QR code. You can have this running in 30 minutes with `make start`.
>
> Alright, I've got 2 minutes for questions. Who wants to ask about robot psychology — or multi-provider economics?"

---

## Demo Preparation Checklist

### Before the Talk:
- [ ] Demo running: `cd demo && make start`
- [ ] Bots configured: 6 bots across 3 providers (HAL/JARVIS on OpenAI, Marvin/Bender on Anthropic, GLADOS/Cortana on Gemini)
- [ ] Test data generated: `make load-gen && make load-gen-tools`
- [ ] Grafana dashboard open with pre-populated data:
  - Cost-by-bot panel showing 24x spread
  - Provider breakdown panel
  - Token usage by model
  - Tool calls panel
- [ ] OpenWebUI open at http://localhost:3000
- [ ] Logged in and HAL selected in model dropdown
- [ ] Test screen sharing - make sure fonts/bots are readable
- [ ] Have backup screenshots in case demo gods are angry

### During the Talk:
- **0:00-2:00**: Slides only, build anticipation
- **2:00-5:00**: Live demo - OpenWebUI + Grafana side by side
- **5:00-7:30**: Back to slides for insights + takeaways
- **7:30-10:00**: Q&A

### Pro Tips:
- Emphasize the 24x cost spread — it's the headline number
- Name the providers when you name the bots: "Marvin on Anthropic Sonnet" not just "Marvin"
- The thinking model angle is NEW and interesting — GLADOS on gemini-3-pro deliberates, it's slow but thorough
- Reference real dollar amounts from the dashboard — specifics are more compelling than "it varies"
- If demo breaks, joke: "Even HAL has bad days across all three providers - this is why we need observability"
- Keep energy HIGH - six robot personalities are inherently entertaining, use it!

---

## Backup Q&A Answers

**Q: "Does this work with frameworks other than OpenWebUI?"**
A: "Absolutely! OpenInference is framework-agnostic. It works with LangChain, LlamaIndex, CrewAI, AutoGen - anything that makes LLM calls. OpenWebUI just happens to be a great demo platform because it has built-in bot personalities and tool management. The instrumentation pattern is the same everywhere."

**Q: "How does LiteLLM fit in? Isn't that another moving part?"**
A: "LiteLLM is a lightweight proxy that translates OpenAI-format requests to Anthropic's native API. It's one container, zero config for us. OpenAI and Gemini both support OpenAI-compatible endpoints natively, so only Anthropic needs the proxy. In production, many teams already use LiteLLM or similar gateways for exactly this reason."

**Q: "What about thinking models? Do they trace differently?"**
A: "Great question! Thinking models like gemini-3-pro take longer and use more tokens because they deliberate internally. The traces capture everything — you can see the extra latency and token cost. That's actually one of the most interesting things to observe: is the thinking model's extra cost worth the quality improvement? The traces give you data to answer that."

**Q: "Isn't this logging sensitive data? What about PII?"**
A: "In this demo, yes - we capture prompts and responses for educational purposes. In production, you'd use OTEL attribute filtering to DROP sensitive fields before export. You keep the metadata (tokens, latencies, tool names, provider) but strip the actual prompt/response text."

**Q: "How much does Grafana Cloud cost for this?"**
A: "Free tier covers 50GB of traces per month. For a small-to-medium AI app, that's plenty. And honestly, the cost of observability is TINY compared to running a bot on an $11/M model when a $0.45/M model would work fine. One optimization pays for years of tracing."

**Q: "Can you do this with streaming responses?"**
A: "Yes! The instrumentation accumulates tool calls across SSE chunks and captures the full token count when the stream completes. Works identically across all three providers."

**Q: "What's the actual cost difference you've seen?"**
A: "In our demo: Marvin on Claude Sonnet costs $0.074 per load test session. JARVIS on gpt-4o-mini costs $0.0018. That's 41x in practice — even worse than the 24x token rate difference because Marvin's personality makes him verbose too. Double cost multiplier: expensive model + chatty personality."

---

## Key Metrics to Highlight

Pull these from your actual dashboard during the demo:

- **3 LLM providers**: OpenAI, Anthropic, Google Gemini
- **6 unique models**: gpt-4o, gpt-4o-mini, claude-sonnet-4-5, claude-haiku-4-5, gemini-3-pro, gemini-3-flash
- **24x token cost spread**: $0.45/M (gpt-4o-mini) to $11.00/M (Sonnet)
- **41x actual cost spread**: $0.0018 (JARVIS) to $0.074 (Marvin) per session
- **Thinking model premium**: gemini-3-pro and Sonnet cost 8-24x more than fast models
- **39 custom tools** across 6 tool sets
- **Trace attributes**: 13+ OpenInference attributes per LLM span including provider
- **Setup time**: `make start` — one command

---

## Slide Design Notes

### Visual Elements:
- **Provider logos**: OpenAI, Anthropic, Google — show all three prominently
- **Bot avatars**: Use icons for each personality, color-coded by provider
- **Color coding by provider**: OpenAI=green, Anthropic=orange, Google=blue (or use provider brand colors)
- **Cost gradient**: Red (expensive) → Green (cheap) for cost panels
- **Grafana orange**: Use #FF8C00 for observability/metrics theme
- **Dark mode**: Looks better for live demos

### Fonts:
- Headers: Bold, sans-serif
- Body: Clean, readable
- Code: Monospace

### Demo Window Layout:
- 50% OpenWebUI chat (left)
- 50% Grafana dashboard (right)
- OR full-screen Grafana for the cost comparison panels

---

**Last Updated**: 2026-02-18
**Duration**: 10 minutes (7 min talk + 3 min Q&A)
**Difficulty**: Medium (requires live demo confidence)
**Fun Factor**: Very High (robot personalities + multi-provider economics!)
