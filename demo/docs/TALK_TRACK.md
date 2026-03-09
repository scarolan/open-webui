# Demo Talk Track — 10 Minutes

**Audience**: Mostly non-technical. Keep it fun, keep it visual, don't get lost in traces.

**Vibe**: You're showing off cool robots and casually revealing why observability matters. The bots are the hook — the dashboard is the punchline.

**Setup**: OpenWebUI on the left, Grafana dashboard on the right. Start traffic gen 45 min early so the dashboard is populated.

---

## Before You Start

```bash
cd demo
make start                     # Full stack up (~2 min)
make traffic DURATION=45       # Background traffic for dashboard data
make load-gen-tools            # Populate tool usage panel
```

Open two browser windows side by side:
- **Left**: http://localhost:3000 (OpenWebUI)
- **Right**: Grafana dashboard (set to "Last 30 minutes")

Log in, pick HAL from the dropdown, and you're ready.

---

## The Talk

### 1. Open with the Hook (1 min)

> "So — how many of you have used ChatGPT? Copilot? Gemini? Yeah, we all have. Now imagine you're running SIX AI assistants in production, each with a different personality, spread across three different providers — OpenAI, Anthropic, and Google. And each one is spending your money at a wildly different rate."
>
> "That's what I built. Let me show you."

**[Show OpenWebUI — point out the bot dropdown with all 6 names]**

> "Six bots. Six different LLM models. Three cloud providers. HAL 9000, JARVIS, Marvin the depressed robot, Bender, GLADOS from Portal, and Cortana from Halo. Each one has its own personality, its own set of tools, and its own price tag."

---

### 2. Chat with a Fast Bot — Introduce Tool Calling (2 min)

**[Select HAL, type: "HAL, what's the status of the pod bay doors?"]**

> "So I ask HAL about the pod bay doors. Watch what happens..."

**[HAL responds in character, calls the pod_bay_doors tool]**

> "See that? HAL didn't just generate text. He actually called a TOOL — a function called `pod_bay_doors`. This is what people mean by 'agentic AI.' The LLM decides it needs to DO something, picks the right tool from its toolkit, calls it, gets the result, and then weaves that into its response."
>
> "HAL has tools like `run_diagnostics`, `check_mission_status`, and `analyze_voice_stress`. Each bot has its own set — 39 tools total across all six bots."

**[Select JARVIS, type: "JARVIS, run a suit diagnostic"]**

> "JARVIS is Tony Stark's AI — he's on the same provider as HAL, but a cheaper model. Watch how fast he responds..."

**[JARVIS responds quickly]**

> "Snappy. Concise. Gets the job done. Now let's try someone... different."

---

### 3. Chat with GLADOS — The Thinking Model (2 min)

**[Select GLADOS, type: "GLADOS, how's the neurotoxin coming along?"]**

> "GLADOS is on Google's gemini-pro-latest, which is what they call a 'thinking model.' It actually reasons through the problem before responding. Watch the response time..."

**[Wait... and wait... GLADOS eventually responds with a deliciously evil monologue]**

> "That took a while, right? She's THINKING. Deliberating. Planning how to best threaten us. That thinking costs money — more tokens, more time, bigger bill."
>
> "And that's the thing — when you're running multiple AI models, you need to know: is the expensive thinking model actually worth it? Or could a fast model do the same job?"

