"""LLM Observability Instrumentation for Open WebUI

This module provides OpenInference-compliant OpenTelemetry instrumentation
for LLM API calls. It captures:
- Token counts (prompt, completion, total)
- Model names and providers
- Input/output messages (truncated for span efficiency)
- Latency metrics
- Error tracking

Follows OpenInference semantic conventions:
https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md
"""

from __future__ import annotations

import time
import json
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.metrics import get_meter

logger = logging.getLogger(__name__)

# Get tracer for creating spans
tracer = trace.get_tracer(__name__)

# Get meter for recording metrics
meter = get_meter(__name__)

# LLM Token usage counter
llm_tokens_counter = meter.create_counter(
    name="llm.tokens.total",
    description="Total tokens consumed by LLM API calls",
    unit="tokens"
)

# LLM request counter
llm_requests_counter = meter.create_counter(
    name="llm.requests.total",
    description="Total LLM API requests by provider and model",
    unit="requests"
)

# LLM request duration histogram
llm_duration_histogram = meter.create_histogram(
    name="llm.request.duration",
    description="LLM API request duration distribution",
    unit="ms"
)


class LLMSpanManager:
    """Context manager for instrumenting LLM API calls with OpenInference attributes

    Usage:
        async with LLMSpanManager(model="gpt-4", provider="openai") as llm_span:
            llm_span.set_input(messages)
            response = await make_llm_call()
            llm_span.set_usage(response["usage"])
            llm_span.set_output(response["choices"][0]["message"]["content"])
    """

    def __init__(
        self,
        model: str,
        provider: str = "openai",
        operation_name: Optional[str] = None
    ):
        """Initialize LLM span manager

        Args:
            model: Model name (e.g., "gpt-4", "gemini-2.0-flash-exp")
            provider: Provider name (e.g., "openai", "gemini", "azure", "ollama")
            operation_name: Optional operation name (defaults to "llm.{provider}.chat")
        """
        self.model = model
        self.provider = provider
        self.operation_name = operation_name or f"llm.{provider}.chat"
        self.span = None
        self.start_time = None
        self.usage_data: Optional[Dict[str, int]] = None

    async def __aenter__(self):
        """Async context manager entry - start span"""
        self.start_time = time.time()

        # Create LLM span with CLIENT kind (external API call)
        self.span = tracer.start_span(
            self.operation_name,
            kind=SpanKind.CLIENT
        )

        # Set OpenInference span kind (required)
        self.span.set_attribute("openinference.span.kind", "LLM")

        # Set LLM metadata
        self.span.set_attribute("llm.model_name", self.model)
        self.span.set_attribute("llm.provider", self.provider)

        # Set generic span type for filtering
        self.span.set_attribute("span_type", "llm")

        logger.debug(f"Started LLM span: {self.operation_name} (model={self.model}, provider={self.provider})")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - end span and record metrics"""
        try:
            # Calculate duration
            duration_ms = (time.time() - self.start_time) * 1000

            # Record metrics
            metric_attributes = {
                "model": self.model,
                "provider": self.provider
            }

            # Record request count
            llm_requests_counter.add(1, metric_attributes)

            # Record duration
            llm_duration_histogram.record(duration_ms, metric_attributes)

            # Record token usage if available
            if self.usage_data:
                total_tokens = self.usage_data.get("total_tokens", 0)
                if total_tokens > 0:
                    llm_tokens_counter.add(total_tokens, metric_attributes)

            # Set span status
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
                logger.error(f"LLM span failed: {exc_val}", exc_info=True)
            else:
                self.span.set_status(Status(StatusCode.OK))
                logger.debug(f"Completed LLM span: {self.operation_name} ({duration_ms:.2f}ms)")

        finally:
            self.span.end()

    def set_usage(self, usage_dict: Optional[Dict[str, int]]):
        """Set token usage attributes from LLM API response

        Args:
            usage_dict: Token usage dict with keys: prompt_tokens, completion_tokens, total_tokens
                       Example: {"prompt_tokens": 150, "completion_tokens": 200, "total_tokens": 350}
        """
        if not usage_dict or not self.span or not self.span.is_recording():
            return

        self.usage_data = usage_dict

        prompt_tokens = usage_dict.get("prompt_tokens", 0)
        completion_tokens = usage_dict.get("completion_tokens", 0)
        total_tokens = usage_dict.get("total_tokens", 0)

        # Set OpenInference token count attributes
        self.span.set_attribute("llm.token_count.prompt", prompt_tokens)
        self.span.set_attribute("llm.token_count.completion", completion_tokens)
        self.span.set_attribute("llm.token_count.total", total_tokens)

        logger.debug(f"Set token usage: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")

    def set_input(self, messages: Optional[List[Dict[str, Any]]]):
        """Capture input prompt from messages array

        Args:
            messages: OpenAI-style messages array
                     Example: [{"role": "user", "content": "What is the capital of France?"}]
        """
        if not messages or not self.span or not self.span.is_recording():
            return

        try:
            # Find last user message
            last_user_msg = None
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    last_user_msg = msg
                    break

            if last_user_msg:
                content = last_user_msg.get("content", "")

                # Handle string content
                if isinstance(content, str):
                    # Truncate to 1000 chars to avoid span bloat
                    truncated_content = content[:1000]
                    self.span.set_attribute("llm.input.message", truncated_content)

                    if len(content) > 1000:
                        logger.debug(f"Truncated input message: {len(content)} -> 1000 chars")

                # Handle array content (multimodal)
                elif isinstance(content, list):
                    text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
                    combined_text = " ".join(text_parts)[:1000]
                    self.span.set_attribute("llm.input.message", combined_text)

        except Exception as e:
            logger.warning(f"Failed to set input message: {e}")

    def set_output(self, content: Optional[str], tool_calls: Optional[list] = None):
        """Capture output response from LLM

        Args:
            content: LLM response text
            tool_calls: Optional list of tool calls from the response
        """
        if not self.span or not self.span.is_recording():
            return

        try:
            # DEBUG: Log what we received
            logger.info(f"🔍 set_output called: content_len={len(content) if content else 0}, tool_calls={tool_calls is not None}")
            if content:
                logger.info(f"🔍 Content preview (first 200 chars): {str(content)[:200]}")

            # Set content if present
            if content:
                # Truncate to 1000 chars
                truncated_content = str(content)[:1000]
                self.span.set_attribute("llm.output.message", truncated_content)

                if len(content) > 1000:
                    logger.debug(f"Truncated output message: {len(content)} -> 1000 chars")

                # Try to parse content as JSON to extract embedded tool calls (OpenWebUI bot format)
                if not tool_calls:
                    logger.info("🔍 No tool_calls provided, attempting to parse content as JSON")
                    try:
                        content_json = json.loads(content)
                        logger.info(f"🔍 Parsed JSON successfully, keys: {list(content_json.keys()) if isinstance(content_json, dict) else 'not a dict'}")
                        if isinstance(content_json, dict) and "tool_calls" in content_json:
                            # Found tool calls embedded in content JSON
                            embedded_tool_calls = content_json["tool_calls"]
                            logger.info(f"✅ Found embedded tool calls in content: {embedded_tool_calls}")
                            # Convert to OpenAI format for consistency
                            tool_calls = self._convert_embedded_tool_calls(embedded_tool_calls)
                        else:
                            logger.info("🔍 No 'tool_calls' key in parsed JSON")
                    except json.JSONDecodeError as e:
                        logger.info(f"🔍 Content is not valid JSON: {e}")
                    except ValueError as e:
                        logger.info(f"🔍 ValueError parsing content: {e}")

            # Set tool calls if present
            if tool_calls:
                self.set_tool_calls(tool_calls)

        except Exception as e:
            logger.warning(f"Failed to set output message: {e}")

    def _convert_embedded_tool_calls(self, embedded_calls: list) -> list:
        """Convert OpenWebUI bot tool call format to OpenAI format

        OpenWebUI bot format:
            [{"name": "pod_bay_doors", "parameters": {"action": "status"}}]

        OpenAI format:
            [{"function": {"name": "pod_bay_doors", "arguments": "{...}"}, "type": "function"}]

        Args:
            embedded_calls: List of tool calls in OpenWebUI bot format

        Returns:
            List of tool calls in OpenAI format
        """
        converted = []
        for call in embedded_calls:
            if isinstance(call, dict) and "name" in call:
                # Convert to OpenAI format
                openai_call = {
                    "function": {
                        "name": call["name"],
                        "arguments": json.dumps(call.get("parameters", {}))
                    },
                    "type": "function"
                }
                converted.append(openai_call)

        logger.info(f"🔄 Converted {len(converted)} embedded tool calls to OpenAI format")
        return converted

    def set_tool_calls(self, tool_calls: Optional[list]):
        """Capture tool calls from LLM response

        Args:
            tool_calls: List of tool call objects from response
        """
        if not tool_calls or not self.span or not self.span.is_recording():
            return

        try:
            # DEBUG: Log the raw tool_calls structure
            logger.info(f"DEBUG: Received tool_calls structure: {json.dumps(tool_calls, indent=2)[:1000]}")

            # Extract tool names
            tool_names = []
            for i, tool_call in enumerate(tool_calls):
                if isinstance(tool_call, dict):
                    # OpenAI format: tool_calls[0].function.name
                    if "function" in tool_call:
                        tool_name = tool_call["function"].get("name", "unknown")
                        tool_names.append(tool_name)

                        # Set individual tool call attributes (limit to first 5)
                        if i < 5:
                            self.span.set_attribute(f"llm.tool_calls.{i}.name", tool_name)

                            # Set function arguments if present (truncated)
                            if "arguments" in tool_call["function"]:
                                args = str(tool_call["function"]["arguments"])[:500]
                                self.span.set_attribute(f"llm.tool_calls.{i}.arguments", args)

            # Set overall tool call indicator
            if tool_names:
                self.span.set_attribute("llm.tool_calls.count", len(tool_names))
                self.span.set_attribute("llm.tool_calls.names", ",".join(tool_names))
                logger.info(f"✅ CAPTURED {len(tool_names)} TOOL CALLS: {tool_names}")
            else:
                logger.warning(f"⚠️ NO TOOL NAMES EXTRACTED from tool_calls")

        except Exception as e:
            logger.warning(f"Failed to set tool calls: {e}")

    def set_invocation_parameters(self, params: Optional[Dict[str, Any]]):
        """Set LLM invocation parameters (temperature, max_tokens, etc.)

        Args:
            params: Dictionary of invocation parameters
        """
        if not params or not self.span or not self.span.is_recording():
            return

        try:
            # Common parameters
            if "temperature" in params:
                self.span.set_attribute("llm.temperature", float(params["temperature"]))

            if "max_tokens" in params:
                self.span.set_attribute("llm.max_tokens", int(params["max_tokens"]))

            if "top_p" in params:
                self.span.set_attribute("llm.top_p", float(params["top_p"]))

            if "top_k" in params:
                self.span.set_attribute("llm.top_k", int(params["top_k"]))

            if "stream" in params:
                self.span.set_attribute("llm.stream", bool(params["stream"]))

        except Exception as e:
            logger.warning(f"Failed to set invocation parameters: {e}")


def ollama_usage_to_openai(ollama_response: Dict[str, Any]) -> Dict[str, int]:
    """Convert Ollama usage format to OpenAI-compatible format

    Ollama returns:
        {"prompt_eval_count": 150, "eval_count": 200}

    OpenAI expects:
        {"prompt_tokens": 150, "completion_tokens": 200, "total_tokens": 350}

    Args:
        ollama_response: Ollama API response dict

    Returns:
        OpenAI-compatible usage dict
    """
    prompt_tokens = ollama_response.get("prompt_eval_count", 0)
    completion_tokens = ollama_response.get("eval_count", 0)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens
    }


def detect_provider_from_url(url: str) -> str:
    """Detect LLM provider from API endpoint URL

    Args:
        url: API endpoint URL

    Returns:
        Provider name (openai, gemini, azure, anthropic, etc.)
    """
    url_lower = url.lower()

    if "generativelanguage.googleapis.com" in url_lower:
        return "gemini"
    elif "api.openai.com" in url_lower:
        return "openai"
    elif "openai.azure.com" in url_lower:
        return "azure"
    elif "api.anthropic.com" in url_lower:
        return "anthropic"
    elif "api.cohere.ai" in url_lower:
        return "cohere"
    else:
        return "openai"  # default fallback
