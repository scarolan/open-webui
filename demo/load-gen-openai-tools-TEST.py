#!/usr/bin/env python3
"""
OpenWebUI Bot Load Generation with Explicit Tool Calls
Generates LLM traces that include actual tool/function calls
"""

import requests
import json
import time
import sys
from typing import List, Dict, Tuple

# Configuration
OPENWEBUI_URL = "http://localhost:3000"
EMAIL = "sean.carolan@grafana.com"
PASSWORD = "open-sesame"

# Tool/function definitions (OpenAI format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search a database for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Bot-specific prompts designed to trigger tool calls
BOT_TOOL_PROMPTS: List[Tuple[str, str]] = [
    # HAL - System queries that would use tools
    ("hal", "What's the weather at mission control in Houston, Texas?"),
    ("hal", "Calculate the trajectory angle: sqrt(450) * 2.5"),
    ("hal", "Search the database for all system anomalies from the past week"),
    ("hal", "What's the temperature in the cargo bay? Check weather in Houston."),

    # GLADOS - Test chamber queries
    ("glados", "What's the weather in the test facility? We're in Salt Lake City."),
    ("glados", "Calculate neurotoxin concentration: 150 / 3.5 * 100"),
    ("glados", "Search database for test subjects with completion rate over 80%"),

    # Marvin - Depressed calculations
    ("marvin", "Calculate probability of happiness: 1 / infinity"),
    ("marvin", "What's the weather like in my digital existence? Check London."),
    ("marvin", "Search database for the meaning of life. You won't find it."),

    # JARVIS - Stark tech
    ("jarvis", "Sir, what's the weather in Malibu today?"),
    ("jarvis", "Calculate arc reactor power output: 3000 * 1.21"),
    ("jarvis", "Search database for Mark 50 suit diagnostics"),
    ("jarvis", "What's the weather at the Avengers facility in upstate New York?"),

    # Bender - Robot priorities
    ("bender", "What's the weather in Mexico? I need to know for... reasons."),
    ("bender", "Calculate my poker odds: (52 - 5) / 52 * 100"),
    ("bender", "Search the database for the nearest bar within 5 miles"),

    # Cortana - Halo tactical
    ("cortana", "What's the weather at Forward Operating Base Alpha?"),
    ("cortana", "Calculate Covenant fleet approach vector: sin(45) * 1000"),
    ("cortana", "Search database for Spartan vital signs anomalies"),

    # Additional variety
    ("hal", "Calculate oxygen reserves: 500 - (24 * 8.5)"),
    ("glados", "Search for test chamber 19 specifications"),
    ("jarvis", "Calculate flight time to New York: 3000 / 550"),
    ("marvin", "What's the weather in the void? Check Antarctica."),
    ("bender", "Search database for blackjack strategies"),
    ("cortana", "Calculate shield recharge time: 100 / 3.33"),
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
        sys.exit(1)

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)


def send_chat_with_tools(auth_header: str, bot: str, prompt: str, count: int, total: int) -> bool:
    """Send chat request with tool definitions"""
    print(f"[{count}/{total}] {bot.upper()}: {prompt[:60]}...")

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
                "tools": TOOLS,
                "tool_choice": "auto",  # Let the model decide when to use tools
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            tokens = data.get("usage", {}).get("total_tokens", "N/A")

            # Check for tool calls
            tool_indicator = ""
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                msg = choices[0]["message"]
                if "tool_calls" in msg and msg["tool_calls"]:
                    tool_count = len(msg["tool_calls"])
                    tool_names = [tc["function"]["name"] for tc in msg["tool_calls"]]
                    tool_indicator = f" 🔧 {tool_count} tools: {', '.join(tool_names)}"

            print(f"  ✓ {tokens} tokens{tool_indicator}\n")
            return True

        else:
            print(f"  ⚠ Failed: {response.status_code}")
            if response.status_code >= 400:
                error_msg = response.text[:300]
                print(f"     {error_msg}\n")
            return False

    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout\n")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False


def main():
    """Main load generation with tool calls"""
    print("\n" + "=" * 70)
    print("🤖 OpenWebUI Bot Load Generation (WITH TOOL CALLS)")
    print("=" * 70)
    print(f"Target: {OPENWEBUI_URL}")
    print(f"Bots: HAL, GLADOS, Marvin, JARVIS, Bender, Cortana")
    print(f"Requests: {len(BOT_TOOL_PROMPTS)}")
    print(f"Tools: get_weather, search_database, calculate")
    print("=" * 70)
    print("\nThis script sends prompts designed to trigger tool calls!")
    print("  • Weather queries → get_weather()")
    print("  • Math problems → calculate()")
    print("  • Database lookups → search_database()")
    print("\n" + "=" * 70 + "\n")

    auth_header = authenticate()

    success_count = 0
    tool_call_count = 0
    start_time = time.time()

    for i, (bot, prompt) in enumerate(BOT_TOOL_PROMPTS, 1):
        if send_chat_with_tools(auth_header, bot, prompt, i, len(BOT_TOOL_PROMPTS)):
            success_count += 1

        # Brief delay
        if i < len(BOT_TOOL_PROMPTS):
            time.sleep(2)

    elapsed_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✅ Load generation complete!")
    print(f"📊 Successfully sent: {success_count}/{len(BOT_TOOL_PROMPTS)} requests")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print("=" * 70)
    print("\n⏳ Wait 10-30 seconds for traces to appear in Tempo")
    print('🔍 Query for tool calls: { span.llm.tool_calls.count > 0 }')
    print("\n💡 Span attributes to check:")
    print("   • span.llm.model_name = bot names")
    print("   • span.llm.tool_calls.count = number of tools called")
    print("   • span.llm.tool_calls.names = tool names (comma-separated)")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted. Exiting.")
        sys.exit(0)
