# Speaker Notes - Quick Reference Card
**Print this or keep on phone during talk**

---

## TIMING CHECKPOINTS
- 2:00 → Start live demo
- 5:00 → End demo, back to slides
- 7:00 → On takeaway slide
- 8:00 → Open Q&A

---

## THE STRUCTURE

### 1. HOOK (0:30)
"Your AI has multiple personalities... they're all spending your money"
- Poll: Who's deployed AI agents?
- Poll: Who uses MORE THAN ONE provider?
- Poll: Who knows which agent is most expensive?
- Headline: 24x cost spread across 3 providers

### 2. PAIN (1:00)
Three things happen:
1. Cloud bill split across THREE vendors — concerning
2. Users say "GLADOS is slower than JARVIS" — thinking model vs fast model, no data
3. Boss asks "which provider to consolidate on?" — you're guessing

Traditional obs → HTTP requests
AI obs → WHICH bot, WHICH provider, what tools, why tokens, what cost

### 3. DEMO SETUP (0:30)
Six bots, three providers, six unique models:
- HAL → OpenAI gpt-4o ($7.50/M)
- JARVIS → OpenAI gpt-4o-mini ($0.45/M)
- Marvin → Anthropic Sonnet ($11.00/M) ← MOST EXPENSIVE
- Bender → Anthropic Haiku ($3.67/M)
- GLADOS → Google gemini-3-pro ($8.67/M) ← THINKING MODEL
- Cortana → Google gemini-3-flash ($2.17/M)

39 tools total. 24x cost spread.

### 4. HAPPY PATH (1:30)
Query: "HAL, what's the status of the pod bay doors?"
Show: Bot name (hal), provider (openai), base model (gpt-4o), tool call (pod_bay_doors), tokens (275), cost

### 5. THE MONEY SHOT (1:30)
Cost panel: Marvin $0.074, GLADOS $0.038, JARVIS $0.0018
- Marvin 41x more expensive than JARVIS IN PRACTICE
- Two reasons: model pricing (24x) + personality verbosity (Marvin 1100 tokens, JARVIS 350)
- Provider view: Anthropic most expensive, Google middle, OpenAI cheapest
- KEY POINT: "Without vendor-neutral observability, you'd have three separate dashboards"

### 6. FOUR SUPERPOWERS (1:00)
1. Cross-vendor cost attribution (24x spread, data to act on)
2. Thinking model economics (is gemini-3-pro worth it over flash?)
3. Tool usage across providers (do tools work differently?)
4. Vendor-neutral debugging (one trace, complete context, any provider)

### 7. HOW (0:45)
OTEL + OpenInference + LiteLLM + Grafana
100 lines of code. `make start`. Three providers, one dashboard.
Tail sampling: keeps only LLM spans, 90% noise filtered.

### 8. HOT TAKE (0:45)
"Multiple providers without unified observability = three separate blind spots"
Don't know: 24x cost spread, thinking model tradeoffs, which provider best
"Terrifying in production across vendors"
"Marvin's depression costs $11/M on Sonnet — maybe Haiku's depression is good enough at $3.67"

### 9. CTA (0:30)
QR codes: GitHub + Grafana Cloud
"`make start` — 30 minutes, three providers, one dashboard"
"Who wants to ask about robot psychology or multi-provider economics?"

---

## POWER PHRASES

Use these:
- "24x cost spread across three vendors"
- "You can't optimize what you can't see across all your providers"
- "One dashboard, three vendors, complete visibility"
- "Is the thinking model worth 24x the cost?"
- "Three separate blind spots"
- "Vendor-neutral observability for a multi-vendor world"
- "Marvin's depression has a dollar amount: $11 per million tokens"

Avoid:
- "Probably should"
- "It's complicated"
- "Maybe you could"

---

## DEMO TRACES (Pre-identify!)

**Panel 1**: Cost-by-bot showing Marvin >> GLADOS >> HAL >> Bender >> Cortana >> JARVIS
**Panel 2**: Provider breakdown (Anthropic highest, Google middle, OpenAI lowest)
**Panel 3**: Token usage showing Marvin's verbosity (1100 tokens avg)
**Panel 4**: Tool calls across all 6 bots

---

## KEY NUMBERS

- **3** LLM providers (OpenAI, Anthropic, Google)
- **6** bot personalities on **6** unique models
- **39** custom tools
- **24x** token cost spread ($0.45/M to $11.00/M)
- **41x** actual cost spread in practice ($0.0018 to $0.074 per session)
- **$11.00/M** most expensive (Marvin on Sonnet)
- **$0.45/M** cheapest (JARVIS on gpt-4o-mini)
- **100** lines of instrumentation code
- **1** command to start: `make start`

---

## IF DEMO BREAKS

Say: "Even HAL has bad days across all three providers - this is why we need observability!"
Do: Switch to backup screenshots

---

## OPENING (Memorize)

