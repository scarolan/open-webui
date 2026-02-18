#!/bin/bash
# Wrapper for setup-bots.py
# Sources .env and sets default credentials before running the Python script

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DEMO_DIR"

# Source .env if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Set defaults
export OPENWEBUI_EMAIL="${OPENWEBUI_EMAIL:-team-se@grafana.com}"
export OPENWEBUI_PASSWORD="${OPENWEBUI_PASSWORD:-open-sesame}"

python3 setup-bots.py "$@"
