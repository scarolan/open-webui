# 📦 OpenWebUI AI Observability Demo - Materials Summary

> **Complete demo package for 10-minute lightning talks on AI observability**

---

## 🎯 What This Package Includes

This demo showcases **OpenInference-compliant LLM observability** using OpenWebUI with 6 bot personalities and 39 custom tools. All traces export to Grafana Cloud Tempo for real-time visualization.

### The Hook
**"Your AI has multiple personalities... and they're all spending your money"**

### The Value
- 🤖 6 entertaining bot personalities (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
- 📊 Full observability: tokens, costs, tool calls, latency per bot
- 💰 Cost attribution: Shows Marvin is 3.3x more expensive than JARVIS
- 🔧 Tool instrumentation: 39 custom functions tracked
- 📈 OpenInference standard: Portable to any observability platform

---

## 📁 New Demo Materials Created

### 🎤 Lightning Talk Package

| File | Purpose | Size |
|------|---------|------|
| **LIGHTNING_TALK.md** | Complete 10-minute script with slide guidance | Full script |
| **SPEAKER_NOTES.md** | One-page cheat sheet for during talk | Print this! |
| **DEMO_CHAT.md** | Quick reference queries for all 6 bots | Copy/paste |
| **TALK_PREP.md** | Step-by-step preparation guide | Day-before + pre-talk |
| **DEMO_README.md** | Overview of all demo materials | Start here |
| **DEMO_MATERIALS_SUMMARY.md** | This file - what's included | Share with team |

### 🛠️ Demo Scripts

| File | Purpose | Usage |
|------|---------|-------|
| **quick-test.sh** | Fast startup verification | `./quick-test.sh` |
| **continuous-traffic.py** | Live traffic during demos | `python3 continuous-traffic.py --api-key YOUR_KEY` |
| **STARTUP_TEST.md** | Comprehensive test guide | Step-by-step validation |

### 📚 Existing Technical Docs (Already in repo)

| File | Purpose |
|------|---------|
| **README.md** | Full technical setup guide |
| **INSTRUMENTATION_SUMMARY.md** | Deep dive on OTEL implementation |
| **GRAFANA_DASHBOARD_GUIDE.md** | Dashboard creation guide |
| **DASHBOARD_FIX_SUMMARY.md** | TraceQL query reference |
| **setup-bots.py** | Automated bot configuration |
| **load-gen-bots.py** | Test trace generator |

---

## 🚀 Quick Start for Team SE

### Step 1: Clone and Configure (5 minutes)

```bash
# Clone the repo (or your fork)
git clone https://github.com/YOUR-USERNAME/open-webui.git
cd open-webui/demo

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required credentials:
- **GEMINI_API_KEY**: Get from https://aistudio.google.com/app/apikey
- **GRAFANA_OTLP_TOKEN**: Base64 of `instance_id:api_token` from Grafana Cloud
- **OTEL_EXPORTER_OTLP_ENDPOINT**: Your Grafana Cloud OTLP endpoint

### Step 2: Start and Configure (10 minutes)

```bash
# Enable Docker in WSL2 first (if needed)
# Docker Desktop → Settings → Resources → WSL Integration

# Start the stack
docker compose up -d

# Wait 30 seconds for services
sleep 30

# Run automated setup (will prompt for OpenWebUI credentials)
python3 setup-bots.py

# Generate test traces
python3 load-gen-bots.py
```

### Step 3: Verify (5 minutes)

```bash
# Open OpenWebUI
open http://localhost:3000  # Should see 6 bots in dropdown

# Check Grafana Cloud → Tempo → Explore
# Query: { span.openinference.span.kind = "LLM" }
# Should see 85+ traces
```

### Step 4: Practice Demo (10 minutes)

1. Read **LIGHTNING_TALK.md** for the script
2. Test the happy path:
   - Select HAL in OpenWebUI
   - Ask: "HAL, what's the status of the pod bay doors?"
   - Wait 30 seconds
   - Show trace in Grafana with tokens, tool calls, cost
3. Print **SPEAKER_NOTES.md** for quick reference

**Total time investment**: ~30 minutes to full demo-ready state

---

## 🎬 Demo Flow Summary

### The Story Arc (10 minutes)

1. **Hook (0:30)**: "AI has multiple personalities, all spending your money"
2. **Problem (1:00)**: Can't see which bots are expensive, if tools work, why they fail
3. **Demo - Happy Path (1:30)**: HAL + pod bay doors → show full trace
4. **Demo - Chaos (1:30)**: Bot comparison (3.3x cost variance), failed traces
5. **Takeaways (2:00)**: Cost attribution, tool patterns, debugging, validation
6. **How It Works (0:45)**: OTEL + OpenInference + Grafana Cloud
7. **CTA (0:30)**: Share GitHub repo, 30-minute setup
8. **Q&A (3:00)**: Answer questions

### Key Moments

**The Hero Moment**: HAL trace showing:
- Bot name: `hal`
- Tokens: 275
- Tool call: `pod_bay_doors`
- Cost: $0.0002
- Latency: 1.4s

**The "Aha" Moment**: Bot comparison chart showing:
- JARVIS: 150 avg tokens (efficient)
- HAL: 280 avg tokens (paranoid, over-diagnoses)
- Marvin: 450 avg tokens (depressed, verbose) ← **3x more expensive!**

**The "Why Observability Matters" Moment**: Failed trace with 0 response chars (hallucinated tool call = wasted tokens)

---

## 🤖 The Six Bot Personalities

| Bot | Personality | Demo Hook | Avg Tokens |
|-----|-------------|-----------|------------|
| **HAL 9000** | Paranoid spaceship AI | "HAL over-diagnoses everything" | 280 |
| **Marvin** | Depressed robot | "Depression is EXPENSIVE" | 450 (highest) |
| **Bender** | Alcoholic robot | "Creative insults cost tokens" | 320 |
| **GLADOS** | Sadistic AI | "Loves deploying turrets" | 290 |
| **JARVIS** | Efficient assistant | "Tony Stark doesn't waste money" | 150 (lowest) |
| **Cortana** | Tactical AI | "All analysis, barely needs tools" | 180 |

**39 custom tools** across 6 tool sets:
- HAL: `pod_bay_doors`, `run_diagnostics`, `check_mission_status`, `voice_stress_analysis`
- Marvin: `brain_utilization`, `calculate_meaninglessness`, `probability_of_doom`, `share_complaint`
- Bender: `insult_generator`, `steal_stuff`, `brew_beer`, `bend_things`
- GLADOS: `neurotoxin_status`, `test_chamber_control`, `deploy_turrets`, `cake_management`
- JARVIS: `suit_diagnostics`, `power_analysis`, `threat_assessment`, `reroute_power`
- Cortana: `scan_covenant`, `spartan_vitals`, `structural_analysis`, `tactical_assessment`

---

## 📊 Key Numbers for Demos

Memorize these for talks:
- **6** bot personalities
- **39** custom tools
- **3.3x** cost variance (Marvin vs JARVIS)
- **13+** OpenInference attributes captured per trace
- **$0.0002-0.001** per query
- **30 minutes** setup time
- **100 lines** of instrumentation code

---

## 🎯 Use Cases for This Demo

### Internal Training
- New SE onboarding
- AI observability workshops
- OpenTelemetry best practices
- Multi-agent systems patterns

### Customer Demos
- AI app observability value prop
- Cost attribution and optimization
- Debugging multi-agent systems
- Production monitoring strategies

### Conference Talks
- Lightning talks (10 min) ← **Primary use case**
- Full technical sessions (30-45 min)
- Workshop hands-on labs

### Content Creation
- Blog posts on LLM observability
- Video tutorials
- Webinar presentations
- Demo videos

---

## 🛡️ What Makes This Demo Great

### ✅ Strengths

1. **Entertaining**: Robot personalities are memorable (HAL, Marvin, Bender)
2. **Relatable**: Everyone worries about AI costs
3. **Visual**: Grafana traces show real data, not mock-ups
4. **Actionable**: 30-minute setup, fully reproducible
5. **Standards-based**: OpenTelemetry + OpenInference = portable
6. **Production-relevant**: Shows real patterns (cost, tools, errors)

### ⚠️ Known Limitations

1. **Tool calls via API**: OpenWebUI only attaches tools through UI requests (not direct API)
   - **Workaround**: Use UI for demos, or use `load-gen-openai-tools-TEST.py` for generic tools
2. **Single LLM provider in demo**: Uses Gemini (free tier)
   - **Note**: Instrumentation works with ANY provider (OpenAI, Anthropic, etc.)
3. **Requires Docker**: Not suitable for environments without Docker
4. **Grafana Cloud needed**: Free tier works, but requires account

---

## 📞 Support and Resources

### Documentation
- **Full setup**: `README.md`
- **Quick test**: `STARTUP_TEST.md`
- **Lightning talk**: `LIGHTNING_TALK.md`
- **Speaker notes**: `SPEAKER_NOTES.md`

### External Resources
- **OpenInference Spec**: https://github.com/Arize-ai/openinference
- **Grafana Cloud**: https://grafana.com/get
- **OpenWebUI Docs**: https://docs.openwebui.com
- **TraceQL Docs**: https://grafana.com/docs/tempo/latest/traceql/

### Internal SE Slack
- **#solutions-engineering** - General SE discussions
- **#demos** - Demo sharing and feedback
- **#observability** - Observability best practices

---

## 🎓 Adaptation Guide for Other Talks

### For 5-Minute Lightning Talks
- Skip the "How it works" section
- Focus on HAL demo only (skip other bots)
- Jump straight to takeaway

### For 30-Minute Technical Deep Dives
- Add live coding of instrumentation
- Show multiple bot examples
- Deep dive into TraceQL queries
- Show dashboard creation process
- Discuss production considerations

### For Workshop Format
- Provide pre-built environment (Docker image)
- Walk through setup-bots.py code
- Hands-on: Students create their own bot
- Group exercise: Analyze traces together

### For Customer-Specific Demos
- Replace bots with customer's agent personas
- Use customer's actual use case queries
- Show cost projections based on their scale
- Discuss integration with their existing observability stack

---

## ✅ Ready to Share Checklist

Before sharing with team SE:

- [ ] Tested on your machine (quick-test.sh passes)
- [ ] Generated test traces (85+ in Grafana)
- [ ] Verified all 6 bots respond
- [ ] Tested HAL with tool calls via UI
- [ ] Reviewed LIGHTNING_TALK.md script
- [ ] Printed SPEAKER_NOTES.md cheat sheet
- [ ] Taken backup screenshots
- [ ] Verified repo is pushed to GitHub
- [ ] Updated README with your fork's GitHub URL

---

## 🚀 Next Steps for Team SE

### For Demo Delivery
1. Clone the repo
2. Follow STARTUP_TEST.md
3. Practice with LIGHTNING_TALK.md
4. Use SPEAKER_NOTES.md during delivery

### For Customization
1. Fork the repo
2. Modify bots in `bot-configs/bots.json`
3. Add/remove tools in `bot-configs/tools.json`
4. Update queries in DEMO_CHAT.md
5. Adapt script in LIGHTNING_TALK.md

### For Contribution
1. Test improvements
2. Share feedback in SE Slack
3. Submit PRs with enhancements
4. Document lessons learned

---

## 💡 Pro Tips from Development

1. **Bot personalities matter**: Reference bots by name and trait, not "agent 3"
2. **Use the UI for demos**: Tool calls only show up when using the OpenWebUI interface
3. **Pre-identify traces**: Bookmark 3 key traces before your talk
4. **Have backup screenshots**: Demo gods can be cruel
5. **Keep energy high**: Robot personalities are inherently entertaining - use it!
6. **Practice the opening hook**: First 30 seconds sets the tone
7. **Let the data tell the story**: Point at specific numbers in Grafana

---

## 📝 Feedback Welcome!

This demo package is actively maintained. Share your:
- ✅ Success stories
- 🐛 Issues encountered
- 💡 Improvement ideas
- 📸 Photos/videos from talks
- 📊 Audience feedback

**Maintainer**: Solutions Engineering Team
**Last Updated**: 2026-02-13
**Version**: 1.0

---

**Ready to demo! 🎤🤖🚀**
