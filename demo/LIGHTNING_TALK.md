# 🤖 "Your AI Has Multiple Personalities... And They're All Spending Your Money" - Lightning Talk
**10 Minutes | OpenWebUI Bot Observatory Demo | Grafana Cloud**

---

## 🎯 Talk Structure (7 mins content + 3 mins Q&A)

### Slide 1: Title Slide (0:00-0:30)
**Visual**: OpenWebUI logo + Six bot avatars (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana) + Grafana logo
**Title**: "Your AI Has Multiple Personalities... And They're All Spending Your Money"
**Subtitle**: "A 7-Minute Journey into AI Observability with Temperamental Robots"

**Talk Track**:
> "Hey folks! Quick question - how many of you have deployed AI agents or chatbots? [pause for hands] Awesome. Now keep your hand up if you can tell me EXACTLY which of your agents is the most expensive to run. [pause - most hands drop] Yeah, thought so. Today I'm going to show you why AI observability is basically parenting six different robot personalities - they're all unique, they're all doing their own thing, and without proper supervision, they'll absolutely blow your API budget. But unlike actual teenagers, we can trace everything they do."

---

### Slide 2: The Problem (0:30-1:30)
**Visual**: Split screen - "What You Built" vs "What's Actually Happening"
- Left: Simple chatbot interface, user sends message
- Right: Chaos - multiple LLM calls, tool invocations, token explosions, errors

**Talk Track**:
> "So you built some AI assistants. Maybe you used OpenWebUI, LangChain, AutoGen, CrewAI - doesn't matter. You deployed them. Users love them. Then three things happen:
>
> 1. Your cloud bill arrives and... [dramatic pause] ...it's concerning
> 2. Users complain that 'HAL is slower than Bender' - and you have no idea why
> 3. Your boss asks 'Which bot should we optimize first?' and you're just guessing
>
> Traditional observability doesn't cut it here. You can see HTTP requests, sure. You can see 'model: gemini-2.0-flash-exp made an API call.' But you CAN'T see:
> - WHICH bot personality made that call
> - What tools they invoked
> - Why Marvin used 3,000 tokens to say he's depressed
> - Whether your bot's system prompt is even working
>
> You're flying blind with a fleet of AI personalities."

---

### Slide 3: The Demo App (1:30-2:00)
**Visual**: Architecture diagram + 6 bot cards with their tools
- HAL 9000: Spaceship AI (pod_bay_doors, run_diagnostics)
- Marvin: Depressed robot (brain_utilization, calculate_meaninglessness)
- Bender: Alcoholic robot (insult_generator, brew_beer)
- GLADOS: Sadistic AI (neurotoxin_status, test_chamber_control)
- JARVIS: Tony Stark's AI (suit_diagnostics, threat_assessment)
- Cortana: Halo AI (scan_covenant, spartan_vitals)

**Talk Track**:
> "Let me show you what we built for testing observability with character. This is an instrumented OpenWebUI fork with six bot personalities:
> - HAL 9000 - the ominous spaceship AI
> - Marvin - the clinically depressed robot
> - Bender - the alcoholic bending unit
> - GLADOS - the sadistic testing AI
> - JARVIS - Tony Stark's helpful assistant
> - Cortana - Master Chief's tactical AI
>
> Each one has custom tools - 39 functions total. HAL can check pod bay door status. Marvin can calculate the meaninglessness of existence. Bender can generate insults and brew beer. You get the idea.
>
> The question is: when you've got six different AI personalities, each with their own tools and prompts, how do you know what they're ACTUALLY doing? Let's find out."

---

### Slide 4: Live Demo Part 1 - The Happy Path (2:00-3:30)
**Visual**: Screen share split - OpenWebUI chat + Grafana Tempo

**Talk Track**:
> "Let me open the OpenWebUI interface and chat with HAL. I'll ask: 'HAL, what's the status of the pod bay doors?'
>
> [Type query, hit send]
>
> Watch what HAL does - see that little superscript indicator? That means he's calling a tool. He's actually executing the `pod_bay_doors` function.
>
> Now flip over to Grafana Tempo. [Switch to dashboard] Look at this trace that just appeared:
>
> 1. **Model Name**: `hal` - not just 'gemini-flash', we know WHICH bot responded
> 2. **Base Model**: `gemini-3-flash-preview` - the underlying LLM
> 3. **Token Usage**: 180 prompt tokens, 95 completion tokens = 275 total
> 4. **Tool Calls**: 1 tool invoked - `pod_bay_doors` with argument `{action: "status"}`
> 5. **Total Cost**: ~$0.0002 for this conversation
> 6. **Latency**: 1.4 seconds end-to-end
>
> That's the happy path. But here's where it gets interesting - let me show you what happens when bots get creative."

---

### Slide 5: Live Demo Part 2 - The Chaos (3:30-5:00)
**Visual**: Grafana dashboard showing bot comparison metrics

