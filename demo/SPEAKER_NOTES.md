# 🎤 Speaker Notes - Quick Reference Card
**Print this or keep on phone during talk**

---

## ⏱️ TIMING CHECKPOINTS
- 2:00 → Start live demo
- 5:00 → End demo, back to slides
- 7:00 → On takeaway slide
- 8:00 → Open Q&A

---

## 🎯 THE STRUCTURE

### 1. HOOK (0:30)
"Your AI has multiple personalities... they're all spending your money"
- Poll: Who's deployed AI agents?
- Poll: Who knows which is most expensive?
- Metaphor: Parenting six robot personalities

### 2. PAIN (1:00)
Three things happen:
1. Cloud bill is concerning
2. Users say "HAL is slower than Bender" - you don't know why
3. Boss asks "which bot to optimize?" - you're guessing

Traditional obs → HTTP
AI obs → WHICH bot, what tools, why tokens

### 3. DEMO SETUP (0:30)
Six bots:
- HAL (paranoid spaceship AI)
- Marvin (depressed robot)
- Bender (alcoholic robot)
- GLADOS (sadistic AI)
- JARVIS (efficient assistant)
- Cortana (tactical AI)

39 tools total

### 4. HAPPY PATH (1:30)
Query: "HAL, what's the status of the pod bay doors?"
Show: Bot name (hal), tool call (pod_bay_doors), tokens (275), cost ($0.0002), latency (1.4s)

### 5. CHAOS (1:30)
Bot comparison: Marvin 3x more expensive than JARVIS (personality costs!)
Tool patterns: HAL over-diagnoses, GLADOS over-deploys
Failed trace: 0 chars = hallucinated tool call, burned tokens

### 6. THE MONEY SHOT (1:00)
Four superpowers:
1. Cost attribution by personality (3.3x difference!)
2. Tool usage patterns (HAL's paranoia, GLADOS's sadism)
3. System prompt validation (is personality working?)
4. Debugging with context (not "500", actual error with bot+tool+input)

### 7. HOW (0:45)
OTEL + OpenInference + Grafana
100 lines of code, 30 mins setup
Handles OpenAI format AND OpenWebUI embedded format

### 8. HOT TAKE (0:45)
"Deploying multiple agents without observability = parenting in the dark"
Don't know: which expensive, if tools correct, if prompts work, why fail
"Terrifying in production"
"Marvin's depression has a dollar amount now"

### 9. CTA (0:30)
QR codes: GitHub + Grafana Cloud
"30 minutes, docker-compose up"
"Who wants to ask about robot psychology?"

---

## 💪 POWER PHRASES

✅ "Parenting in the dark"
✅ "Personality matters"
✅ "Terrifying in production"
✅ "Table stakes for multi-agent systems"
✅ "At least you'll know exactly how much his depression costs"
✅ "Even HAL has bad days"

❌ "Probably should"
❌ "It's complicated"
❌ "Maybe you could"

---

## 🎬 DEMO TRACES (Pre-identify!)

**Trace 1**: Clean HAL query (pod bay doors, single tool call)
**Trace 2**: Bot comparison bar chart (all 6 bots, cost variance)
**Trace 3**: Failed trace with 0 response chars (hallucinated tool)

---

## 🔢 KEY NUMBERS

- 6 bot personalities
- 39 custom tools
- **3.3x cost variance** (Marvin vs JARVIS)
- $0.0002-0.001 per query
- 13+ OpenInference attributes
- 30 min setup
- 100 lines code

---

## 🛡️ IF DEMO BREAKS

Say: "Even HAL has bad days - this is why we need observability!"
Do: Switch to backup screenshots

---

## 🎤 OPENING (Memorize)

"Hey folks! Quick question - how many of you have deployed AI agents or chatbots?"

[Hands up]

"Awesome. Now keep your hand up if you can tell me EXACTLY which of your agents is the most expensive to run."

[Hands drop]

"Yeah, thought so. Today I'm going to show you why AI observability is basically parenting six different robot personalities..."

