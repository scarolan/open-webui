#!/usr/bin/env python3
"""
OpenWebUI Complete Setup Script
Automatically configures OpenAI, Anthropic (via LiteLLM), and Gemini connections
and imports all 6 bot personalities

Usage:
    python3 setup-bots.py

Requirements:
    - OpenWebUI running at http://localhost:3000
    - User account already created (sign up first in the UI)
    - .env file with OPENAI_API_KEY, ANTHROPIC_API_KEY, and GEMINI_API_KEY configured
"""

import requests
import json
import sys
import os
from pathlib import Path

# Configuration
OPENWEBUI_URL = "http://localhost:3000"

# Load API keys from environment or .env file
def load_env_key(var_name):
    """Load an API key from environment variable or .env file"""
    env_file = Path(__file__).parent / ".env"

    # Try environment variable first
    key = os.getenv(var_name)
    if key:
        return key

    # Try .env file
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith(f"{var_name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Prompt user
    return input(f"Enter your {var_name}: ").strip()

GEMINI_API_KEY = load_env_key("GEMINI_API_KEY")
ANTHROPIC_API_KEY = load_env_key("ANTHROPIC_API_KEY")
OPENAI_API_KEY = load_env_key("OPENAI_API_KEY")

# Get email/password from environment or prompt
EMAIL = os.getenv("OPENWEBUI_EMAIL")
PASSWORD = os.getenv("OPENWEBUI_PASSWORD")

if not EMAIL:
    EMAIL = input("Enter your OpenWebUI email: ").strip()
if not PASSWORD:
    PASSWORD = input("Enter your OpenWebUI password: ").strip()

def authenticate():
    """Authenticate with OpenWebUI and return Bearer token"""
    print("\n🔑 Authenticating...")

    try:
        response = requests.post(
            f"{OPENWEBUI_URL}/api/v1/auths/signin",
            json={"email": EMAIL, "password": PASSWORD},
            timeout=10
        )

        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                print("✅ Authenticated!\n")
                return f"Bearer {token}"

        print(f"❌ Authentication failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)


def configure_connections(auth_header):
    """Configure OpenAI, Anthropic (via LiteLLM), and Gemini API connections"""
    print("🔌 Configuring API connections...")
    print("  [0] OpenAI  → https://api.openai.com/v1")
    print("  [1] LiteLLM → http://litellm:4000/v1 (Anthropic proxy)")
    print("  [2] Gemini  → https://generativelanguage.googleapis.com/v1beta/openai")

    config_payload = {
        "ENABLE_OPENAI_API": True,
        "OPENAI_API_BASE_URLS": [
            "https://api.openai.com/v1",                                 # index 0: OpenAI
            "http://litellm:4000/v1",                                    # index 1: LiteLLM (Anthropic)
            "https://generativelanguage.googleapis.com/v1beta/openai"    # index 2: Gemini
        ],
        "OPENAI_API_KEYS": [
            OPENAI_API_KEY,
            "sk-unused",  # LiteLLM handles its own auth via ANTHROPIC_API_KEY env var
            GEMINI_API_KEY
        ],
        "OPENAI_API_CONFIGS": {
            "0": {
                "enable": True,
                "tags": [],
                "prefix_id": "",
                "model_ids": ["gpt-4o", "gpt-4o-mini"],
                "connection_type": "external",
                "auth_type": "bearer"
            },
            "1": {
                "enable": True,
                "tags": [],
                "prefix_id": "",
                "model_ids": ["claude-sonnet-4-5", "claude-haiku-4-5"],
                "connection_type": "external",
                "auth_type": "bearer"
            },
            "2": {
                "enable": True,
                "tags": [],
                "prefix_id": "",
                "model_ids": ["models/gemini-pro-latest", "models/gemini-flash-latest"],
                "connection_type": "external",
                "auth_type": "bearer"
            }
        }
    }

    try:
        response = requests.post(
            f"{OPENWEBUI_URL}/openai/config/update",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json=config_payload,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print("  ✅ OpenAI connection configured (index 0)")
            print("  ✅ LiteLLM/Anthropic connection configured (index 1)")
            print("  ✅ Gemini connection configured (index 2)")
            return True
        else:
            print(f"  ⚠️  Configuration failed (status {response.status_code})")
            print(f"  Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"  ❌ Failed to configure connections: {e}")
        return False


def create_tool(auth_header, tool_data):
    """Create a tool in OpenWebUI"""
    tool_name = tool_data["name"]
    print(f"  Creating tool: {tool_name}...")

    try:
        meta = json.loads(tool_data["meta"]) if isinstance(tool_data["meta"], str) else tool_data["meta"]
        response = requests.post(
            f"{OPENWEBUI_URL}/api/v1/tools/create",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json={
                "id": tool_data["id"],
                "name": tool_data["name"],
                "content": tool_data["content"],
                "meta": meta
            },
            timeout=30
        )

        if response.status_code in [200, 201]:
            print(f"    ✅ Tool '{tool_name}' created")
            return True
        elif response.status_code == 400:
            detail = response.json().get("detail", "")
            if "already exists" in detail.lower() or "duplicate" in detail.lower():
                print(f"    ✅ Tool '{tool_name}' already exists (skipped)")
            else:
                print(f"    ⚠️  Tool '{tool_name}' returned 400: {detail[:100]}")
            return True
        else:
            print(f"    ❌ Tool '{tool_name}' failed (status {response.status_code})")
            return False

    except Exception as e:
        print(f"    ❌ Failed to create tool '{tool_name}': {e}")
        return False


def create_bot(auth_header, bot_data):
    """Create a bot model in OpenWebUI"""
    bot_name = bot_data["name"]
    print(f"  Creating bot: {bot_name}...")

    try:
        meta = json.loads(bot_data["meta"]) if isinstance(bot_data["meta"], str) else bot_data["meta"]
        params = json.loads(bot_data["params"]) if isinstance(bot_data["params"], str) else bot_data["params"]

        response = requests.post(
            f"{OPENWEBUI_URL}/api/v1/models/create",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json={
                "id": bot_data["id"],
                "base_model_id": bot_data["base_model_id"],
                "name": bot_data["name"],
                "meta": meta,
                "params": params
            },
            timeout=30
        )

        if response.status_code in [200, 201]:
            print(f"    ✅ Bot '{bot_name}' created")
            return True
        else:
            print(f"    ⚠️  Bot '{bot_name}' may already exist (status {response.status_code})")
            return True

    except Exception as e:
        print(f"    ❌ Failed to create bot '{bot_name}': {e}")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("🤖 OpenWebUI Complete Setup")
    print("="*70)
    print(f"Target: {OPENWEBUI_URL}")
    print("Tasks:")
    print("  1. Configure OpenAI + Anthropic (via LiteLLM) + Gemini API connections")
    print("  2. Import 6 bot personalities (HAL, Marvin, Bender, GLADOS, JARVIS, Cortana)")
    print("  3. Import 6 custom tool sets (39 total functions)")
    print("="*70 + "\n")

    # Load bot configs
    configs_dir = Path(__file__).parent / "bot-configs"

    if not configs_dir.exists():
        print(f"❌ Bot configs directory not found: {configs_dir}")
        sys.exit(1)

    tools_file = configs_dir / "tools.json"
    bots_file = configs_dir / "bots.json"

    if not tools_file.exists() or not bots_file.exists():
        print(f"❌ Config files not found in {configs_dir}")
        sys.exit(1)

    # Load data
    with open(tools_file) as f:
        tools = json.load(f)

    with open(bots_file) as f:
        bots = json.load(f)

    # Authenticate
    auth_header = authenticate()

    # Step 1: Configure API connections (Gemini + LiteLLM/Anthropic)
    print("=" * 70)
    print("STEP 1: Admin Configuration")
    print("=" * 70 + "\n")
    configure_connections(auth_header)
    print()

    # Step 2: Create tools
    print("=" * 70)
    print("STEP 2: Import Tools")
    print("=" * 70 + "\n")
    print(f"📦 Creating {len(tools)} tool sets...")
    tools_created = 0
    for tool in tools:
        if create_tool(auth_header, tool):
            tools_created += 1

    print(f"\n✅ Imported {tools_created}/{len(tools)} tool sets\n")

    # Step 3: Create bots
    print("=" * 70)
    print("STEP 3: Import Bot Personalities")
    print("=" * 70 + "\n")
    print(f"🤖 Creating {len(bots)} bots...")
    bots_created = 0
    for bot in bots:
        if create_bot(auth_header, bot):
            bots_created += 1

    print(f"\n✅ Imported {bots_created}/{len(bots)} bots\n")

    # Summary
    print("="*70)
    print("✅ Setup Complete!")
    print("="*70)
    print("\n📋 What was configured:")
    print("  ✅ OpenAI connection (HAL → gpt-4o, JARVIS → gpt-4o-mini)")
    print("  ✅ LiteLLM/Anthropic connection (Marvin → Sonnet 4.5, Bender → Haiku 4.5)")
    print("  ✅ Gemini connection (GLADOS → gemini-pro-latest, Cortana → gemini-flash-latest)")
    print(f"  ✅ {tools_created} tool sets with 39 custom functions")
    print(f"  ✅ {bots_created} bot personalities with unique system prompts")
    print("\n📋 Next steps:")
    print("  1. Open http://localhost:3000")
    print("  2. Click the model dropdown in chat")
    print("  3. Select HAL, Marvin, Bender, GLADOS, JARVIS, or Cortana")
    print("  4. Start chatting and watch tool calls trigger!")
    print("\n💡 Tips:")
    print("  • Ask HAL about pod bay doors to trigger diagnostics")
    print("  • Ask Marvin about the meaning of life")
    print("  • Ask Bender to steal something or brew beer")
    print("  • Traces appear in Grafana Tempo after 30-60 seconds")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Exiting.")
        sys.exit(0)
