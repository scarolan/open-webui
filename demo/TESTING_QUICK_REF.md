# Testing Quick Reference Card

> **One-page guide for running tests**

---

## 🚀 **Quick Commands**

```bash
# Run all unit tests (fast, no deps)
cd demo && ./run-tests.sh

# Run integration tests
docker compose up -d
./run-tests.sh --integration

# Run Tempo query tests
./run-tests.sh --tempo

# Run everything
./run-tests.sh --all -v
```

---

## 📋 **Before Testing**

### **One-Time Setup**:
```bash
# Install all dependencies (automated)
cd demo/tests/
./setup-tests.sh

# OR manually
cd ../../backend && pip install -e .
cd ../demo/tests && pip install -r requirements.txt
```

### **Set Environment Variables**:
```bash
# For integration tests
export TEST_EMAIL="your-email@example.com"
export TEST_PASSWORD="your-password"

# For Tempo query tests
export GRAFANA_TEMPO_URL="https://tempo-prod-us-east-0.grafana.net"
export GRAFANA_TEMPO_TOKEN="your-base64-token"
```

---

## 🧪 **Test Categories**

| Command | Tests | Time | Requires |
|---------|-------|------|----------|
| `./run-tests.sh` | Unit | <5s | Nothing |
| `./run-tests.sh --integration` | Integration | ~30s | OpenWebUI running |
| `./run-tests.sh --tempo` | Query validation | ~10s | Grafana + test data |
| `./run-tests.sh --all` | Everything | ~45s | All of above |

---

## 🎯 **Common Workflows**

### **Before Demo/Release**:
```bash
# 1. Start services
docker compose up -d

# 2. Run all tests
./run-tests.sh --all -v

# 3. Generate test data
python3 load-gen-bots.py
python3 load-gen-openai-tools-TEST.py

# 4. Wait and verify Tempo
sleep 60
./run-tests.sh --tempo
```

### **During Development**:
```bash
# After changing instrumentation code
./run-tests.sh --unit

# If tests pass, rebuild and test integration
docker compose build && docker compose up -d
./run-tests.sh --integration
```

### **Quick Smoke Test**:
```bash
# Just run unit tests
./run-tests.sh -v
```

---

## 🐛 **Troubleshooting**

### **Import errors**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../../backend"
```

### **Tests skipped**:
```bash
# Check credentials are set
env | grep TEST_
env | grep GRAFANA_

# Check OpenWebUI is running
docker compose ps
curl http://localhost:3000/health
```

### **No traces found**:
```bash
# Generate test data
python3 load-gen-bots.py
sleep 60
./run-tests.sh --tempo
```

---

## 📖 **More Info**

- **Detailed docs**: `demo/tests/README.md`
- **Test summary**: `demo/tests/TEST_SUMMARY.md`
- **Main docs**: `CLAUDE.md`

---

## ✅ **Test Pass Criteria**

**All green means**:
- ✅ Instrumentation code works correctly
- ✅ Traces are created end-to-end
- ✅ Dashboard queries return results
- ✅ Ready for demo/production

---

**Last updated**: 2026-02-11