"Hey folks! Quick question - how many of you have deployed AI agents or chatbots?"

[Hands up]

"Now keep your hand up if you're using MORE THAN ONE LLM provider."

[Some hands stay]

"Keep your hand up if you can tell me EXACTLY which agent is the most expensive to run."

[Hands drop]

"Yeah, thought so. Today I'm going to show you six robot personalities spread across OpenAI, Anthropic, and Google — with a 24x cost spread — and why multi-provider observability is the only way to make sense of it."

---

## CLOSING (Memorize)

"Here's my hot take: If you're using multiple LLM providers without unified observability, you're managing three separate blind spots."

[Pause]

"You don't know that your thinking model costs 24x your fast model. You don't know if that premium is worth it. You don't know which provider is fastest or cheapest."

[Pause]

"In production, that's terrifying. One dashboard. Three vendors. Complete visibility. That's what OpenTelemetry gives you."

[Pause]

"Marvin might be depressed, but at least you'll know his depression costs exactly $11 per million tokens on Sonnet — and you can decide if Haiku's depression is good enough at $3.67."

[Point to QR codes]

"Alright, questions. Who wants to talk about robot psychology or multi-provider economics?"

---

## LIKELY QUESTIONS

**Q: Non-OpenWebUI frameworks?**
A: Framework-agnostic! LangChain, LlamaIndex, CrewAI, AutoGen. Same pattern.

**Q: How does LiteLLM fit in?**
A: Lightweight proxy for Anthropic. OpenAI and Gemini connect directly. One container, zero config.

**Q: Thinking models different?**
A: Yes! Longer latency, more tokens, higher cost. Traces show the tradeoff — is the quality worth 24x?

**Q: Sensitive data / PII?**
A: Attribute filtering → DROP prompts/responses, KEEP metadata (tokens, provider, cost). Docs in repo.

**Q: Grafana Cloud cost?**
A: Free tier = 50GB/month. Cost of obs << cost of running $11/M model when $0.45/M would work.

**Q: Streaming?**
A: Yes! Accumulates tool calls across SSE chunks. Full tokens + latency when stream completes.

**Q: Actual cost difference?**
A: Marvin $0.074/session, JARVIS $0.0018. That's 41x — model pricing PLUS personality verbosity.

---

## BODY LANGUAGE

- Stand if possible
- Name the PROVIDER when you name the bot: "Marvin on Anthropic Sonnet"
- Point at specific cost numbers on the dashboard
- Make eye contact during polls
- Smile when showing bot personalities
- High energy throughout
- The 24x number is your anchor — keep coming back to it

---

## WHAT NOT TO FORGET

- [ ] Docker running (3 containers: openwebui, litellm, otel-collector)
- [ ] Bots configured (6 bots, 3 providers)
- [ ] Test data generated (`make load-gen && make load-gen-tools`)
- [ ] Dashboard loaded with cost data
- [ ] Grafana time range set
- [ ] OpenWebUI logged in, HAL selected
- [ ] Backup screenshots ready
- [ ] Phone on silent
- [ ] Water nearby
- [ ] BREATHE

---

## THE ONE THING

**If you forget everything else, remember this:**

24x cost spread. Three providers. One dashboard. You can't optimize what you can't see.

The robots are the hook — multi-provider economics is the insight.

**You've got this!**

---

## PERSONALITY HOOKS

Use these to keep energy high:

- **HAL** (OpenAI gpt-4o): "HAL's on the premium OpenAI model — paranoid AND expensive"
- **JARVIS** (OpenAI gpt-4o-mini): "JARVIS is efficient — Tony Stark runs on the budget model and still gets the job done"
- **Marvin** (Anthropic Sonnet): "Marvin's depression is EXPENSIVE — $11 per million tokens on the most premium model, and he's VERBOSE about it"
- **Bender** (Anthropic Haiku): "Bender's on the cheap Anthropic model — even his insults are budget-friendly"
- **GLADOS** (Google gemini-3-pro): "GLADOS is on a thinking model — she DELIBERATES before deploying turrets. Slow, expensive, thorough."
- **Cortana** (Google gemini-3-flash): "Cortana's tactical — fast model, fast responses, low cost. Military efficiency."

Reference by personality + provider + model = maximum impact.

---

## DEMO TIPS

### When Showing OpenWebUI:
- Select bot from dropdown, say the name AND provider out loud
- Type slowly so audience can read
- Point out the tool call indicator
- Wait for response, then immediately flip to Grafana

### When Showing Grafana:
- Full screen the cost panel — it's the star
- Point at Marvin's bar vs JARVIS's bar — the visual gap is dramatic
- Call out specific dollar amounts: "$0.074 vs $0.0018"
- Show the provider breakdown — three colors, three vendors, one chart

### When Showing Dashboards:
- Lead with cost panel (the money shot)
- Then provider breakdown (the why)
- Then token usage (the detail)
- Let the 24x gap tell the story
