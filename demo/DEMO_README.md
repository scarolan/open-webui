# 🎤 Lightning Talk Demo Materials

> **Everything you need for a 10-minute lightning talk on AI observability**

This directory contains all materials for delivering a compelling 10-minute lightning talk using the OpenWebUI bot demo with Grafana Cloud observability.

---

## 📁 What's In This Folder

### 🎯 Primary Demo Materials

| File | Purpose | When to Use |
|------|---------|-------------|
| **LIGHTNING_TALK.md** | Full 10-minute script with slides | Read this first! Complete talk structure |
| **SPEAKER_NOTES.md** | One-page cheat sheet | Print this - quick reference during talk |
| **DEMO_CHAT.md** | Query reference + Grafana queries | Keep open during demo for copy/paste |
| **TALK_PREP.md** | Step-by-step prep guide | Use day-before and 30 mins before talk |

### 🛠️ Supporting Scripts

| File | Purpose | Usage |
|------|---------|-------|
| **setup-bots.py** | Configure all 6 bots + tools | Run once: `python3 setup-bots.py` |
| **load-gen-bots.py** | Generate test traces | Pre-talk prep: `python3 load-gen-bots.py` |
| **continuous-traffic.py** | Live traffic during talk | Background: `python3 continuous-traffic.py --api-key YOUR_KEY --duration 30` |
| **run-tests.sh** | Validate instrumentation | Optional: `./run-tests.sh --integration` |

### 📚 Technical Documentation

| File | Purpose |
|------|---------|
| **README.md** | Full technical setup guide |
| **INSTRUMENTATION_SUMMARY.md** | Deep dive on OTEL implementation |
| **GRAFANA_DASHBOARD_GUIDE.md** | Dashboard setup instructions |
| **DASHBOARD_FIX_SUMMARY.md** | TraceQL query reference |

---

## 🚀 Quick Start: Preparing Your Talk

### Step 1: One Day Before (30 minutes)

```bash
# Make sure everything works
cd ~/git_repos/open-webui/demo

# Start the stack
docker compose up -d

# Configure bots (enter your OpenWebUI credentials)
python3 setup-bots.py

# Generate test traces
python3 load-gen-bots.py

# Wait 60 seconds, then verify in Grafana
# Query: { span.openinference.span.kind = "LLM" }
```

✅ **Success**: You see traces from all 6 bots (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)

### Step 2: Pre-Flight Check (15 minutes before talk)

Follow **TALK_PREP.md** final checklist:
- [ ] Docker running
- [ ] Grafana accessible
- [ ] OpenWebUI logged in with HAL selected
- [ ] 3 key traces bookmarked
- [ ] Backup screenshots saved
- [ ] Browser tabs ready

### Step 3: During Talk

Keep **SPEAKER_NOTES.md** visible (phone or printed) for:
- Timing checkpoints
- Key numbers
- Power phrases
- Demo trace IDs

---

## 🎬 The Demo Flow (TL;DR)

**The Hook**: "Your AI has multiple personalities... and they're all spending your money"

**The Demo**:
1. Show OpenWebUI with HAL bot
2. Ask: "HAL, what's the status of the pod bay doors?"
3. Switch to Grafana, show the trace appearing
4. Deep dive: bot name, tokens (275), tool call (pod_bay_doors), cost ($0.0002)
5. Show bot comparison: Marvin 3x more expensive than JARVIS
6. Show failed trace with 0 response chars (hallucinated tool)

**The Takeaway**: "Without observability, you're parenting six robot personalities in the dark"

**The CTA**: "Scan the QR code - 30 minutes to set this up yourself"

---

## 🤖 The Six Bot Personalities

| Bot | Character | Demo Hook | Token Profile |
|-----|-----------|-----------|---------------|
| **HAL 9000** | Paranoid spaceship AI | "HAL over-diagnoses everything" | Medium-high |
| **Marvin** | Depressed robot | "Marvin's depression is EXPENSIVE" | Highest (verbose) |
| **Bender** | Alcoholic robot | "Creative insults cost tokens" | High |
| **GLADOS** | Sadistic AI | "GLADOS loves deploying turrets" | Medium-high |
| **JARVIS** | Efficient assistant | "Tony Stark doesn't waste money" | Lowest (concise) |
| **Cortana** | Tactical AI | "All analysis, barely needs tools" | Low-medium |

**Demo Tip**: Reference bots by personality trait, not "agent 3" - more memorable!

---

## 📊 Key Numbers to Memorize

