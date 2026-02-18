# 🎬 Lightning Talk Prep Guide

> **Goal**: Have everything ready 30 minutes before your talk

---

## 📋 Day-Before Checklist

### 1. Test Your Environment (15 minutes)

```bash
# Clone/pull latest
cd ~/git_repos/open-webui/demo

# Make sure .env is configured
cat .env | grep -E "GEMINI_API_KEY|GRAFANA_OTLP"
# Should show your keys - if not, edit .env

# Start stack
docker compose up -d

# Wait 30 seconds, then check services
docker ps
# Should see: openwebui-instrumented, otel-collector

# Open http://localhost:3000
# Sign up / log in

# Run setup script
python3 setup-bots.py
# Enter your email/password
# Wait for success messages

# Verify bots appear in model dropdown
# Should see: HAL 9000, Marvin, Bender, GLADOS, JARVIS, Cortana
```

### 2. Generate Test Data (5 minutes)

```bash
# Generate 30-50 traces across all bots
python3 load-gen-bots.py

# Wait 60 seconds for traces to propagate to Grafana Cloud

# Open Grafana → Explore → Tempo
# Query: { span.openinference.span.kind = "LLM" }
# Should see traces from all 6 bots
```

### 3. Pre-Identify Key Traces (10 minutes)

Open Grafana Cloud Tempo and bookmark these traces:

#### Trace 1: Clean HAL Query (Happy Path)
```traceql
{ span.llm.model_name = "hal" && span.llm.tool_calls.count = 1 }
```
- Find one with `pod_bay_doors` tool call
- Bookmark it or note the trace ID
- This is your **main demo trace**

#### Trace 2: Bot Comparison Data
```traceql
{ span.openinference.span.kind = "LLM" }
| count by span.llm.model_name
```
- Screenshot the bar chart showing all 6 bots
- Save as `backup-bot-comparison.png`

#### Trace 3: Failed/Error Trace (if available)
```traceql
{ span.llm.token_count.completion = 0 }
```
- Find one with 0 response chars (hallucinated tool call)
- Bookmark it
- Great for showing "why observability matters"

### 4. Prepare Browser Tabs (5 minutes)

Set up your demo browser (Chrome/Firefox):

**Tab 1: OpenWebUI**
- http://localhost:3000
- Logged in
- HAL 9000 selected in model dropdown
- Ready to type "HAL, what's the status of the pod bay doors?"

**Tab 2: Grafana Tempo - Explore**
- Your Grafana Cloud instance
- Tempo data source selected
- Time range: Last 15 minutes
- Query ready: `{ span.openinference.span.kind = "LLM" }`

**Tab 3: Grafana Tempo - Bot Comparison Dashboard** (optional)
- Pre-built query showing bot usage bar chart
- `{ span.openinference.span.kind = "LLM" } | count by span.llm.model_name`

**Tab 4: Backup Screenshots** (local file browser)
- Open folder with backup screenshots
- In case live demo fails

### 5. Take Backup Screenshots (10 minutes)

In case the demo gods are angry:

```bash
mkdir -p ~/demo-screenshots
```

Screenshot these and save:
1. **happy-path-hal.png**: Clean HAL trace with pod_bay_doors tool call
2. **bot-comparison.png**: Bar chart showing all 6 bots
3. **tool-usage-timeline.png**: Time series of tool calls over time
4. **failed-trace.png**: Example of 0 response chars error
5. **openwebui-interface.png**: OpenWebUI with HAL selected

---

## ⏰ 30 Minutes Before Talk

### Final Checks:

- [ ] Docker stack running: `docker ps`
- [ ] OpenWebUI accessible: http://localhost:3000
- [ ] Grafana Cloud accessible (test login)
- [ ] Test traces visible in Grafana (last 15 mins)
- [ ] Browser tabs set up (OpenWebUI + Grafana)
- [ ] Backup screenshots ready
- [ ] Phone on silent / airplane mode
- [ ] Water bottle nearby
- [ ] Speaker notes printed or on second device

### Quick Smoke Test:

1. Send a test query to HAL: "Hello HAL"
2. Wait 30 seconds
3. Check Grafana - should see new trace appear
4. If yes → you're good to go!
5. If no → check OTEL config, restart services

---

## 🎤 5 Minutes Before Talk

