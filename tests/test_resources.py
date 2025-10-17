"""Tests for MCP resources."""

import pytest
from unittest.mock import MagicMock, patch

from govbrnews_mcp.resources import (
    get_stats,
    format_stats,
    get_agencies,
    format_agencies,
    get_themes,
    format_themes,
    get_news_by_id,
    format_news,
)


class TestStatsResource:
    """Tests for stats resource."""

    @patch("govbrnews_mcp.resources.stats.get_typesense_client")
    def test_get_stats_success(self, mock_get_client):
        """Test getting stats successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock collection info
        mock_client.get_collection_info.return_value = {
            "num_documents": 295511
        }

        # Mock year distribution
        mock_client._client.collections.__getitem__.return_value.documents.search.return_value = {
            "facet_counts": [
                {
                    "field_name": "year",
                    "counts": [
                        {"value": "2025", "count": 50000},
                        {"value": "2024", "count": 100000},
                    ]
                }
            ]
        }

        # Mock search for coverage period
        mock_client.search.side_effect = [
            {  # Oldest
                "found": 1,
                "hits": [{"document": {"published_at": 1609459200}}]
            },
            {  # Newest
                "found": 1,
                "hits": [{"document": {"published_at": 1735689600}}]
            }
        ]

        stats = get_stats()

        assert stats["total_documents"] == 295511
        assert "year_distribution" in stats
        assert "top_agencies" in stats
        assert "coverage_period" in stats

    @patch("govbrnews_mcp.resources.stats.get_typesense_client")
    def test_get_stats_no_collection_info(self, mock_get_client):
        """Test getting stats when collection info fails."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_collection_info.return_value = None

        stats = get_stats()

        assert "error" in stats
        assert stats["total_documents"] == 0

    def test_format_stats(self):
        """Test formatting stats."""
        stats = {
            "total_documents": 295511,
            "year_distribution": {
                "2025": 50000,
                "2024": 100000,
            },
            "top_agencies": [
                {"agency": "MEC", "count": 10000},
                {"agency": "MS", "count": 8000},
            ],
            "coverage_period": {
                "start_date_formatted": "01/01/2021",
                "end_date_formatted": "01/01/2025",
            }
        }

        result = format_stats(stats)

        assert "# Estatísticas do Dataset GovBRNews" in result
        assert "295,511" in result
        assert "MEC" in result
        assert "2025" in result

    def test_format_stats_error(self):
        """Test formatting stats with error."""
        stats = {"error": "Test error"}

        result = format_stats(stats)

        assert "# Erro" in result
        assert "Test error" in result


class TestAgenciesResource:
    """Tests for agencies resource."""

    @patch("govbrnews_mcp.resources.agencies.get_typesense_client")
    def test_get_agencies_success(self, mock_get_client):
        """Test getting agencies successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "facet_counts": [
                {
                    "field_name": "agency",
                    "counts": [
                        {"value": "MEC", "count": 10000},
                        {"value": "MS", "count": 8000},
                        {"value": "MJ", "count": 5000},
                    ]
                }
            ]
        }

        agencies = get_agencies()

        assert agencies["total_agencies"] == 3
        assert len(agencies["agencies"]) == 3
        assert agencies["agencies"][0]["agency"] == "MEC"
        assert agencies["agencies"][0]["count"] == 10000

    @patch("govbrnews_mcp.resources.agencies.get_typesense_client")
    def test_get_agencies_error(self, mock_get_client):
        """Test getting agencies with error."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.client.collections.__getitem__.side_effect = Exception("API error")

        agencies = get_agencies()

        assert "error" in agencies
        assert agencies["agencies"] == []

    def test_format_agencies(self):
        """Test formatting agencies."""
        agencies_data = {
            "total_agencies": 3,
            "agencies": [
                {"agency": "MEC", "count": 10000},
                {"agency": "MS", "count": 8000},
            ]
        }

        result = format_agencies(agencies_data)

        assert "# Agências Governamentais" in result
        assert "Total de agências:** 3" in result
        assert "MEC" in result
        assert "10,000" in result

    def test_format_agencies_error(self):
        """Test formatting agencies with error."""
        agencies_data = {"error": "Test error"}

        result = format_agencies(agencies_data)

        assert "# Erro" in result
        assert "Test error" in result


