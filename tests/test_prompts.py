"""Tests for MCP prompts."""

import pytest

from govbrnews_mcp.server import (
    analyze_theme,
    compare_agencies,
    temporal_evolution,
    discover_context,
)


class TestAnalyzeThemePrompt:
    """Tests for analyze_theme prompt."""

    def test_analyze_theme_returns_messages(self):
        """Test that analyze_theme returns list of messages."""
        result = analyze_theme("educação")

        assert isinstance(result, list)
        assert len(result) > 0
        assert "role" in result[0]
        assert "content" in result[0]

    def test_analyze_theme_includes_theme_in_content(self):
        """Test that theme is included in prompt content."""
        theme = "meio ambiente"
        result = analyze_theme(theme)

        content_text = result[0]["content"]["text"]
        assert theme in content_text

    def test_analyze_theme_mentions_all_tools(self):
        """Test that prompt mentions all relevant tools."""
        result = analyze_theme("saúde")

        content_text = result[0]["content"]["text"]

        # Should mention key tools
        assert "search_news" in content_text
        assert "analyze_temporal" in content_text
        assert "get_facets" in content_text

    def test_analyze_theme_has_structured_analysis(self):
        """Test that prompt has structured analysis sections."""
        result = analyze_theme("educação")

        content_text = result[0]["content"]["text"]

        # Should have numbered sections
        assert "## 1." in content_text
        assert "## 2." in content_text
        assert "## 3." in content_text

        # Should mention key analysis aspects
        assert "Visão Geral" in content_text or "visão geral" in content_text.lower()
        assert "Agências" in content_text or "agências" in content_text.lower()
        assert "Temporal" in content_text or "temporal" in content_text.lower()


class TestCompareAgenciesPrompt:
    """Tests for compare_agencies prompt."""

    def test_compare_agencies_returns_messages(self):
        """Test that compare_agencies returns list of messages."""
        result = compare_agencies(["MEC", "INEP"])

        assert isinstance(result, list)
        assert len(result) > 0
        assert "role" in result[0]
        assert "content" in result[0]

    def test_compare_agencies_includes_all_agencies(self):
        """Test that all agencies are mentioned in prompt."""
        agencies = ["MMA", "IBAMA", "ICMBio"]
        result = compare_agencies(agencies)

        content_text = result[0]["content"]["text"]

        for agency in agencies:
            assert agency in content_text

    def test_compare_agencies_with_theme_filter(self):
        """Test compare_agencies with specific theme."""
        result = compare_agencies(["MS", "ANVISA"], theme="saúde")

        content_text = result[0]["content"]["text"]

        assert "MS" in content_text
        assert "ANVISA" in content_text
        assert "saúde" in content_text

    def test_compare_agencies_without_theme(self):
        """Test compare_agencies without theme filter."""
        result = compare_agencies(["MEC", "INEP"])

        content_text = result[0]["content"]["text"]

        # Should not mention specific theme when not provided
        assert "MEC" in content_text
        assert "INEP" in content_text

    def test_compare_agencies_mentions_comparison_tools(self):
        """Test that prompt mentions tools for comparison."""
        result = compare_agencies(["MMA", "IBAMA"])

        content_text = result[0]["content"]["text"]

        assert "search_news" in content_text
        assert "analyze_temporal" in content_text
        assert "get_facets" in content_text

    def test_compare_agencies_has_structured_comparison(self):
        """Test that prompt has structured comparison sections."""
        result = compare_agencies(["MEC", "INEP"])

        content_text = result[0]["content"]["text"]

        # Should have comparison sections
        assert "CADA" in content_text or "cada" in content_text
        assert "Compare" in content_text or "compare" in content_text.lower()