### Mental Prep:

1. Read your opening hook (memorize it)
2. Read your closing takeaway (memorize it)
3. Breathe deeply 3 times
4. Remember: The bots are entertaining, use them!
5. If demo fails, joke about it and use backup screenshots

### Physical Prep:

- [ ] Laptop plugged in (not on battery)
- [ ] Screen sharing tested
- [ ] Browser zoom level good (125-150% for readability)
- [ ] Speaker notes accessible
- [ ] Backup device with screenshots ready
- [ ] Water nearby
- [ ] Stand/sit in comfortable position

---

## 🎬 During Talk

### Timing Guide:

| Minute | Slide/Action | Notes |
|--------|--------------|-------|
| 0-0:30 | Opening hook | Poll the audience |
| 0:30-1:30 | Pain points | Build the problem |
| 1:30-2:00 | Intro 6 bots | Set the stage |
| **2:00-2:15** | **Open OpenWebUI** | **Switch to demo** |
| **2:15-2:30** | **Ask HAL about pod bay doors** | **Type slowly** |
| **2:30-3:00** | **Switch to Grafana** | **Show the trace** |
| 3:00-3:30 | Deep dive trace details | Point out tokens, tools, cost |
| 3:30-4:00 | Show bot comparison | Highlight cost variance |
| 4:00-4:30 | Show tool patterns | HAL over-diagnoses |
| 4:30-5:00 | Show failed trace | 0 chars example |
| 5:00-7:30 | Back to slides | Takeaways, how it works |
| 7:30-8:00 | Call to action | QR codes |
| 8:00-10:00 | Q&A | You got this! |

### If You're Running Behind:

- Skip slide 7 (how it works) - not critical
- Keep demo focused on HAL only (skip other bots)
- Jump straight to takeaway slide

### If You're Running Ahead:

- Show more bot examples (Marvin, Bender)
- Show tool usage timeline in Grafana
- Add more commentary during trace deep dive

---

## 🛡️ Troubleshooting During Talk

### Demo Fails - No Traces Appearing:

**Say**: "And THIS is why we need observability - even my demo has bad days!"

**Do**:
1. Switch to backup screenshots
2. Walk through the same story with static images
3. Make it part of the narrative ("See, stuff fails - that's why tracing matters")

### Browser Crashes:

**Do**:
1. Stay calm, crack a joke: "Even HAL crashes sometimes"
2. Reopen browser tabs (should still be in history)
3. Continue with backup screenshots if needed

### Grafana Query Takes Forever:

**Do**:
1. Pre-load queries in multiple tabs
2. Switch to backup screenshots
3. Say: "While this loads, let me show you what we saw earlier..."

### Forgot What to Say:

**Do**:
1. Glance at speaker notes on phone/second screen
2. Use transition phrase: "Now here's the interesting part..."
3. Remember the structure: Pain → Demo → Superpowers → Takeaway

---

## 📞 Emergency Contacts

Just in case:

- **Docker issues**: `docker compose restart` or `docker compose down && docker compose up -d`
- **Bot not responding**: Check Gemini API key in .env
- **No traces**: Check GRAFANA_OTLP_TOKEN in .env
- **OpenWebUI 500 error**: Check logs with `docker logs openwebui-instrumented`

---

## 🎯 Remember

**The One Thing**: The demo is the hero. Your job is to show why observability matters for multi-agent systems through real, entertaining bot personalities.

**Backup Plan**: If all else fails, you have screenshots and a great story about why observability matters (because stuff breaks!).

**Energy**: High! Robot personalities are fun - reference them by name, use their quirks, make it memorable.

**You've got this! 🤖🚀**

---

## ✅ Final Pre-Talk Checklist

Print this and check off:

- [ ] Docker running
- [ ] Bots configured (6 bots visible)
- [ ] Test data generated (30+ traces)
- [ ] Grafana accessible
- [ ] 3 key traces bookmarked
- [ ] Browser tabs ready
- [ ] Backup screenshots saved
- [ ] Speaker notes accessible
- [ ] Phone silent
- [ ] Water nearby
- [ ] Laptop plugged in
- [ ] Screen sharing tested
- [ ] Opening hook memorized
- [ ] Closing takeaway memorized
- [ ] Deep breath taken

**GO TIME! 🎤**