class TestThemesResource:
    """Tests for themes resource."""

    @patch("govbrnews_mcp.resources.themes.get_typesense_client")
    def test_get_themes_success(self, mock_get_client):
        """Test getting themes successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "facet_counts": [
                {
                    "field_name": "theme_1_level_1",
                    "counts": [
                        {"value": "02 - Educação", "count": 50000},
                        {"value": "03 - Saúde", "count": 40000},
                        {"value": "05 - Meio Ambiente e Sustentabilidade", "count": 30000},
                    ]
                }
            ]
        }

        themes = get_themes()

        assert themes["total_themes"] == 3
        assert len(themes["themes"]) == 3
        assert themes["themes"][0]["theme"] == "02 - Educação"
        assert themes["themes"][0]["count"] == 50000

    @patch("govbrnews_mcp.resources.themes.get_typesense_client")
    def test_get_themes_error(self, mock_get_client):
        """Test getting themes with error."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.client.collections.__getitem__.side_effect = Exception("API error")

        themes = get_themes()

        assert "error" in themes
        assert themes["themes"] == []

    def test_format_themes(self):
        """Test formatting themes."""
        themes_data = {
            "total_themes": 2,
            "themes": [
                {"theme": "02 - Educação", "count": 50000},
                {"theme": "03 - Saúde", "count": 40000},
            ]
        }

        result = format_themes(themes_data)

        assert "# Taxonomia de Temas" in result
        assert "Total de temas:** 2" in result
        assert "02 - Educação" in result
        assert "50,000" in result

    def test_format_themes_error(self):
        """Test formatting themes with error."""
        themes_data = {"error": "Test error"}

        result = format_themes(themes_data)

        assert "# Erro" in result
        assert "Test error" in result


class TestNewsResource:
    """Tests for individual news resource."""

    @patch("govbrnews_mcp.resources.news.get_typesense_client")
    def test_get_news_by_id_success(self, mock_get_client):
        """Test getting news by ID successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_document = {
            "id": "123",
            "title": "Test News",
            "content": "Test content",
            "agency": "MEC",
            "published_at": 1609459200,
            "year": 2021,
        }
        mock_client.get_document.return_value = mock_document

        news = get_news_by_id("123")

        assert news["id"] == "123"
        assert news["title"] == "Test News"
        assert news["agency"] == "MEC"

    @patch("govbrnews_mcp.resources.news.get_typesense_client")
    def test_get_news_by_id_not_found(self, mock_get_client):
        """Test getting news by ID when not found."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_document.return_value = None

        news = get_news_by_id("999")

        assert "error" in news
        assert "999" in news["error"]

    @patch("govbrnews_mcp.resources.news.get_typesense_client")
    def test_get_news_by_id_error(self, mock_get_client):
        """Test getting news by ID with error."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_document.side_effect = Exception("API error")

        news = get_news_by_id("123")

        assert "error" in news
        assert "API error" in news["error"]

    def test_format_news(self):
        """Test formatting news."""
        news = {
            "id": "123",
            "title": "Test News",
            "content": "Test content",
            "agency": "MEC",
            "published_at": 1609459200,
            "year": 2021,
            "category": "EDUCAÇÃO",
            "theme": "02 - Educação",
            "url": "https://example.com/news/123",
        }

        result = format_news(news)

        assert "# Test News" in result
        assert "MEC" in result
        assert "2021" in result
        assert "Test content" in result
        assert "https://example.com/news/123" in result

    def test_format_news_minimal(self):
        """Test formatting news with minimal data."""
        news = {
            "title": "Test News",
            "content": "Test content",
        }

        result = format_news(news)

        assert "# Test News" in result
        assert "Test content" in result

    def test_format_news_error(self):
        """Test formatting news with error."""
        news = {"error": "Not found", "id": "999"}

        result = format_news(news)

        assert "# Erro" in result
        assert "Not found" in result