**Talk Track**:
> "Now let's look at the data we generated earlier - I ran a load test with all six bots answering the same questions. Watch what happens.
>
> [Pull up bot usage bar chart]
>
> See this? Marvin and Bender are the MOST expensive bots to run. Why? Because of their personalities. Marvin's system prompt tells him to be verbose and existential. Bender's prompt encourages creative insults. So they burn more tokens per response than JARVIS, who's trained to be efficient.
>
> [Pull up tool usage over time]
>
> And look at tool invocation patterns. HAL calls `run_diagnostics` for EVERYTHING. It's in his nature - he's paranoid. GLADOS loves deploying turrets. Cortana barely uses tools - she's all tactical analysis in her responses.
>
> [Pull up a failed trace]
>
> And here's my favorite - this trace shows zero response characters. The LLM hallucinated a tool call that doesn't exist for that bot, errored out, and we burned 200 tokens for NOTHING. Without tracing, you'd never know this was happening.
>
> The million-dollar question: If you don't know which bots are expensive, which ones are calling the wrong tools, or which ones are hallucinating, how do you optimize? You can't."

---

### Slide 6: The Money Shot - What You Actually Learn (5:00-6:00)
**Visual**: Dashboard with four key metric panels highlighted
- Cost per bot (bar chart showing Marvin > Bender > HAL > others)
- Tool call patterns (time series)
- Token usage distribution (pie chart)
- Error rates by bot (bar gauge)

**Talk Track**:
> "So what does AI observability actually give you? Four superpowers:
>
> 1. **Cost Attribution by Personality** - You can see EXACTLY which bot personas cost what. Marvin averages $0.001 per query. JARVIS? $0.0003. That's 3.3x difference. If you're paying per token, personality matters.
>
> 2. **Tool Usage Patterns** - You can see when bots are over-using tools. HAL runs diagnostics on every query, even 'hello'. That's wasted function calls. You can tune his system prompt to be less paranoid.
>
> 3. **System Prompt Validation** - You can see if your personality prompts are working. If Bender's NOT using the insult generator, his prompt is broken. If GLADOS isn't dark and menacing, something's wrong.
>
> 4. **Debugging with Context** - When something fails, you don't just see 'HTTP 500'. You see: 'Bot: Marvin. Tool: calculate_meaninglessness. Input: Why are we here? Error: Function timeout after 30s'. That's ACTIONABLE. Maybe Marvin's existential calculations are actually too complex."

---

### Slide 7: How This Actually Works (6:00-6:45)
**Visual**: Simple architecture diagram
- OpenWebUI → OpenTelemetry SDK → Grafana Cloud Tempo
- OpenInference semantic conventions layer
- Shows span creation with bot name + tool calls

**Talk Track**:
> "Quick implementation note - this isn't magic or vendor lock-in. It's three open standards:
>
> 1. **OpenTelemetry SDK** - industry standard observability
> 2. **OpenInference semantic conventions** - LLM-specific attributes (model name, tokens, tool calls)
> 3. **Grafana Cloud Tempo** - stores and visualizes the traces
>
> The code changes? About 100 lines. We wrapped the LLM API call with a span manager that extracts bot name, token counts, and tool calls. It handles both OpenAI tool format AND OpenWebUI's embedded format automatically.
>
> Total setup time? 30 minutes. Docker compose up, run setup script, start chatting. Every LLM call becomes a trace with full context."

---

### Slide 8: The Takeaway (6:45-7:30)
**Visual**: Three key points with icons
- 💰 Know Which Personalities Cost Most
- 🔧 See Which Tools Are Actually Used
- 🎭 Validate System Prompts Are Working

**Talk Track**:
> "Here's my hot take: If you're deploying multiple AI agents or bot personalities without observability, you're basically parenting in the dark. You don't know:
> - Which bots are expensive vs efficient
> - If they're using tools correctly
> - Whether their personality prompts actually work
> - Why they fail or hallucinate
>
> And in production, that's terrifying. Especially when you scale to hundreds of conversations per day.
>
> Observability isn't optional anymore. It's table stakes for multi-agent systems. The good news? OpenTelemetry and OpenInference make it easy. The fun part? You get to watch your robot personalities in action, see what makes them tick, and optimize the expensive troublemakers.
>
> Marvin might be depressed, but at least you'll know EXACTLY how much his depression costs you per query."

---

### Slide 9: Call to Action (7:30-8:00)
**Visual**: QR code + GitHub repo link + Grafana Cloud trial link

**Talk Track**:
> "If you want to try this yourself - everything I showed you is open source. Scan this QR code, it'll take you to the GitHub repo. The whole instrumented OpenWebUI fork, six bot configs, 39 custom tools, and even the load generators I used.
>
> And if you want to try Grafana Cloud for observability, there's a free tier - scan the second QR code. You can have this running in 30 minutes with docker-compose.
>
> Alright, I've got 2 minutes for questions. Who wants to ask about robot psychology?"

---

## 🎬 Demo Preparation Checklist

