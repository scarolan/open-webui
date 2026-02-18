#!/usr/bin/env bats
# Preflight tests — validate prerequisites without a running stack

DEMO_DIR="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"

@test "Docker is installed" {
  command -v docker
}

@test "Docker daemon is running" {
  docker ps >/dev/null 2>&1
}

@test "docker compose is available" {
  docker compose version >/dev/null 2>&1
}

@test ".env file exists" {
  [ -f "$DEMO_DIR/.env" ]
}

@test "OPENAI_API_KEY is set in .env" {
  value=$(grep '^OPENAI_API_KEY=' "$DEMO_DIR/.env" | cut -d'=' -f2-)
  [ -n "$value" ]
  ! echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder)'
}

@test "ANTHROPIC_API_KEY is set in .env" {
  value=$(grep '^ANTHROPIC_API_KEY=' "$DEMO_DIR/.env" | cut -d'=' -f2-)
  [ -n "$value" ]
  ! echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder)'
}

@test "GEMINI_API_KEY is set in .env" {
  value=$(grep '^GEMINI_API_KEY=' "$DEMO_DIR/.env" | cut -d'=' -f2-)
  [ -n "$value" ]
  ! echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder)'
}

@test "GRAFANA_OTLP_TOKEN is set in .env" {
  value=$(grep '^GRAFANA_OTLP_TOKEN=' "$DEMO_DIR/.env" | cut -d'=' -f2-)
  [ -n "$value" ]
  ! echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder)'
}

@test "OTEL_EXPORTER_OTLP_ENDPOINT is set in .env" {
  value=$(grep '^OTEL_EXPORTER_OTLP_ENDPOINT=' "$DEMO_DIR/.env" | cut -d'=' -f2-)
  [ -n "$value" ]
  ! echo "$value" | grep -qE '(your-.*-here|xxxxxxxx|changeme|placeholder|REGION)'
}

@test "python3 is available" {
  command -v python3
}

@test "Python requests module is installed" {
  python3 -c "import requests"
}
