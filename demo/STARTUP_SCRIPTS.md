# 🚀 Startup Scripts Guide

Quick reference for the demo startup scripts.

---

## 📁 Available Scripts

### **start-demo.sh** ⭐ RECOMMENDED
**Complete end-to-end startup with helpful guidance**

**What it does**:
- ✅ Detects OS (macOS/Linux)
- ✅ Checks Docker is installed and running
- ✅ Validates .env configuration
- ✅ Starts docker-compose services
- ✅ Waits for services to be ready
- ✅ Tests OpenWebUI endpoint
- ✅ Shows next steps with copy/paste commands

**Usage**:
```bash
cd ~/git_repos/open-webui/demo
./start-demo.sh
```

**Best for**: First-time setup, team onboarding, demo prep

---

### **quick-test.sh**
**Fast verification that services are running**

**What it does**:
- ✅ Checks Docker
- ✅ Validates .env
- ✅ Starts services
- ✅ Quick health check

**Usage**:
```bash
cd ~/git_repos/open-webui/demo
./quick-test.sh
```

**Best for**: Quick check before a demo, debugging

---

## 🎯 Which Script to Use?

| Scenario | Use This | Why |
|----------|----------|-----|
| **First time setup** | `start-demo.sh` | Full guidance + next steps |
| **Team onboarding** | `start-demo.sh` | Clear instructions for new users |
| **Before a demo** | `quick-test.sh` | Fast verification |
| **Debugging issues** | `quick-test.sh` | Minimal output |
| **Daily development** | `docker compose up -d` | Direct control |

---

## 📋 Complete Setup Flow

### Full Setup (First Time)

```bash
cd ~/git_repos/open-webui/demo

# 1. Configure environment
cp .env.example .env
nano .env  # Add your credentials

# 2. Start services
./start-demo.sh

# 3. Configure bots (opens browser for you on Mac)
python3 setup-bots.py

# 4. Generate test data
python3 load-gen-bots.py

# 5. Verify in Grafana Cloud
# Query: { span.openinference.span.kind = "LLM" }
```

**Total time**: ~10 minutes

---

### Quick Restart (Already Configured)

```bash
cd ~/git_repos/open-webui/demo

# Start services
./quick-test.sh

# Or just use docker compose directly
docker compose up -d
```

**Total time**: ~30 seconds

---

## 🖥️ Platform-Specific Notes

### macOS
- ✅ Scripts work out of the box
- Use `open http://localhost:3000` to launch browser
- Docker Desktop must be running

### Linux
- ✅ Scripts work out of the box
- Use `xdg-open http://localhost:3000` or just paste URL in browser
- Docker must be installed and daemon running

### Windows (WSL2)
- ✅ Scripts work in WSL2 terminal
- Docker Desktop WSL integration must be enabled
- Docker Desktop must be running on Windows host
- Access UI at http://localhost:3000 from Windows browser

---

## 🔧 Manual Commands (Alternative)

If you prefer not to use the scripts:

### Start Services
```bash
docker compose up -d
```

### Check Status
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f
```

### Stop Services
```bash
docker compose down
```

### Restart Services
```bash
docker compose restart
```

---

## 🐛 Troubleshooting

### "Docker not found"
**macOS/Windows**: Install Docker Desktop
**Linux**: Install Docker Engine

### "Docker daemon not running"
**macOS**: Start Docker Desktop app
**Windows**: Start Docker Desktop
**Linux**: `sudo systemctl start docker`

### ".env file not found"
```bash
cp .env.example .env
nano .env
```

### "Port 3000 already in use"
```bash
# Find what's using the port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Change port in docker-compose.yml or kill the process
```

### Services start but OpenWebUI not responding
```bash
# Wait a bit longer (can take 60s on first start)
docker logs openwebui-instrumented

# Common issues:
# - Still initializing (wait)
# - Port conflict (change port)
# - Invalid .env (check credentials)
```

---

## ✅ Success Indicators

After running `start-demo.sh`, you should see:

```
✅ Docker found: Docker version 24.x.x
✅ Docker daemon is running
✅ .env is properly configured
✅ Services started
✅ Services should be ready
✅ Core services are running
✅ OpenWebUI is responding at http://localhost:3000
```

If you see all green checkmarks, you're good to go!

---

## 📖 Next Steps After Startup

Once services are running:

1. **Configure Bots**:
   ```bash
   python3 setup-bots.py
   ```

2. **Generate Test Traces**:
   ```bash
   python3 load-gen-bots.py
   ```

3. **Test Live Interaction**:
   - Open http://localhost:3000
   - Select HAL from model dropdown
   - Ask: "HAL, what's the status of the pod bay doors?"

4. **View Traces**:
   - Go to Grafana Cloud → Tempo
   - Query: `{ span.openinference.span.kind = "LLM" }`

---

## 🎤 Demo Day Quick Check

**5 minutes before your demo**:

```bash
cd ~/git_repos/open-webui/demo

# Quick verification
./quick-test.sh

# Open OpenWebUI
open http://localhost:3000  # macOS
# or just go to http://localhost:3000 in browser

# Test HAL is responding
# (Do a quick query in the UI)

# Check Grafana has traces
# (Open Grafana Cloud → Tempo → search for recent traces)
```

✅ **If all checks pass, you're demo-ready!**

---

**Pro tip**: Run `start-demo.sh` once the day before your talk, then just use `quick-test.sh` right before presenting.
