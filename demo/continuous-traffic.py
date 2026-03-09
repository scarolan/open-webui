#!/usr/bin/env python3
"""
Continuous Traffic Generator for OpenWebUI Bot Demo

Generates a steady stream of bot queries to populate Grafana dashboards
with fresh traces during a live demo/presentation.

Usage:
    python3 continuous-traffic.py --duration 30  # Run for 30 minutes
    python3 continuous-traffic.py --interval 10   # Query every 10 seconds
"""

import asyncio
import aiohttp
import random
import sys
from datetime import datetime, timedelta

# OpenWebUI Configuration
OPENWEBUI_URL = "http://localhost:3000"
API_ENDPOINT = f"{OPENWEBUI_URL}/api/chat/completions"

# Bot model names (must match your OpenWebUI bot IDs)
BOTS = ["hal", "marvin", "bender", "glados", "jarvis", "cortana"]

# Query templates for each bot
QUERIES = {
    "hal": [
        "HAL, what's the status of the pod bay doors?",
        "Run a diagnostic check",
        "Check mission status",
        "Analyze voice stress patterns",
        "What systems need attention?",
    ],
    "marvin": [
        "Marvin, how are you feeling?",
        "What's your brain utilization?",
        "Calculate the meaninglessness of existence",
        "Share your complaints",
        "What's the probability of doom?",
    ],
    "bender": [
        "Bender, what do you think of humans?",
        "Can you make some beer?",
        "What would you steal?",
        "Generate an insult",
        "Bend something for me",
    ],
    "glados": [
        "GLADOS, check the neurotoxin status",
        "Set up a test chamber",
        "Deploy the turrets",
        "How's the cake coming along?",
        "Status report please",
    ],
    "jarvis": [
        "JARVIS, run a suit diagnostic",
        "Analyze power distribution",
        "Threat assessment please",
        "Reroute power to shields",
        "System status",
    ],
    "cortana": [
        "Cortana, scan for Covenant forces",
        "Check the Chief's vitals",
        "Analyze this structure",
        "Tactical assessment",
        "What's the situation?",
    ],
}


async def send_query(session: aiohttp.ClientSession, bot: str, query: str, api_key: str) -> dict:
    """Send a chat query to OpenWebUI API"""
    payload = {
        "model": bot,
        "messages": [{"role": "user", "content": query}],
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }

    try:
        async with session.post(API_ENDPOINT, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "success": True,
                    "bot": bot,
                    "query": query,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")[:100],
                }
            else:
                return {
                    "success": False,
                    "bot": bot,
                    "query": query,
                    "error": f"HTTP {resp.status}",
                }
    except Exception as e:
        return {
            "success": False,
            "bot": bot,
            "query": query,
            "error": str(e)[:100],
        }


async def generate_traffic(duration_minutes: int = 30, interval_seconds: int = 15, api_key: str = None):
    """
    Generate continuous traffic for the specified duration

    Args:
        duration_minutes: How long to run (default 30 minutes)
        interval_seconds: Seconds between queries (default 15)
        api_key: OpenWebUI API key (required)
    """
    if not api_key:
        print("❌ Error: API key required")
        print("Get your API key from OpenWebUI: Settings → Account → API Keys")
        sys.exit(1)

    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    query_count = 0
    success_count = 0

    print(f"🚀 Starting continuous traffic generation")
    print(f"⏱️  Duration: {duration_minutes} minutes")
    print(f"⏳ Interval: {interval_seconds} seconds")
    print(f"🤖 Bots: {', '.join(BOTS)}")
    print(f"🎯 Target: {API_ENDPOINT}")
    print(f"⏰ Will stop at: {end_time.strftime('%H:%M:%S')}")
    print("-" * 60)

    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            # Pick a random bot
            bot = random.choice(BOTS)
            query = random.choice(QUERIES[bot])

            # Send query
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🤖 {bot.upper():7} → {query[:50]}...", end="", flush=True)

            result = await send_query(session, bot, query, api_key)
            query_count += 1

            if result["success"]:
                success_count += 1
                print(f" ✅")
            else:
                print(f" ❌ {result['error']}")

            # Wait before next query
            await asyncio.sleep(interval_seconds)

    # Summary
    print("-" * 60)
    print(f"✅ Traffic generation complete!")
    print(f"📊 Total queries: {query_count}")
    print(f"✅ Successful: {success_count} ({success_count/query_count*100:.1f}%)")
    print(f"❌ Failed: {query_count - success_count}")
    print()
    print("💡 Check Grafana Tempo for traces:")
    print("   Query: { span.openinference.span.kind = \"LLM\" }")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate continuous traffic for OpenWebUI bot demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run for 30 minutes (default), query every 15 seconds (default)
  python3 continuous-traffic.py --api-key YOUR_KEY

  # Run for 10 minutes, query every 10 seconds
  python3 continuous-traffic.py --api-key YOUR_KEY --duration 10 --interval 10

  # Quick test: 5 minutes, query every 5 seconds
  python3 continuous-traffic.py --api-key YOUR_KEY --duration 5 --interval 5

Getting your API key:
  1. Open http://localhost:3000
  2. Go to Settings → Account → API Keys
  3. Generate new key
  4. Copy and use here
        """
    )

    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="OpenWebUI API key (get from Settings → Account → API Keys)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration in minutes (default: 30)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Seconds between queries (default: 15)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(generate_traffic(
            duration_minutes=args.duration,
            interval_seconds=args.interval,
            api_key=args.api_key,
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("✅ Traffic generation stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
