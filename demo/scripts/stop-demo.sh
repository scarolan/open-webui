#!/bin/bash
# Stop the OpenWebUI LLM Observability Demo
# Preserves volumes by default. Use `make clean` to remove volumes.

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DEMO_DIR"

echo "Stopping demo containers..."
docker compose down
echo "Done. Volumes preserved — use 'make clean' to remove them."
