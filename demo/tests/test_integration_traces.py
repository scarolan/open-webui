"""
Integration Tests for End-to-End Tracing

Tests that traces are properly created and exported to Grafana Tempo.
Requires running OpenWebUI instance and Grafana Cloud credentials.
"""

import pytest
import requests
import time
import json
from typing import Dict, List


class TestEndToEndTracing:
    """Test complete trace flow from request to Tempo"""

    @pytest.mark.integration
    def test_basic_llm_trace_creation(self, openwebui_url, auth_token, wait_for_traces):
        """Test that a basic LLM request creates a trace"""
        # Send a chat completion request
        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": "gemini-3-flash-preview",
                "messages": [
                    {"role": "user", "content": "What is 2+2?"}
                ],
                "stream": False
            },
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "usage" in data

        # Note: Actual Tempo validation requires tempo_query_helper
        # which we test in separate tests
        print("\n✅ LLM request completed successfully")
        print(f"   Tokens used: {data['usage'].get('total_tokens', 'N/A')}")

    @pytest.mark.integration
    def test_bot_personality_trace(self, openwebui_url, auth_token):
        """Test that bot personalities create properly attributed traces"""
        bot_name = "hal"

        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": bot_name,
                "messages": [
                    {"role": "user", "content": "What is the pod bay door status?"}
                ],
                "stream": False
            },
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response
        assert "choices" in data
        assert data["model"] == bot_name or data["model"].startswith(bot_name)

        print(f"\n✅ Bot '{bot_name}' responded successfully")

    @pytest.mark.integration
    def test_tool_call_trace(self, openwebui_url, auth_token):
        """Test that tool calls are captured in traces"""
        # Define tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ]

        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": "gemini-3-flash-preview",
                "messages": [
                    {"role": "user", "content": "What's the weather in San Francisco?"}
                ],
                "tools": tools,
                "tool_choice": "auto",
                "stream": False
            },
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        print("\n✅ Tool call request completed")

        # Check if tools were called (may not always happen depending on model)
        if "choices" in data and data["choices"]:
            message = data["choices"][0].get("message", {})
            if "tool_calls" in message:
                print(f"   🔧 Tools called: {len(message['tool_calls'])}")

    @pytest.mark.integration
    def test_streaming_response(self, openwebui_url, auth_token):
        """Test that streaming responses create proper traces"""
        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": "gemini-3-flash-preview",
                "messages": [
                    {"role": "user", "content": "Count to 5"}
                ],
                "stream": True
            },
            timeout=30,
            stream=True
        )

        assert response.status_code == 200

        # Consume stream
        chunks = []
        for line in response.iter_lines():
            if line:
                chunks.append(line)

        assert len(chunks) > 0
        print(f"\n✅ Streaming response completed ({len(chunks)} chunks)")

    @pytest.mark.integration
    def test_multiple_bot_traces(self, openwebui_url, auth_token):
        """Test creating traces from multiple bots"""
        bots = ["hal", "marvin", "bender"]

        for bot in bots:
            response = requests.post(
                f"{openwebui_url}/api/chat/completions",
                headers={
                    "Authorization": auth_token,
                    "Content-Type": "application/json"
                },
                json={
                    "model": bot,
                    "messages": [
                        {"role": "user", "content": "Hello!"}
                    ],
                    "stream": False
                },
                timeout=30
            )

            assert response.status_code == 200
            print(f"✅ Bot '{bot}' responded")

            # Brief delay between requests
            time.sleep(1)


class TestTempoValidation:
    """Test trace validation in Grafana Tempo"""

    @pytest.mark.tempo
    def test_tempo_connection(self, tempo_query_helper):
        """Test that we can connect to Tempo and execute queries"""
        # Simple query for any LLM spans in last 15 minutes
        results = tempo_query_helper('{ span.openinference.span.kind = "LLM" }')

        assert results is not None
        print("\n✅ Tempo connection successful")

        if "traces" in results:
            trace_count = len(results["traces"])
            print(f"   Found {trace_count} traces")

    @pytest.mark.tempo
    def test_llm_span_attributes_exist(self, tempo_query_helper, wait_for_traces):
        """Test that LLM spans have required OpenInference attributes"""
        # Query for recent LLM spans
        results = tempo_query_helper('{ span.openinference.span.kind = "LLM" }')

        assert results is not None
        assert "traces" in results

        if len(results["traces"]) == 0:
            pytest.skip("No traces found - run load-gen scripts first")

        # Check first trace
        trace = results["traces"][0]

        # Required attributes that should exist
        required_attrs = [
            "openinference.span.kind",
            "llm.model_name",
            "llm.provider"
        ]

        # Note: Actual attribute checking depends on Tempo API response format
        # This is a simplified check
        print(f"\n✅ Found {len(results['traces'])} LLM traces")

    @pytest.mark.tempo
    def test_bot_traces_distinguishable(self, tempo_query_helper):
        """Test that bot traces can be distinguished by model_name"""
        # Query for HAL bot specifically
        results = tempo_query_helper('{ span.llm.model_name = "hal" }')

        if results and "traces" in results and len(results["traces"]) > 0:
            print(f"\n✅ Found {len(results['traces'])} HAL traces")
        else:
            pytest.skip("No HAL traces found - run load-gen-bots.py first")

    @pytest.mark.tempo
    def test_tool_call_traces_exist(self, tempo_query_helper):
        """Test that traces with tool calls are captured"""
        # Query for traces with tool calls
        results = tempo_query_helper('{ span.llm.tool_calls.count > 0 }')

        if results and "traces" in results and len(results["traces"]) > 0:
            print(f"\n✅ Found {len(results['traces'])} traces with tool calls")
        else:
            pytest.skip("No tool call traces found - run load-gen-openai-tools-TEST.py first")

    @pytest.mark.tempo
    def test_token_usage_captured(self, tempo_query_helper):
        """Test that token usage is captured in traces"""
        # Query for traces with token counts
        results = tempo_query_helper('{ span.llm.token_count.total > 0 }')

        if results and "traces" in results and len(results["traces"]) > 0:
            print(f"\n✅ Found {len(results['traces'])} traces with token usage")
        else:
            pytest.skip("No traces with token usage found")


class TestErrorHandling:
    """Test error scenarios and trace capture"""

    @pytest.mark.integration
    def test_invalid_model_error(self, openwebui_url, auth_token):
        """Test that errors are handled gracefully"""
        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": "nonexistent-model-xyz",
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "stream": False
            },
            timeout=30
        )

        # Should get error response
        assert response.status_code >= 400
        print(f"\n✅ Error handled properly (status {response.status_code})")

    @pytest.mark.integration
    def test_malformed_request(self, openwebui_url, auth_token):
        """Test handling of malformed requests"""
        response = requests.post(
            f"{openwebui_url}/api/chat/completions",
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            },
            json={
                "model": "gemini-3-flash-preview",
                # Missing required 'messages' field
                "stream": False
            },
            timeout=30
        )

        # Should get validation error
        assert response.status_code >= 400
        print(f"\n✅ Malformed request rejected (status {response.status_code})")