- **6** bot personalities
- **39** custom tools (across 6 tool sets)
- **3.3x** cost variance (Marvin vs JARVIS)
- **$0.0002-0.001** per query
- **30 minutes** setup time
- **100 lines** of instrumentation code

---

## 🎯 Talk Timing Breakdown

| Time | Section | What to Show |
|------|---------|--------------|
| 0:00-2:00 | Setup + Problem | Slides only |
| 2:00-3:30 | Happy Path Demo | HAL + pod bay doors |
| 3:30-5:00 | Chaos Demo | Bot comparison, failed traces |
| 5:00-7:30 | Takeaways + How | Slides with key insights |
| 7:30-8:00 | Call to Action | QR codes |
| 8:00-10:00 | Q&A | Open floor |

**If running behind**: Skip "How it works" slide (slide 7)
**If running ahead**: Show more bot examples (Marvin, Bender)

---

## 🛡️ Backup Plan (If Demo Fails)

**Say**: "Even HAL crashes sometimes - this is why we need observability!"

**Do**:
1. Switch to backup screenshots (in ~/demo-screenshots/)
2. Walk through the same story with static images
3. Make it part of the narrative: "See? Stuff fails. That's why tracing matters."

Pre-capture these screenshots:
- `happy-path-hal.png` - Clean HAL trace
- `bot-comparison.png` - Bar chart of all 6 bots
- `failed-trace.png` - Error with 0 response chars
- `openwebui-interface.png` - UI with HAL selected

---

## ❓ Common Questions You'll Get

**"Does this work with [other framework]?"**
→ Yes! Framework-agnostic. LangChain, LlamaIndex, CrewAI, AutoGen all supported.

**"What about [other LLM provider]?"**
→ Works with ALL providers (OpenAI, Anthropic, Gemini, etc). Token metadata is universal.

**"Isn't this logging sensitive data?"**
→ Use OTEL attribute filtering to drop prompts/responses, keep metadata only.

**"Cost of Grafana Cloud?"**
→ Free tier = 50GB/month. Cost of observability << cost of inefficient bots.

**"What about streaming?"**
→ Yes! Captures spans when stream completes. Full tokens + latency.

---

## 💡 Pro Tips from Other Speakers

✅ **Reference bots by name** - "HAL is paranoid" is more engaging than "agent 1 uses more tokens"

✅ **Type slowly during demo** - Let audience read what you're typing

✅ **Zoom in on Grafana** - 125-150% browser zoom for readability

✅ **Point at specific numbers** - Use mouse to highlight tokens, cost, latency

✅ **Keep energy HIGH** - Robot personalities are inherently fun, use them!

✅ **Practice the opening hook** - First 30 seconds sets the tone

✅ **Memorize the closing** - Last impression matters

❌ **Don't read slides** - Talk to audience, glance at slides

❌ **Don't apologize for demo failures** - Make it part of the story

❌ **Don't go over time** - Respect the 10-minute limit

---

## 🎨 Slide Design Notes

If creating your own slides:

**Visuals**:
- Bot avatars/icons for each personality
- Architecture diagram (OpenWebUI → OTEL → Grafana)
- Split screen: "What you built" vs "What's actually happening"
- Use Grafana orange (#FF8C00) for observability theme

**Fonts**:
- Large and bold for headers
- Readable from back of room
- Use monospace for code/queries

**Demo Layout**:
- 50/50 split: OpenWebUI left, Grafana right
- OR full-screen Grafana for dashboard panels

---

## 📞 Last-Minute Help

**Services won't start:**
```bash
docker compose down
docker compose up -d
```

**No traces in Grafana:**
- Check `.env` for correct GRAFANA_OTLP_TOKEN
- Wait 60-90 seconds for initial export
- Test query: `{ resource.service.name = "openwebui" }`

**Bots not responding:**
- Check GEMINI_API_KEY in `.env`
- Check logs: `docker logs openwebui-instrumented`

**Tools not showing up:**
- Use the UI, not direct API (OpenWebUI limitation)
- Verify bot has tools assigned in Admin panel

---

## 🎓 After Your Talk

**Share the repo**: https://github.com/YOUR-USERNAME/open-webui

**Grafana Cloud trial**: https://grafana.com/get

**OpenInference spec**: https://github.com/Arize-ai/openinference

**Follow up**: Offer to help anyone who wants to implement this

---

## 🎤 You've Got This!

Remember:
- The bots are entertaining - use their personalities!
- The demo is the hero - let the data tell the story
- If something fails, make it part of the narrative
- High energy, have fun, enjoy the 10 minutes!

**Questions?** Check the other files in this folder or ping the Solutions Engineering team.

**Good luck! 🤖🚀**
