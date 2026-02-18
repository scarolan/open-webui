#!/usr/bin/env bats
# Telemetry tests — validate tracing pipeline
# OTEL Collector ports are internal-only, so we use docker compose exec.

DEMO_DIR="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
COMPOSE="docker compose -f $DEMO_DIR/docker-compose.yml"

setup() {
  if [ -f "$DEMO_DIR/.env" ]; then
    set -a
    source "$DEMO_DIR/.env"
    set +a
  fi
  OPENWEBUI_URL="http://localhost:3000"
  OPENWEBUI_EMAIL="${OPENWEBUI_EMAIL:-team-se@grafana.com}"
  OPENWEBUI_PASSWORD="${OPENWEBUI_PASSWORD:-open-sesame}"
}

get_token() {
  curl -s -X POST "$OPENWEBUI_URL/api/v1/auths/signin" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$OPENWEBUI_EMAIL\",\"password\":\"$OPENWEBUI_PASSWORD\"}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null
}

@test "LLM request returns usage data" {
  token=$(get_token)
  response=$(curl -s -X POST "$OPENWEBUI_URL/api/chat/completions" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d '{"model":"hal","messages":[{"role":"user","content":"Status report."}],"stream":false}' \
    --max-time 60)
  echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
usage = d.get('usage', {})
assert usage.get('total_tokens', 0) > 0, 'No token usage in response'
"
}

@test "OTEL Collector is running" {
  run $COMPOSE ps --format json otel-collector
  echo "$output" | grep -q '"State":"running"'
}

@test "OTEL Collector logs show span export" {
  run $COMPOSE logs otel-collector --tail 50
  # Collector debug exporter logs exported spans
  echo "$output" | grep -qi "trace\|span\|export"
}