---

## 🏁 CLOSING (Memorize)

"Here's my hot take: If you're deploying multiple AI agents or bot personalities without observability, you're basically parenting in the dark."

[Pause]

"You don't know which bots are expensive vs efficient, if they're using tools correctly, whether their personality prompts actually work, or why they fail."

[Pause]

"In production, that's terrifying. Especially when you scale to hundreds of conversations per day."

[Pause]

"The good news? OpenTelemetry and OpenInference make it easy. The fun part? You get to watch your robot personalities in action and optimize the expensive troublemakers."

[Smile]

"Marvin might be depressed, but at least you'll know EXACTLY how much his depression costs you per query."

[Point to QR codes]

"Alright, I've got 2 minutes for questions. Who wants to ask about robot psychology?"

---

## ❓ LIKELY QUESTIONS

**Q: Non-OpenWebUI frameworks?**
A: Framework-agnostic! LangChain, LlamaIndex, CrewAI, AutoGen. Same pattern.

**Q: Other providers (OpenAI/Anthropic)?**
A: Yes! ALL providers. Token metadata universal. Using Gemini for free tier demo.

**Q: Sensitive data / PII?**
A: Attribute filtering → DROP prompts/responses, KEEP metadata. Docs in repo.

**Q: Grafana Cloud cost?**
A: Free tier = 50GB/month. Cost of obs << cost of inefficient bots.

**Q: Streaming?**
A: Yes! Captures when stream completes. Full tokens + latency.

**Q: Tools only in UI?**
A: OpenWebUI attaches tools during UI flow. For demos use UI (fun!) or explicit API calls.

---

## 🎯 BODY LANGUAGE

✅ Stand if possible
✅ Reference bots by name (more engaging)
✅ Point at specific trace attributes
✅ Make eye contact during polls
✅ Smile when showing bot personalities
✅ High energy throughout
✅ Optional: Do the voices (HAL, Marvin, Bender) if brave

---

## 🚨 WHAT NOT TO FORGET

- [ ] Docker running
- [ ] Bots configured (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
- [ ] Test data generated (30+ traces)
- [ ] 3 traces pre-identified
- [ ] Grafana loaded, time range set
- [ ] OpenWebUI logged in, HAL selected
- [ ] Backup screenshots ready
- [ ] Phone on silent
- [ ] Water nearby
- [ ] BREATHE

---

## 💡 THE ONE THING

**If you forget everything else, remember this:**

The bots are the heroes.
Your job: show why observability matters for multi-agent systems.
How: real personalities, real tools, real cost differences.

The robots are inherently entertaining - USE IT!

**You've got this! 🤖🔥**

---

## 🎨 DEMO TIPS

### When Showing OpenWebUI:
- Select bot from dropdown, say the name out loud
- Type slowly so audience can read
- Point out the superscript tool call indicator
- Wait for response, then immediately flip to Grafana

### When Showing Grafana:
- Use large font size (zoom in browser if needed)
- Click on a single span to expand details
- Highlight specific attributes (bot name, tokens, tool calls)
- Use mouse to point at numbers you're discussing

### When Showing Dashboards:
- Full screen the visualization
- Explain axes ("This is bot name, this is total traces")
- Call out the variance ("See? Marvin is 3x more expensive!")
- Let the data tell the story

---

## 🎭 PERSONALITY HOOKS

Use these to keep energy high:

- **HAL**: "HAL's paranoid - he over-diagnoses everything"
- **Marvin**: "Marvin's depression is EXPENSIVE, token-wise"
- **Bender**: "Bender's creative insults cost more than you'd think"
- **GLADOS**: "GLADOS loves deploying turrets - system prompt working as intended!"
- **JARVIS**: "JARVIS is efficient - Tony Stark doesn't waste money"
- **Cortana**: "Cortana's all tactical analysis, barely needs tools"

Reference them by personality trait = more memorable than "agent 3 uses more tokens"
