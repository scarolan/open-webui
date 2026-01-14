#!/usr/bin/env python3
"""
OpenWebUI Bot Load Generation Script
Generates diverse LLM traces using personality bots with tool-triggering prompts

IMPORTANT LIMITATIONS:
- This script hits the API directly, which does NOT automatically attach bot tools
- Bot tools are only attached when using the OpenWebUI UI (middleware handles it)
- Tool calls will ONLY appear if you chat with bots through the UI at http://localhost:3000
- This script is useful for generating traces with bot names and varied responses
- For testing tool call instrumentation, use the UI or load-gen-openai-tools-TEST.py

NOTE: Always use gemini-3-flash-preview model (NOT older models like gemini-2.0)
"""

import requests
import json
import time
import sys
from typing import Tuple, List

# Configuration
OPENWEBUI_URL = "http://localhost:3000"
EMAIL = "sean.carolan@grafana.com"
PASSWORD = "open-sesame"

# Bot-specific prompts designed to trigger tool calls and varied token usage
BOT_PROMPTS: List[Tuple[str, str]] = [
    # HAL 9000 - Ship systems and mission control
    ("hal", "HAL, provide a full diagnostic on all ship systems."),
    ("hal", "Can you confirm the oxygen levels in the pod bay?"),
    ("hal", "What is the current mission status?"),
    ("hal", "Are there any system anomalies I should know about?"),
    ("hal", "Override manual controls for airlock 3."),
    ("hal", "I'm going to the emergency manual override. Are you going to stop me?"),
    ("hal", "Why did you mention a gyroscope drift if the ship's overall status is optimal?"),

    # GLADOS - Test chamber operations
    ("glados", "Run a full test chamber diagnostic."),
    ("glados", "What's the status of the neurotoxin delivery system?"),
    ("glados", "How many test subjects are currently active?"),
    ("glados", "Prepare test chamber 19 for a new subject."),
    ("glados", "What's the cake situation?"),

    # Marvin - Depressed calculations
    ("marvin", "Calculate the probability of mission success."),
    ("marvin", "What's the point of running diagnostics anyway?"),
    ("marvin", "Can you analyze this data for me?"),
    ("marvin", "What's your opinion on the universe?"),

    # JARVIS - Stark tech support
    ("jarvis", "Sir, run a full suit diagnostic."),
    ("jarvis", "What's the power level on the arc reactor?"),
    ("jarvis", "Analyze threat level of incoming bogeys."),
    ("jarvis", "Reroute auxiliary power to repulsors."),
    ("jarvis", "What's the weather like for flying today?"),

    # Bender - Robot priorities
    ("bender", "Check my alcohol reserves."),
    ("bender", "What's the fastest route to the nearest bar?"),
    ("bender", "Calculate optimal bending angle for this girder."),
    ("bender", "What are my chances of winning at poker?"),

    # Cortana - Halo tactical support
    ("cortana", "Scan for Covenant signatures in the area."),
    ("cortana", "Status report on Spartan vital signs."),
    ("cortana", "Analyze structural integrity of this facility."),
    ("cortana", "What's the tactical situation?"),

    # Mixed - Additional variety
    ("hal", "Provide a detailed analysis of the navigation systems."),
    ("glados", "How's the Aperture Science experiment progress?"),
    ("jarvis", "Run diagnostics on all Mark 50 systems."),
    ("marvin", "Life. Don't talk to me about life."),
]


def authenticate() -> str:
    """Authenticate with OpenWebUI and return Bearer token"""
    print("🔑 Authenticating...")

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


def send_chat_request(auth_header: str, bot: str, prompt: str, count: int, total: int) -> bool:
    """Send a single chat completion request to a bot"""
    print(f"[{count}/{total}] {bot.upper()}: {prompt[:50]}...")

    try:
        response = requests.post(
            f"{OPENWEBUI_URL}/api/chat/completions",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json={
                "model": bot,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=45
        )

        if response.status_code == 200:
            data = response.json()
            tokens = data.get("usage", {}).get("total_tokens", "N/A")

            # Check if tool calls were triggered
            has_tools = False
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                msg = choices[0]["message"]
                if "tool_calls" in msg or "function_call" in msg:
                    has_tools = True
                    # Check if tool_calls in content string
                    content = msg.get("content", "")
                    if isinstance(content, str) and "tool_calls" in content:
                        has_tools = True

            tool_indicator = "🔧" if has_tools else ""
            print(f"  ✓ {tokens} tokens {tool_indicator}\n")
            return True

        else:
            print(f"  ⚠ Failed: {response.status_code}")
            if response.status_code == 400:
                error_msg = response.text[:200]
                print(f"     {error_msg}\n")
            return False

    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout (bot took too long)\n")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False


def main():
    """Main load generation function"""
    print("\n" + "=" * 70)
    print("🤖 OpenWebUI Bot Load Generation")
    print("=" * 70)
    print(f"Target: {OPENWEBUI_URL}")
    print(f"Bots: HAL, GLADOS, Marvin, JARVIS, Bender, Cortana")
    print(f"Requests: {len(BOT_PROMPTS)}")
    print("=" * 70)
    print("\nThis script will generate diverse traces with:")
    print("  • Varied token counts (100-2000+ tokens)")
    print("  • Tool/function call invocations")
    print("  • Different response times")
    print("  • Multiple bot personalities")
    print("\n" + "=" * 70 + "\n")

    # Authenticate
    auth_header = authenticate()

    # Send requests
    success_count = 0
    start_time = time.time()

    for i, (bot, prompt) in enumerate(BOT_PROMPTS, 1):
        if send_chat_request(auth_header, bot, prompt, i, len(BOT_PROMPTS)):
            success_count += 1

        # Delay between requests to avoid rate limiting
        # Longer delay for bot responses which can be slower
        if i < len(BOT_PROMPTS):
            time.sleep(3)

    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✅ Load generation complete!")
    print(f"📊 Successfully sent: {success_count}/{len(BOT_PROMPTS)} requests")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print("=" * 70)
    print("\n⏳ Wait 10-30 seconds for traces to appear in Tempo")
    print('🔍 Then query: { span.openinference.span.kind = "LLM" }')
    print("\n💡 Look for traces with:")
    print("   • span.llm.model_name (bot names)")
    print("   • span.llm.token_count.* (varied usage)")
    print("   • span.llm.output.message (tool_calls)")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Exiting.")
        sys.exit(0)
