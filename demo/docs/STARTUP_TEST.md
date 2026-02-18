# 🚀 Demo Startup Test Guide

## Prerequisites

### Enable Docker in WSL2

Your Docker Desktop needs WSL2 integration enabled:

1. **Open Docker Desktop** (Windows)
2. Go to **Settings** → **Resources** → **WSL Integration**
3. **Enable** "Enable integration with my default WSL distro"
4. **Enable** your specific distro (Ubuntu/Debian)
5. Click **Apply & Restart**

### Verify Docker Works

```bash
# In WSL2 terminal
docker --version
docker compose version
```

Should show Docker version 20+ and Compose version 2+.

---

## 🧪 Complete Startup Test

Run these commands step-by-step to verify everything works:

### Step 1: Start the Stack

```bash
cd ~/git_repos/open-webui/demo

# Verify .env is configured
echo "Checking environment..."
cat .env | grep -E "GEMINI_API_KEY|GRAFANA_OTLP_TOKEN|OTEL_EXPORTER" | wc -l
# Should show "3" (all three vars present)

# Start services
echo "Starting docker stack..."
docker compose up -d

# Wait for services to initialize (30 seconds)
echo "Waiting 30 seconds for services to start..."
sleep 30

# Check services are running
docker compose ps
```

**Expected output**:
```
NAME                     IMAGE                          STATUS
openwebui-instrumented   openwebui-instrumented:latest  Up
otel-collector           otel/opentelemetry-collector   Up
```

### Step 2: Verify OpenWebUI Access

```bash
# Test HTTP endpoint
curl -s http://localhost:3000/health || echo "OpenWebUI not ready yet"

# Open in browser
echo "Open this URL in your browser:"
echo "http://localhost:3000"
```

**Manual step**:
1. Open http://localhost:3000 in browser
2. Sign up with email/password (first user becomes admin)
3. Log in

### Step 3: Run Bot Setup Script

```bash
cd ~/git_repos/open-webui/demo

# Run setup (will prompt for credentials)
python3 setup-bots.py
```

**What this does**:
- ✅ Configures Gemini API connection (from .env)
- ✅ Imports 6 tool sets (39 total functions)
- ✅ Imports 6 bot personalities (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)
- ✅ Links tools to bots

**Expected output**:
```
✅ Admin config updated successfully
✅ Tool 'HAL 9000 System Tools' created with ID: xxx
✅ Tool 'Marvin Tools' created with ID: xxx
...
✅ Model 'hal' created with ID: xxx
✅ Model 'marvin' created with ID: xxx
...
🎉 Setup complete!
```

### Step 4: Verify Bots in UI

**Manual verification**:
1. Go to http://localhost:3000
2. Click the model dropdown (top of chat interface)
3. **Should see**: HAL 9000, Marvin, Bender, GLADOS, JARVIS, Cortana

✅ **Success!** If you see all 6 bots, setup worked!

### Step 5: Generate Test Traces

```bash
cd ~/git_repos/open-webui/demo

# Generate 30-50 test traces
python3 load-gen-bots.py
```

**Expected output**:
```
🚀 Starting OpenWebUI bot load generation
📊 Target: 15 queries per bot
🤖 Bots: hal, marvin, bender, glados, jarvis, cortana

[12:34:56] 🤖 HAL     → HAL, what's the status of the pod bay doors? ✅
[12:34:58] 🤖 MARVIN  → Marvin, how are you feeling? ✅
[12:35:00] 🤖 BENDER  → Bender, what do you think of humans? ✅
...

✅ Load generation complete!
📊 Total queries: 90
✅ Successful: 85 (94.4%)
❌ Failed: 5
```

**Wait 60 seconds** for traces to export to Grafana Cloud.

### Step 6: Verify Traces in Grafana

1. **Open Grafana Cloud** → **Explore** → **Tempo**
2. **Set time range**: Last 15 minutes
3. **Query**:
   ```traceql
   { span.openinference.span.kind = "LLM" }
   ```
4. **Click Search**

**Expected result**: You should see 85+ traces from the last few minutes

**Click into a trace** and verify these attributes exist:
- `span.llm.model_name` (e.g., "hal", "marvin")
- `span.llm.token_count.total` (e.g., 275)
- `span.llm.tool_calls.count` (may be 0 for API-generated traces)
- `span.llm.provider` (e.g., "gemini")

### Step 7: Test Live Bot Interaction

**Manual test** (tool calls only work via UI):

1. Go to http://localhost:3000
2. Select **HAL 9000** from model dropdown
3. Type: `HAL, what's the status of the pod bay doors?`
4. Send message
5. Wait for HAL's response (should reference pod bay doors)
6. Wait 30 seconds
7. Go to Grafana Tempo, refresh query
8. Find the trace with `span.llm.model_name = "hal"`
9. **Look for**: `span.llm.tool_calls.count > 0` (tool call should be present!)

✅ **Success criteria**: You see a trace with HAL + tool call (pod_bay_doors)

---

## 🎯 Demo Readiness Checklist

After completing all steps above, verify:

- [ ] Docker services running (`docker compose ps` shows 2 services)
- [ ] OpenWebUI accessible at http://localhost:3000
- [ ] 6 bots visible in model dropdown
- [ ] Test traces in Grafana (85+ traces from load-gen)
- [ ] Live bot interaction works (HAL responds)
- [ ] Tool calls instrumented (HAL trace has tool_calls.count > 0)

---

## 🐛 Troubleshooting

### Docker not found in WSL2
```bash
# Check Docker Desktop WSL integration
# Settings → Resources → WSL Integration → Enable

# Restart WSL
wsl.exe --shutdown
# Then reopen WSL terminal
```

### Port 3000 already in use
```bash
# Find what's using port 3000
sudo lsof -i :3000

# Kill it or change port in docker-compose.yml
```

### OpenWebUI container crashes
```bash
# Check logs
docker logs openwebui-instrumented

# Common issues:
# - Port conflict
# - Permission issues
# - Invalid .env configuration
```

### No traces in Grafana
```bash
# Check OTEL collector logs
docker logs otel-collector

# Verify .env credentials
echo $GRAFANA_OTLP_TOKEN | base64 -d
# Should decode to: instance_id:token

# Check endpoint in .env matches your Grafana Cloud region
cat .env | grep OTEL_EXPORTER_OTLP_ENDPOINT
```

### Bots not responding
```bash
# Check Gemini API key
cat .env | grep GEMINI_API_KEY

# Check OpenWebUI logs for API errors
docker logs openwebui-instrumented | tail -50
```

### Tool calls not appearing
- **Important**: Tool calls ONLY work through the UI, not API
- Direct API calls won't include bot tools (OpenWebUI limitation)
- Use the UI at http://localhost:3000 to see tool calls

---

## 📊 Success Metrics

You're ready for demo/sharing when:

✅ **All 6 bots respond** (test each one quickly)
✅ **85+ traces in Grafana** (from load-gen)
✅ **At least 1 trace with tool calls** (HAL via UI)
✅ **Cost variance visible** (query: `| count by span.llm.model_name`)
✅ **Token counts captured** (check any trace for token attributes)

---

## 🚀 Ready to Share

Once all checks pass, your demo is ready for:
- ✅ Team SE demos
- ✅ Customer presentations
- ✅ Lightning talks
- ✅ Internal training

**Next steps**:
1. Practice your demo flow (LIGHTNING_TALK.md)
2. Take backup screenshots (TALK_PREP.md)
3. Share GitHub repo with team

**Questions?** Check other docs in `demo/` folder.