**[If GLADOS hasn't responded yet, chat with Bender while waiting]**

**[Select Bender: "Bender, what do you think of humans?"]**

> "While GLADOS thinks about neurotoxin, Bender on Claude Haiku has an instant opinion."

---

### 4. Pivot to the Dashboard (3 min)

> "OK so we've been chatting with robots. Fun, right? Now let me show you what was happening behind the scenes the whole time."

**[Switch to Grafana dashboard]**

> "This is Grafana. Every single conversation we just had — and the hundreds of test conversations I ran before the demo — they all generated traces. Telemetry. Data about what the AI was actually doing."

Walk through the panels:

**Request Rate:**
> "Here's our request rate. Every spike is a bot conversation."

**Bots in Use:**
> "All six bots, all three providers, all generating data."

**Estimated Cost by Bot** (the money shot):
> "Now HERE'S the interesting part. This panel shows estimated cost by bot. See how Marvin — the depressed robot on Anthropic's most expensive model — towers over everyone else? He costs about 24 TIMES more per conversation than JARVIS on OpenAI's budget model."
>
> "Why? Two reasons. First, the model itself is more expensive. Second, Marvin's personality makes him VERBOSE. He'll use 1,000 tokens to tell you he's miserable. JARVIS uses 350 tokens to save the world."

**LLM Response Time p95:**
> "And look at response times. See that spike? That's GLADOS on the thinking model. Two to three MINUTES per response. The other bots? Under 10 seconds. Without this dashboard, you'd just know 'some bot is slow' but not which one or why."

**Token Usage:**
> "Tokens are the currency of AI. This is where your money goes. Prompt tokens are what you send IN, completion tokens are what the AI sends BACK. Different models, different costs, different behaviors — all visible in one place."

**Tool Usage** (if populated):
> "And here's the tool usage panel — remember HAL calling `pod_bay_doors`? Every tool call across every bot shows up here."

---

### 5. The Takeaway (1 min)

> "So what's the point? The point is: AI isn't a black box anymore. With the right instrumentation, you can see exactly what your AI agents are doing — which tools they're calling, how many tokens they're burning, how much each conversation costs, and which provider is giving you the best value."
>
> "We're running three different AI providers here — OpenAI, Anthropic, and Google — and without this kind of observability, you'd be checking three separate billing dashboards and GUESSING. One dashboard, three vendors, complete visibility."
>
> "The whole thing is open source, it's about 400 lines of instrumentation code, and you can set it up with one command. Happy to chat more about it after."

---

### 6. Q&A (1 min)

> "Questions? And yes, the cake is a lie."

**Common questions:**

- **"Does this work with other AI frameworks?"** — Yes! The instrumentation is based on OpenTelemetry + OpenInference standards. Works with LangChain, LlamaIndex, any framework that makes LLM calls.

- **"What about sensitive data?"** — In production you'd filter out prompts and responses. Keep the metadata (tokens, costs, tool names) but strip the actual conversation content.

- **"How much does the monitoring cost?"** — Grafana Cloud has a free tier. And the cost of monitoring is nothing compared to accidentally running your chatbot on an $11/million-token model when a $0.45 model would do.

- **"What's a thinking model?"** — Models like gemini-pro-latest and Claude Sonnet do internal reasoning before responding. Better quality sometimes, but much slower and more expensive. The traces let you see whether the quality difference is worth the cost.

---

## Cheat Sheet

### Bot Quick Reference

| Bot | Provider | Model | Cost | Personality |
|-----|----------|-------|------|-------------|
| HAL 9000 | OpenAI | gpt-4o | $7.50/M | Ominous spaceship AI |
| JARVIS | OpenAI | gpt-4o-mini | $0.45/M | Efficient, concise |
| Marvin | Anthropic | claude-sonnet-4-5 | $11.00/M | Depressed, verbose, EXPENSIVE |
| Bender | Anthropic | claude-haiku-4-5 | $3.67/M | Rude but cheap |
| GLADOS | Google | gemini-pro-latest | $8.67/M | Thinking model, SLOW |
| Cortana | Google | gemini-flash-latest | $2.17/M | Fast, tactical |

### Key Numbers
- **24x** cost spread between cheapest and most expensive bot
- **3** LLM providers (OpenAI, Anthropic, Google)
- **6** unique models
- **39** custom tool functions
- **~400** lines of instrumentation code

### Favorite Chat Prompts
- HAL: "What's the status of the pod bay doors?"
- JARVIS: "Run a suit diagnostic"
- Marvin: "How much of your brain are you using?"
- Bender: "What do you think of humans?"
- GLADOS: "How's the neurotoxin coming along?"
- Cortana: "Scan for Covenant forces"

### If the Demo Breaks
Say: "Even HAL has bad days — this is exactly why we need observability!"
Switch to the pre-populated dashboard and talk from there.
