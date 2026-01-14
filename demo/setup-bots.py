#!/usr/bin/env python3
"""
OpenWebUI Bot Setup Script
Automatically imports all 6 bot personalities with their custom tools

Usage:
    python3 setup-bots.py

Requirements:
    - OpenWebUI running at http://localhost:3000
    - User account already created (sign up first in the UI)
    - Email and password for authentication
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
OPENWEBUI_URL = "http://localhost:3000"
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
    print("🤖 OpenWebUI Bot Setup")
    print("="*70)
    print(f"Target: {OPENWEBUI_URL}")
    print("Bots: HAL 9000, Marvin, Bender, GLADOS, JARVIS, Cortana")
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

    # Create tools first
    print("📦 Creating Tools...")
    tools_created = 0
    for tool in tools:
        if create_tool(auth_header, tool):
            tools_created += 1

    print(f"\n✅ Created {tools_created}/{len(tools)} tools\n")

    # Create bots
    print("🤖 Creating Bots...")
    bots_created = 0
    for bot in bots:
        if create_bot(auth_header, bot):
            bots_created += 1

    print(f"\n✅ Created {bots_created}/{len(bots)} bots\n")

    # Summary
    print("="*70)
    print("✅ Setup complete!")
    print("="*70)
    print("\n📋 Next steps:")
    print("  1. Open http://localhost:3000")
    print("  2. Click the model dropdown")
    print("  3. Select HAL, Marvin, Bender, GLADOS, JARVIS, or Cortana")
    print("  4. Start chatting and watch tool calls in action!")
    print("\n💡 Tip: Chat with HAL about pod bay doors to trigger tools\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Exiting.")
        sys.exit(0)
