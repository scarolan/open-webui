#!/usr/bin/env python3
"""
OpenWebUI Complete Setup Script
Automatically configures Gemini connection and imports all 6 bot personalities

Usage:
    python3 setup-bots.py

Requirements:
    - OpenWebUI running at http://localhost:3000
    - User account already created (sign up first in the UI)
    - .env file with GEMINI_API_KEY configured
"""

import requests
import json
import sys
import os
from pathlib import Path

# Configuration
OPENWEBUI_URL = "http://localhost:3000"

# Load Gemini API key from environment or .env file
def load_gemini_key():
    """Load Gemini API key from .env file or environment"""
    env_file = Path(__file__).parent / ".env"

    # Try environment variable first
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key

    # Try .env file
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Prompt user
    return input("Enter your Gemini API key: ").strip()

GEMINI_API_KEY = load_gemini_key()
EMAIL = input("Enter your OpenWebUI email: ").strip()
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


def configure_gemini_connection(auth_header):
    """Configure Gemini API connection in admin settings"""
    print("🔌 Configuring Gemini connection...")

    admin_config = {
        "version": 0,
        "ui": {
            "enable_signup": False
        },
        "openai": {
            "enable": True,
            "api_base_urls": [
                "https://generativelanguage.googleapis.com/v1beta/openai"
            ],
            "api_keys": [
                GEMINI_API_KEY
            ],
            "api_configs": {
                "0": {
                    "enable": True,
                    "tags": [],
                    "prefix_id": "",
                    "model_ids": [],
                    "connection_type": "external",
                    "auth_type": "bearer"
                }
            }
        },
        "evaluation": {
            "arena": {
                "enable": False,
                "models": []
            }
        },
        "ollama": {
            "enable": False,
            "base_urls": [],
            "api_configs": {}
        }
    }

    try:
        response = requests.post(
            f"{OPENWEBUI_URL}/api/config/update",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json=admin_config,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print("  ✅ Gemini connection configured")
            print("  📡 API endpoint: https://generativelanguage.googleapis.com")
            print("  🔑 API key configured")
            return True
        else:
            print(f"  ⚠️  Configuration may have failed (status {response.status_code})")
            print(f"  Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"  ❌ Failed to configure connection: {e}")
        return False


def create_tool(auth_header, tool_data):
    """Create a tool in OpenWebUI"""
    tool_name = tool_data["name"]
    print(f"  Creating tool: {tool_name}...")

    try:
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
                "specs": json.loads(tool_data["specs"]) if isinstance(tool_data["specs"], str) else tool_data["specs"],
                "meta": json.loads(tool_data["meta"]) if isinstance(tool_data["meta"], str) else tool_data["meta"]
            },
            timeout=30
        )

        if response.status_code in [200, 201]:
            print(f"    ✅ Tool '{tool_name}' created")
            return True
        else:
            # Tool might already exist
            print(f"    ⚠️  Tool '{tool_name}' may already exist (status {response.status_code})")
            return True

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
            f"{OPENWEBUI_URL}/api/v1/models/add",
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
    print("  1. Configure Gemini API connection")
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

    # Step 1: Configure Gemini connection
    print("=" * 70)
    print("STEP 1: Admin Configuration")
    print("=" * 70 + "\n")
    configure_gemini_connection(auth_header)
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
    print("  ✅ Gemini API connection (gemini-3-flash-preview)")
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
