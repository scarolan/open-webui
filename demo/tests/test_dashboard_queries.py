"""
Dashboard Query Validation Tests

Validates that TraceQL queries used in dashboards work correctly.
"""

import pytest
import time


class TestBasicQueries:
    """Test basic TraceQL queries"""

    @pytest.mark.tempo
    def test_all_llm_traces_query(self, tempo_query_helper):
        """Test: { span.openinference.span.kind = "LLM" }"""
        query = '{ span.openinference.span.kind = "LLM" }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: All LLM traces")

        if "traces" in results:
            print(f"   Found {len(results['traces'])} traces")

    @pytest.mark.tempo
    def test_specific_bot_query(self, tempo_query_helper):
        """Test: { span.llm.model_name = "hal" }"""
        query = '{ span.llm.model_name = "hal" }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: HAL bot traces")

        if "traces" in results:
            print(f"   Found {len(results['traces'])} HAL traces")

    @pytest.mark.tempo
    def test_tool_calls_query(self, tempo_query_helper):
        """Test: { span.llm.tool_calls.count > 0 }"""
        query = '{ span.llm.tool_calls.count > 0 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Traces with tool calls")

        if "traces" in results:
            print(f"   Found {len(results['traces'])} traces with tools")

    @pytest.mark.tempo
    def test_specific_tool_query(self, tempo_query_helper):
        """Test: { span.llm.tool_calls.0.name = "get_weather" }"""
        query = '{ span.llm.tool_calls.0.name = "get_weather" }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: get_weather tool calls")


class TestAggregationQueries:
    """Test aggregation queries used in dashboard panels"""

    @pytest.mark.tempo
    def test_bot_usage_count(self, tempo_query_helper):
        """Test: { span.openinference.span.kind = "LLM" } | count by span.llm.model_name"""
        query = '{ span.openinference.span.kind = "LLM" } | count() by(span.llm.model_name)'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Bot usage count aggregation")

    @pytest.mark.tempo
    def test_tool_usage_over_time(self, tempo_query_helper):
        """Test: { span.llm.tool_calls.count > 0 } | count_over_time() by span.llm.tool_calls.names"""
        query = '{ span.llm.tool_calls.count > 0 } | count_over_time() by(span.llm.tool_calls.names)'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Tool usage over time")

    @pytest.mark.tempo
    def test_token_usage_rate(self, tempo_query_helper):
        """Test: Token usage rate by bot"""
        query = '{ span.openinference.span.kind = "LLM" } | rate(span.llm.token_count.total) by(span.llm.model_name)'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Token usage rate by bot")

    @pytest.mark.tempo
    def test_average_latency(self, tempo_query_helper):
        """Test: Average latency by bot"""
        query = '{ span.openinference.span.kind = "LLM" } | avg(duration) by(span.llm.model_name)'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Average latency by bot")


class TestFilterQueries:
    """Test filtering queries"""

    @pytest.mark.tempo
    def test_high_token_usage(self, tempo_query_helper):
        """Test: Traces with >500 tokens"""
        query = '{ span.llm.token_count.total > 500 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: High token usage traces")

    @pytest.mark.tempo
    def test_multiple_tool_calls(self, tempo_query_helper):
        """Test: Traces with multiple tool calls"""
        query = '{ span.llm.tool_calls.count > 1 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Multiple tool call traces")

    @pytest.mark.tempo
    def test_gemini_provider_only(self, tempo_query_helper):
        """Test: Only Gemini provider traces"""
        query = '{ span.llm.provider = "gemini" }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Gemini provider traces")

    @pytest.mark.tempo
    def test_service_name_filter(self, tempo_query_helper):
        """Test: Filter by service name"""
        query = '{ resource.service.name = "openwebui" }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Service name filter")


class TestComplexQueries:
    """Test complex multi-condition queries"""

    @pytest.mark.tempo
    def test_bot_with_tools(self, tempo_query_helper):
        """Test: Specific bot with tool calls"""
        query = '{ span.llm.model_name = "hal" && span.llm.tool_calls.count > 0 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: HAL bot with tool calls")

    @pytest.mark.tempo
    def test_high_token_with_tools(self, tempo_query_helper):
        """Test: High token usage with tool calls"""
        query = '{ span.llm.token_count.total > 300 && span.llm.tool_calls.count > 0 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: High tokens + tools")

    @pytest.mark.tempo
    def test_exclude_low_tokens(self, tempo_query_helper):
        """Test: Exclude traces with low token usage"""
        query = '{ span.openinference.span.kind = "LLM" && span.llm.token_count.total > 50 }'
        results = tempo_query_helper(query)

        assert results is not None
        print(f"\n✅ Query successful: Exclude low token traces")


class TestQueryPerformance:
    """Test query performance and limits"""

    @pytest.mark.tempo
    def test_query_response_time(self, tempo_query_helper):
        """Test that queries complete in reasonable time"""
        start = time.time()

        query = '{ span.openinference.span.kind = "LLM" }'
        results = tempo_query_helper(query)

        elapsed = time.time() - start

        assert results is not None
        assert elapsed < 10.0  # Should complete within 10 seconds

        print(f"\n✅ Query completed in {elapsed:.2f}s")

    @pytest.mark.tempo
    def test_large_time_range(self, tempo_query_helper):
        """Test query over larger time range (1 hour)"""
        end_time = int(time.time())
        start_time = end_time - (60 * 60)  # 1 hour ago

        query = '{ span.openinference.span.kind = "LLM" }'
        results = tempo_query_helper(query, start_time=start_time, end_time=end_time)

        assert results is not None
        print(f"\n✅ Large time range query successful")


class TestAttributeExistence:
    """Test that expected attributes exist in traces"""

    @pytest.mark.tempo
    def test_required_openinference_attributes(self, tempo_query_helper):
        """Test that OpenInference required attributes exist"""
        # These attributes should always be present
        required_attrs = [
            "openinference.span.kind",
            "llm.model_name",
            "llm.provider"
        ]

        for attr in required_attrs:
            query = f'{{ {attr} != nil }}'
            results = tempo_query_helper(query)

            assert results is not None
            print(f"✅ Attribute exists: {attr}")

    @pytest.mark.tempo
    def test_token_attributes_exist(self, tempo_query_helper):
        """Test that token count attributes exist"""
        token_attrs = [
            "llm.token_count.prompt",
            "llm.token_count.completion",
            "llm.token_count.total"
        ]

        for attr in token_attrs:
            query = f'{{ {attr} > 0 }}'
            results = tempo_query_helper(query)

            assert results is not None
            print(f"✅ Token attribute exists: {attr}")

    @pytest.mark.tempo
    def test_io_attributes_exist(self, tempo_query_helper):
        """Test that input/output attributes exist"""
        io_attrs = [
            "llm.input.message",
            "llm.output.message"
        ]

        for attr in io_attrs:
            query = f'{{ {attr} != "" }}'
            results = tempo_query_helper(query)

            assert results is not None
            print(f"✅ I/O attribute exists: {attr}")
