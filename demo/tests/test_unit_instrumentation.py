"""
Unit Tests for LLM Instrumentation

Tests the core instrumentation code without requiring live services.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Import the code we're testing
from open_webui.utils.telemetry.llm_instrumentation import (
    LLMSpanManager,
    detect_provider_from_url,
    ollama_usage_to_openai,
)


@pytest.fixture(scope="session")
def session_tracer_setup():
    """
    Setup tracer provider once for the entire test session

    OpenTelemetry doesn't allow overriding the global tracer provider,
    so we set it up once and reuse it across all tests.
    """
    # Create in-memory exporter
    span_exporter = InMemorySpanExporter()

    # Setup tracer provider (only once for entire session)
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))

    # Set as global (needed for LLMSpanManager to find it)
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider.get_tracer(__name__), span_exporter


@pytest.fixture(scope="function")
def in_memory_tracer(session_tracer_setup):
    """
    Per-test fixture that clears spans between tests

    Returns tuple of (tracer, span_exporter) where span_exporter.get_finished_spans()
    can be used to inspect created spans
    """
    tracer, span_exporter = session_tracer_setup

    # Clear any spans from previous tests
    span_exporter.clear()

    yield tracer, span_exporter

    # Cleanup after test
    span_exporter.clear()


class TestLLMSpanManager:
    """Test LLMSpanManager context manager"""

    @pytest.mark.asyncio
    async def test_basic_span_creation(self, in_memory_tracer):
        """Test that LLMSpanManager creates a span with basic attributes"""
        tracer, exporter = in_memory_tracer

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            pass

        spans = exporter.get_finished_spans()
        assert len(spans) == 1

        span = spans[0]
        assert span.name == "llm.openai.chat"
        assert span.attributes["openinference.span.kind"] == "LLM"
        assert span.attributes["llm.model_name"] == "gpt-4"
        assert span.attributes["llm.provider"] == "openai"
        assert span.attributes["span_type"] == "llm"

    @pytest.mark.asyncio
    async def test_custom_operation_name(self, in_memory_tracer):
        """Test custom operation name"""
        tracer, exporter = in_memory_tracer

        async with LLMSpanManager(
            model="gemini-pro",
            provider="gemini",
            operation_name="llm.custom.operation"
        ) as llm_span:
            pass

        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "llm.custom.operation"

    @pytest.mark.asyncio
    async def test_set_usage(self, in_memory_tracer):
        """Test setting token usage"""
        tracer, exporter = in_memory_tracer

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_usage({
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            })

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.token_count.prompt"] == 100
        assert span.attributes["llm.token_count.completion"] == 200
        assert span.attributes["llm.token_count.total"] == 300

    @pytest.mark.asyncio
    async def test_set_input_string_content(self, in_memory_tracer):
        """Test capturing input messages with string content"""
        tracer, exporter = in_memory_tracer

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "What is 2+2?"}
        ]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_input(messages)

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.input.message"] == "What is 2+2?"

    @pytest.mark.asyncio
    async def test_set_input_truncation(self, in_memory_tracer):
        """Test that input is truncated to 1000 chars"""
        tracer, exporter = in_memory_tracer

        long_content = "A" * 2000
        messages = [{"role": "user", "content": long_content}]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_input(messages)

        spans = exporter.get_finished_spans()
        span = spans[0]

        captured_input = span.attributes["llm.input.message"]
        assert len(captured_input) == 1000
        assert captured_input == "A" * 1000

    @pytest.mark.asyncio
    async def test_set_output_simple(self, in_memory_tracer):
        """Test capturing simple output"""
        tracer, exporter = in_memory_tracer

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_output("The answer is 4.")

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.output.message"] == "The answer is 4."

    @pytest.mark.asyncio
    async def test_set_output_with_openai_tool_calls(self, in_memory_tracer):
        """Test capturing output with OpenAI-format tool calls"""
        tracer, exporter = in_memory_tracer

        tool_calls = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "SF"}'
                }
            }
        ]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_output("", tool_calls=tool_calls)

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.tool_calls.count"] == 1
        assert span.attributes["llm.tool_calls.names"] == "get_weather"
        assert span.attributes["llm.tool_calls.0.name"] == "get_weather"
        assert span.attributes["llm.tool_calls.0.arguments"] == '{"location": "SF"}'

    @pytest.mark.asyncio
    async def test_set_output_with_embedded_tool_calls(self, in_memory_tracer):
        """Test capturing output with OpenWebUI embedded tool calls"""
        tracer, exporter = in_memory_tracer

        # OpenWebUI bot format - tool calls embedded in JSON content
        content = json.dumps({
            "tool_calls": [
                {"name": "pod_bay_doors", "parameters": {"action": "open"}},
                {"name": "run_diagnostics", "parameters": {"system": "life_support"}}
            ]
        })

        async with LLMSpanManager(model="hal", provider="openai") as llm_span:
            llm_span.set_output(content)

        spans = exporter.get_finished_spans()
        span = spans[0]

        # Should convert to OpenAI format and extract attributes
        assert span.attributes["llm.tool_calls.count"] == 2
        assert span.attributes["llm.tool_calls.names"] == "pod_bay_doors,run_diagnostics"
        assert span.attributes["llm.tool_calls.0.name"] == "pod_bay_doors"
        assert span.attributes["llm.tool_calls.1.name"] == "run_diagnostics"

    @pytest.mark.asyncio
    async def test_set_invocation_parameters(self, in_memory_tracer):
        """Test capturing invocation parameters"""
        tracer, exporter = in_memory_tracer

        params = {
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9,
            "stream": False
        }

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_invocation_parameters(params)

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.temperature"] == 0.7
        assert span.attributes["llm.max_tokens"] == 500
        assert span.attributes["llm.top_p"] == 0.9
        assert span.attributes["llm.stream"] == False

    @pytest.mark.asyncio
    async def test_error_handling(self, in_memory_tracer):
        """Test that exceptions are captured in span status"""
        tracer, exporter = in_memory_tracer

        with pytest.raises(ValueError):
            async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
                raise ValueError("Test error")

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.status.status_code.name == "ERROR"
        assert "Test error" in span.status.description


class TestProviderDetection:
    """Test LLM provider detection from URLs"""

    def test_detect_gemini(self):
        """Test Gemini provider detection"""
        url = "https://generativelanguage.googleapis.com/v1beta/openai"
        assert detect_provider_from_url(url) == "gemini"

    def test_detect_openai(self):
        """Test OpenAI provider detection"""
        url = "https://api.openai.com/v1/chat/completions"
        assert detect_provider_from_url(url) == "openai"

    def test_detect_azure(self):
        """Test Azure OpenAI provider detection"""
        url = "https://myresource.openai.azure.com/openai/deployments"
        assert detect_provider_from_url(url) == "azure"

    def test_detect_anthropic(self):
        """Test Anthropic provider detection"""
        url = "https://api.anthropic.com/v1/messages"
        assert detect_provider_from_url(url) == "anthropic"

    def test_detect_cohere(self):
        """Test Cohere provider detection"""
        url = "https://api.cohere.ai/v1/generate"
        assert detect_provider_from_url(url) == "cohere"

    def test_detect_default_fallback(self):
        """Test default fallback to OpenAI"""
        url = "https://some-custom-api.com/v1/chat"
        assert detect_provider_from_url(url) == "openai"


class TestOllamaFormatConversion:
    """Test Ollama usage format conversion"""

    def test_ollama_usage_conversion(self):
        """Test converting Ollama usage format to OpenAI format"""
        ollama_response = {
            "prompt_eval_count": 150,
            "eval_count": 200
        }

        result = ollama_usage_to_openai(ollama_response)

        assert result["prompt_tokens"] == 150
        assert result["completion_tokens"] == 200
        assert result["total_tokens"] == 350

    def test_ollama_usage_missing_fields(self):
        """Test Ollama conversion with missing fields"""
        ollama_response = {}

        result = ollama_usage_to_openai(ollama_response)

        assert result["prompt_tokens"] == 0
        assert result["completion_tokens"] == 0
        assert result["total_tokens"] == 0


class TestToolCallParsing:
    """Test tool call parsing and conversion"""

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, in_memory_tracer):
        """Test capturing multiple tool calls"""
        tracer, exporter = in_memory_tracer

        tool_calls = [
            {
                "type": "function",
                "function": {"name": "tool1", "arguments": "{}"}
            },
            {
                "type": "function",
                "function": {"name": "tool2", "arguments": "{}"}
            },
            {
                "type": "function",
                "function": {"name": "tool3", "arguments": "{}"}
            }
        ]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_tool_calls(tool_calls)

        spans = exporter.get_finished_spans()
        span = spans[0]

        assert span.attributes["llm.tool_calls.count"] == 3
        assert span.attributes["llm.tool_calls.names"] == "tool1,tool2,tool3"
        assert span.attributes["llm.tool_calls.0.name"] == "tool1"
        assert span.attributes["llm.tool_calls.1.name"] == "tool2"
        assert span.attributes["llm.tool_calls.2.name"] == "tool3"

    @pytest.mark.asyncio
    async def test_tool_call_argument_truncation(self, in_memory_tracer):
        """Test that tool call arguments are truncated to 500 chars"""
        tracer, exporter = in_memory_tracer

        long_args = json.dumps({"data": "X" * 1000})
        tool_calls = [
            {
                "type": "function",
                "function": {
                    "name": "big_tool",
                    "arguments": long_args
                }
            }
        ]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_tool_calls(tool_calls)

        spans = exporter.get_finished_spans()
        span = spans[0]

        captured_args = span.attributes["llm.tool_calls.0.arguments"]
        assert len(captured_args) == 500

    @pytest.mark.asyncio
    async def test_max_five_tool_calls_captured(self, in_memory_tracer):
        """Test that only first 5 tool calls get individual attributes"""
        tracer, exporter = in_memory_tracer

        # Create 10 tool calls
        tool_calls = [
            {
                "type": "function",
                "function": {"name": f"tool{i}", "arguments": "{}"}
            }
            for i in range(10)
        ]

        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_tool_calls(tool_calls)

        spans = exporter.get_finished_spans()
        span = spans[0]

        # Count should be 10
        assert span.attributes["llm.tool_calls.count"] == 10

        # But only 0-4 should have individual attributes
        assert "llm.tool_calls.0.name" in span.attributes
        assert "llm.tool_calls.4.name" in span.attributes
        assert "llm.tool_calls.5.name" not in span.attributes
