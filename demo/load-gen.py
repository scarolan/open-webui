#!/usr/bin/env python3
"""
OpenWebUI Load Generation Script
Generates diverse LLM traces for dashboard development
"""

import requests
import json
import time
import sys
from typing import Optional

# Configuration
OPENWEBUI_URL = "http://localhost:3000"
MODEL = "gemini-3-flash-preview"  # Always use gemini-3-flash-preview (NOT older models like gemini-2.0)

# Diverse prompts for varied token counts
PROMPTS = [
    "What is 2+2?",
    "Explain quantum entanglement in simple terms.",
    "Write a haiku about observability.",
    "What are the key differences between REST and GraphQL APIs?",
    "Describe the architecture of a microservices system with detailed explanations of service discovery, load balancing, and circuit breakers.",
    "List 5 programming languages.",
    "Explain how Docker containers differ from virtual machines, including memory overhead, startup time, and isolation mechanisms.",
    "What is Kubernetes?",
    "Write a detailed guide on implementing distributed tracing in a polyglot microservices environment using OpenTelemetry.",
    "Hello!",
    "Explain the CAP theorem with real-world examples of AP and CP systems.",
    "What time is it?",
    "Compare and contrast Prometheus pull-based monitoring versus push-based systems like Graphite.",
    "Tell me a joke.",
    "Describe the differences between sampling strategies in distributed tracing: head-based, tail-based, and adaptive sampling.",
    "What is the meaning of life?",
    "Explain how to optimize Grafana dashboard queries for large-scale time series data.",
    "Count to 10.",
    "What are the trade-offs between using PromQL aggregations versus recording rules?",
    "Why is the sky blue?",
    "Describe the process of photosynthesis.",
    "What is the capital of France?",
    "Explain the difference between TCP and UDP.",
    "Write a Python function to calculate Fibonacci numbers.",
    "What is machine learning?",
]


def get_api_key() -> Optional[str]:
    """Prompt user for API key"""
    print("\n🔑 OpenWebUI API Key Required")
    print("=" * 50)
    print("\nTo generate an API key:")
    print("1. Go to http://localhost:3000")
    print("2. Click your profile → Settings")
    print("3. Go to 'Account' → 'API Keys'")
    print("4. Click 'Create new API key'")
    print("5. Copy the key and paste it here")
    print("\n" + "=" * 50)

    api_key = input("\nEnter API Key (or press Enter to use email/password): ").strip()

    if api_key:
        return api_key
    return None


def authenticate_with_credentials() -> Optional[str]:
    """Authenticate using email and password"""
    print("\n📧 Email/Password Authentication")
    print("=" * 50)

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    try:
        response = requests.post(
            f"{OPENWEBUI_URL}/api/v1/auths/signin",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                print("✅ Authentication successful!")
                return f"Bearer {token}"

        print(f"❌ Authentication failed: {response.status_code}")
        print(response.text)
        return None

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def send_chat_request(auth_header: str, prompt: str, count: int, total: int) -> bool:
    """Send a single chat completion request"""
    print(f"\n[{count}/{total}] Sending: {prompt[:60]}...")

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(
            f"{OPENWEBUI_URL}/api/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Extract token usage
            usage = data.get("usage", {})
            total_tokens = usage.get("total_tokens", "N/A")

            print(f"✓ Response received ({total_tokens} tokens)")
            return True
        else:
            print(f"⚠ Request failed: {response.status_code}")
            print(response.text[:200])
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🚀 OpenWebUI Load Generation")
    print("=" * 60)
    print(f"Target: {OPENWEBUI_URL}")
    print(f"Model: {MODEL}")
    print(f"Requests: {len(PROMPTS)}")
    print("=" * 60)

    # Get authentication
    api_key = get_api_key()

    if api_key:
        auth_header = f"Bearer {api_key}"
    else:
        auth_header = authenticate_with_credentials()

    if not auth_header:
        print("\n❌ Authentication failed. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Starting load generation...")
    print("=" * 60)

    # Send requests
    success_count = 0
    for i, prompt in enumerate(PROMPTS, 1):
        if send_chat_request(auth_header, prompt, i, len(PROMPTS)):
            success_count += 1

        # Delay to avoid rate limiting
        if i < len(PROMPTS):
            time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Load generation complete!")
    print(f"📊 Successfully sent: {success_count}/{len(PROMPTS)} requests")
    print("=" * 60)
    print("\n⏳ Wait 10-30 seconds for traces to appear in Tempo")
    print('🔍 Query: { span.openinference.span.kind = "LLM" }')
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Exiting.")
        sys.exit(0)
