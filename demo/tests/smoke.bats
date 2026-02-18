#!/usr/bin/env bats
# Smoke tests — validate a running demo stack

DEMO_DIR="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"

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

@test "OpenWebUI container is running" {
  run docker compose -f "$DEMO_DIR/docker-compose.yml" ps --format json openwebui
  echo "$output" | grep -q '"State":"running"'
}

@test "OTEL Collector container is running" {
  run docker compose -f "$DEMO_DIR/docker-compose.yml" ps --format json otel-collector
  echo "$output" | grep -q '"State":"running"'
}

@test "OpenWebUI /health returns 200" {
  status_code=$(curl -s -o /dev/null -w "%{http_code}" "$OPENWEBUI_URL/health")
  [ "$status_code" = "200" ]
}

@test "Can authenticate with OpenWebUI" {
  token=$(get_token)
  [ -n "$token" ] && [ "$token" != "None" ]
}

@test "6 bots are configured" {
  token=$(get_token)
  count=$(curl -s "$OPENWEBUI_URL/api/models" \
    -H "Authorization: Bearer $token" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
bots = [m for m in d.get('data', []) if m['id'] in ['hal','marvin','bender','glados','jarvis','cortana']]
print(len(bots))
" 2>/dev/null)
  [ "$count" = "6" ]
}

@test "6 tool sets are configured" {
  token=$(get_token)
  count=$(curl -s "$OPENWEBUI_URL/api/v1/tools/" \
    -H "Authorization: Bearer $token" \
    | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)
  [ "$count" = "6" ]
}
