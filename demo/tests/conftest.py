"""
Pytest Configuration and Shared Fixtures

Provides common fixtures and configuration for all tests.
"""

import pytest
import os
import sys
import requests
import time
from pathlib import Path
from typing import Dict, Optional

# Add backend to Python path for imports
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Test configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:3000")
GRAFANA_TEMPO_URL = os.getenv("GRAFANA_TEMPO_URL", "")  # e.g., https://tempo-prod-us-east-0.grafana.net
GRAFANA_TEMPO_TOKEN = os.getenv("GRAFANA_TEMPO_TOKEN", "")  # Base64 encoded instance_id:token


@pytest.fixture(scope="session")
def openwebui_url():
    """OpenWebUI base URL"""
    return OPENWEBUI_URL


@pytest.fixture(scope="session")
def tempo_url():
    """Grafana Tempo URL"""
    if not GRAFANA_TEMPO_URL:
        pytest.skip("GRAFANA_TEMPO_URL not configured")
    return GRAFANA_TEMPO_URL


@pytest.fixture(scope="session")
def tempo_token():
    """Grafana Tempo auth token"""
    if not GRAFANA_TEMPO_TOKEN:
        pytest.skip("GRAFANA_TEMPO_TOKEN not configured")
    return GRAFANA_TEMPO_TOKEN


@pytest.fixture(scope="session")
def auth_token(openwebui_url):
    """
    Authenticate with OpenWebUI and return Bearer token

    Requires TEST_EMAIL and TEST_PASSWORD environment variables
    """
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not email or not password:
        pytest.skip("TEST_EMAIL and TEST_PASSWORD must be set for integration tests")

    try:
        response = requests.post(
            f"{openwebui_url}/api/v1/auths/signin",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                return f"Bearer {token}"

        pytest.fail(f"Authentication failed: {response.status_code}")

    except Exception as e:
        pytest.fail(f"Authentication error: {e}")


@pytest.fixture
def mock_llm_response():
    """Mock LLM API response with standard structure"""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gemini-flash-latest",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the LLM."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_llm_response_with_tools():
    """Mock LLM API response with tool calls (OpenAI format)"""
    return {
        "id": "chatcmpl-test456",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gemini-flash-latest",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": '{"location": "San Francisco, CA", "unit": "celsius"}'
                            }
                        },
                        {
                            "id": "call_def456",
                            "type": "function",
                            "function": {
                                "name": "search_database",
                                "arguments": '{"query": "latest results", "limit": 10}'
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ],
        "usage": {
            "prompt_tokens": 75,
            "completion_tokens": 50,
            "total_tokens": 125
        }
    }


@pytest.fixture
def mock_openwebui_bot_response():
    """Mock response from OpenWebUI bot (embedded tool calls format)"""
    return {
        "id": "chatcmpl-bot789",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "hal",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"tool_calls": [{"name": "pod_bay_doors", "parameters": {"action": "status"}}, {"name": "run_diagnostics", "parameters": {"system": "navigation"}}]}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 60,
            "completion_tokens": 80,
            "total_tokens": 140
        }
    }


@pytest.fixture
def sample_messages():
    """Sample message array for LLM requests"""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the weather in San Francisco?"}
    ]


@pytest.fixture
def wait_for_traces():
    """
    Fixture that provides a function to wait for traces to propagate

    Usage:
        wait_for_traces(seconds=30)
    """
    def _wait(seconds: int = 30):
        """Wait for traces to propagate to Tempo"""
        print(f"\n⏳ Waiting {seconds}s for traces to propagate to Tempo...")
        time.sleep(seconds)

    return _wait


@pytest.fixture
def tempo_query_helper(tempo_url, tempo_token):
    """
    Helper function for querying Grafana Tempo

    Returns a function that executes TraceQL queries
    """
    def _query(traceql: str, start_time: Optional[int] = None, end_time: Optional[int] = None) -> Dict:
        """
        Execute a TraceQL query against Grafana Tempo

        Args:
            traceql: TraceQL query string
            start_time: Start time in Unix timestamp (seconds)
            end_time: End time in Unix timestamp (seconds)

        Returns:
            Query results as dict
        """
        if not start_time:
            # Default to last 15 minutes
            end_time = int(time.time())
            start_time = end_time - (15 * 60)

        url = f"{tempo_url}/api/search"

        headers = {
            "Authorization": f"Basic {tempo_token}",
            "Content-Type": "application/json"
        }

        params = {
            "q": traceql,
            "start": start_time,
            "end": end_time
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            pytest.fail(f"Tempo query failed: {e}")

    return _query