class TestTemporalEvolutionPrompt:
    """Tests for temporal_evolution prompt."""

    def test_temporal_evolution_returns_messages(self):
        """Test that temporal_evolution returns list of messages."""
        result = temporal_evolution("educação")

        assert isinstance(result, list)
        assert len(result) > 0
        assert "role" in result[0]
        assert "content" in result[0]

    def test_temporal_evolution_includes_query(self):
        """Test that query is included in prompt."""
        query = "meio ambiente"
        result = temporal_evolution(query)

        content_text = result[0]["content"]["text"]
        assert query in content_text

    def test_temporal_evolution_with_year_range(self):
        """Test temporal_evolution with year range."""
        result = temporal_evolution("educação", year_from=2020, year_to=2025)

        content_text = result[0]["content"]["text"]

        assert "2020" in content_text
        assert "2025" in content_text

    def test_temporal_evolution_with_year_from_only(self):
        """Test temporal_evolution with only year_from."""
        result = temporal_evolution("saúde", year_from=2023)

        content_text = result[0]["content"]["text"]

        assert "2023" in content_text
        assert "desde" in content_text.lower()

    def test_temporal_evolution_with_year_to_only(self):
        """Test temporal_evolution with only year_to."""
        result = temporal_evolution("segurança", year_to=2024)

        content_text = result[0]["content"]["text"]

        assert "2024" in content_text
        assert "até" in content_text.lower()

    def test_temporal_evolution_mentions_all_granularities(self):
        """Test that prompt mentions all temporal granularities."""
        result = temporal_evolution("educação")

        content_text = result[0]["content"]["text"]

        assert "yearly" in content_text
        assert "monthly" in content_text
        assert "weekly" in content_text

    def test_temporal_evolution_has_multi_scale_analysis(self):
        """Test that prompt has multi-scale temporal analysis."""
        result = temporal_evolution("educação")

        content_text = result[0]["content"]["text"]

        # Should mention different time scales
        assert "Longo Prazo" in content_text or "anual" in content_text.lower()
        assert "Médio Prazo" in content_text or "mensal" in content_text.lower()
        assert "Recente" in content_text or "semanal" in content_text.lower()


class TestDiscoverContextPrompt:
    """Tests for discover_context prompt."""

    def test_discover_context_returns_messages(self):
        """Test that discover_context returns list of messages."""
        result = discover_context("abc123")

        assert isinstance(result, list)
        assert len(result) > 0
        assert "role" in result[0]
        assert "content" in result[0]

    def test_discover_context_includes_news_id(self):
        """Test that news_id is included in prompt."""
        news_id = "news_2025_10_23_001"
        result = discover_context(news_id)

        content_text = result[0]["content"]["text"]
        assert news_id in content_text

    def test_discover_context_mentions_resource(self):
        """Test that prompt mentions news resource."""
        news_id = "test123"
        result = discover_context(news_id)

        content_text = result[0]["content"]["text"]

        assert "govbrnews://news/" in content_text
        assert news_id in content_text

    def test_discover_context_mentions_similar_news_tool(self):
        """Test that prompt mentions similar_news tool."""
        result = discover_context("abc123")

        content_text = result[0]["content"]["text"]

        assert "similar_news" in content_text

    def test_discover_context_mentions_search_tools(self):
        """Test that prompt mentions search and analysis tools."""
        result = discover_context("abc123")

        content_text = result[0]["content"]["text"]

        assert "search_news" in content_text
        assert "analyze_temporal" in content_text or "get_facets" in content_text

    def test_discover_context_has_contextual_sections(self):
        """Test that prompt has contextual analysis sections."""
        result = discover_context("abc123")

        content_text = result[0]["content"]["text"]

        # Should have different context dimensions
        assert "Contexto" in content_text
        assert "Similar" in content_text or "similares" in content_text.lower()
        assert "Temporal" in content_text or "temporal" in content_text.lower()


class TestPromptsIntegration:
    """Integration tests for all prompts."""

    def test_all_prompts_return_valid_structure(self):
        """Test that all prompts return valid MCP prompt structure."""
        prompts = [
            analyze_theme("test"),
            compare_agencies(["A", "B"]),
            temporal_evolution("test"),
            discover_context("id123"),
        ]

        for prompt_result in prompts:
            assert isinstance(prompt_result, list)
            assert len(prompt_result) > 0

            for message in prompt_result:
                assert "role" in message
                assert "content" in message
                assert message["role"] == "user"
                assert "type" in message["content"]
                assert "text" in message["content"]
                assert message["content"]["type"] == "text"
                assert len(message["content"]["text"]) > 0

    def test_all_prompts_mention_tools(self):
        """Test that all prompts mention relevant MCP tools."""
        prompts = [
            analyze_theme("test"),
            compare_agencies(["A", "B"]),
            temporal_evolution("test"),
            discover_context("id123"),
        ]

        for prompt_result in prompts:
            content_text = prompt_result[0]["content"]["text"]

            # All prompts should mention at least one tool
            assert any(
                tool in content_text
                for tool in ["search_news", "analyze_temporal", "get_facets", "similar_news"]
            )

    def test_all_prompts_have_structured_content(self):
        """Test that all prompts have structured markdown content."""
        prompts = [
            analyze_theme("test"),
            compare_agencies(["A", "B"]),
            temporal_evolution("test"),
            discover_context("id123"),
        ]

        for prompt_result in prompts:
            content_text = prompt_result[0]["content"]["text"]

            # Should have markdown headers
            assert "##" in content_text

            # Should have clear instructions
            assert any(
                keyword in content_text.lower()
                for keyword in ["use", "analise", "identifique", "compare", "resuma"]
            )