### Before the Talk:
- [ ] Demo running: `cd demo && docker compose up -d`
- [ ] Bots configured: `python3 setup-bots.py` (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
- [ ] Test data generated: `python3 load-gen-bots.py` (30-60 seconds worth)
- [ ] Grafana dashboard open in browser tab with pre-identified traces:
  - A clean HAL query with tool call (happy path)
  - Bot comparison bar chart showing cost differences
  - Tool usage timeline showing patterns
  - A failed trace with 0 response chars
- [ ] OpenWebUI open in second browser tab at http://localhost:3000
- [ ] Logged in and HAL bot selected in model dropdown
- [ ] Test screen sharing - make sure fonts/bots are readable
- [ ] Have backup screenshots in case demo gods are angry

### During the Talk:
- **0:00-2:00**: Slides only, build anticipation
- **2:00-5:00**: Live demo - OpenWebUI + Grafana side by side
- **5:00-7:30**: Back to slides for insights + takeaways
- **7:30-10:00**: Q&A

### Pro Tips:
- Practice saying "OpenInference semantic conventions" without tripping
- Have the Grafana query ready: `{ span.openinference.span.kind = "LLM" }`
- Reference the bot personalities by name - it's more engaging than "agent 1"
- If demo breaks, joke: "Even HAL has bad days - this is why we need observability"
- Keep energy HIGH - six robot personalities are inherently entertaining, use it!
- Do the voices if you're feeling brave (kidding... unless?)

---

## 🎤 Backup Q&A Answers

**Q: "Does this work with frameworks other than OpenWebUI?"**
A: "Absolutely! OpenInference is framework-agnostic. It works with LangChain, LlamaIndex, CrewAI, AutoGen - anything that makes LLM calls. OpenWebUI just happens to be a great demo platform because it has built-in bot personalities and tool management. The instrumentation pattern is the same everywhere."

**Q: "What about other LLM providers like OpenAI or Anthropic?"**
A: "Works with ALL of them. OpenInference captures token counts from any provider that exposes them in the API response. We're using Gemini here because it's free-tier friendly for demos, but in production we've done this with GPT-4, Claude, Llama, DeepSeek - doesn't matter. Token metadata is universal."

**Q: "Isn't this logging sensitive data? What about PII?"**
A: "Great question! In this demo, yes - we're capturing prompts and responses for educational purposes. In production, you'd use OTEL attribute filtering to DROP sensitive fields before export. You keep the metadata (tokens, latencies, tool names) but strip the actual prompt/response text. We've got docs on this in the repo."

**Q: "How much does Grafana Cloud cost for this?"**
A: "Free tier covers 50GB of traces per month. For a small-to-medium AI app, that's plenty. And honestly, the cost of observability is TINY compared to the cost of running inefficient bots. If Marvin is 3x more expensive than JARVIS and you don't know it, observability pays for itself immediately."

**Q: "Can you do this with streaming responses?"**
A: "Yes! Streaming works fine - OpenInference captures spans when the stream completes. You'll see full token counts and latency for the entire streamed response, including tool calls accumulated across chunks."

**Q: "How do you handle tools that are only available in the UI?"**
A: "Good catch - OpenWebUI attaches bot tools during UI request flow, not via direct API. So for demos, we either use the UI (which is fun because personalities!) or use explicit tool definitions in API calls. The instrumentation handles both OpenAI tool format and OpenWebUI's embedded format automatically."

---

## 📊 Key Metrics to Highlight

Pull these from your actual dashboard during the demo:

- **6 bot personalities**: HAL, Marvin, Bender, GLADOS, JARVIS, Cortana
- **39 custom tools** across 6 tool sets
- **Token cost variance**: 3.3x difference between most/least expensive bots
- **Tool usage patterns**: HAL over-diagnoses, GLADOS over-deploys turrets, Cortana barely uses tools
- **Trace attributes**: 13+ OpenInference attributes per LLM span
- **Error rate**: ~5-10% (use this to show hallucinated tool calls)
- **Average latency**: 1-2 seconds for simple queries, 3-5 seconds with multiple tool calls

---

## 🎨 Slide Design Notes

### Visual Elements:
- **Bot avatars**: Use icons or simple graphics for each personality
- **Color coding**: Assign each bot a color (HAL=red, Marvin=blue, Bender=orange, etc.)
- **Grafana orange**: Use #FF8C00 for observability/metrics theme
- **Dark mode**: Looks better for live demos

### Fonts:
- Headers: Bold, sans-serif
- Body: Clean, readable
- Code: Monospace

### Demo Window Layout:
- 50% OpenWebUI chat (left)
- 50% Grafana Tempo (right)
- OR full-screen Grafana for metric dashboards

---

**Last Updated**: 2026-02-12
**Duration**: 10 minutes (7 min talk + 3 min Q&A)
**Difficulty**: 🌶️🌶️ (Medium - requires live demo confidence)
**Fun Factor**: 🤖🤖🤖🤖🤖 (Very High - robot personalities!)
