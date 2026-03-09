# OpenWebUI LLM Observability Demo
# Standard demo-builder targets + demo-specific targets

SHELL := /bin/bash
DEMO_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
COMPOSE := docker compose -f $(DEMO_DIR)docker-compose.yml

.DEFAULT_GOAL := help

##@ General
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Lifecycle
.PHONY: preflight
preflight: ## Check prerequisites (Docker, .env, python3)
	@$(DEMO_DIR)scripts/preflight-check.sh

.PHONY: start
start: ## Start the full demo (preflight + docker + bots)
	@$(DEMO_DIR)scripts/start-demo.sh

.PHONY: stop
stop: ## Stop containers (preserves volumes)
	@$(DEMO_DIR)scripts/stop-demo.sh

.PHONY: clean
clean: ## Stop containers AND remove volumes
	@echo "Stopping containers and removing volumes..."
	@$(COMPOSE) down --volumes --remove-orphans 2>/dev/null || true
	@echo "Clean complete."

##@ Testing
.PHONY: test
test: test-preflight test-smoke ## Run preflight + smoke tests

.PHONY: test-preflight
test-preflight: ## Run preflight BATS tests
	@bats $(DEMO_DIR)tests/preflight.bats

.PHONY: test-smoke
test-smoke: ## Run smoke BATS tests (requires running stack)
	@bats $(DEMO_DIR)tests/smoke.bats

.PHONY: test-telemetry
test-telemetry: ## Run telemetry BATS tests (requires running stack)
	@bats $(DEMO_DIR)tests/telemetry.bats

.PHONY: test-unit
test-unit: ## Run pytest unit tests
	@cd $(DEMO_DIR) && ./run-tests.sh --unit

.PHONY: test-integration
test-integration: ## Run pytest integration tests (requires running stack)
	@cd $(DEMO_DIR) && ./run-tests.sh --integration

.PHONY: test-all
test-all: test test-telemetry test-unit ## Run all tests

##@ Load Generation
.PHONY: load-gen
load-gen: ## Generate bot traces (33 requests)
	@cd $(DEMO_DIR) && python3 load-gen-bots.py

.PHONY: load-gen-tools
load-gen-tools: ## Generate tool call traces (25 requests)
	@cd $(DEMO_DIR) && python3 load-gen-openai-tools-TEST.py

.PHONY: traffic
traffic: ## Generate continuous traffic (default 45 min). Usage: make traffic [DURATION=45]
	@DURATION=$${DURATION:-45}; \
	EMAIL=$${OPENWEBUI_EMAIL:-team-se@grafana.com}; \
	PASSWORD=$${OPENWEBUI_PASSWORD:-open-sesame}; \
	TOKEN=$$(curl -s -X POST http://localhost:3000/api/v1/auths/signin \
		-H 'Content-Type: application/json' \
		-d "{\"email\":\"$$EMAIL\",\"password\":\"$$PASSWORD\"}" \
		| python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))"); \
	if [ -z "$$TOKEN" ] || [ "$$TOKEN" = "None" ]; then \
		echo "❌ Failed to get API token. Is OpenWebUI running? Try: make start"; \
		exit 1; \
	fi; \
	cd $(DEMO_DIR) && python3 continuous-traffic.py --api-key "$$TOKEN" --duration "$$DURATION"

.PHONY: load-test
load-test: ## Run k6 load test
	@k6 run $(DEMO_DIR)k6/load-test.js
