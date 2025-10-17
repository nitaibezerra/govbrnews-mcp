"""Tests for advanced tools (facets and similar)."""

import pytest
from unittest.mock import MagicMock, patch

from govbrnews_mcp.tools.facets import get_facets
from govbrnews_mcp.tools.similar import similar_news


class TestGetFacetsTool:
    """Tests for get_facets tool."""

    @patch("govbrnews_mcp.tools.facets.get_typesense_client")
    def test_get_facets_success(self, mock_get_client):
        """Test getting facets successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 50211,
            "facet_counts": [
                {
                    "field_name": "agency",
                    "counts": [
                        {"value": "mec", "count": 5326},
                        {"value": "capes", "count": 6102},
                    ]
                }
            ]
        }

        result = get_facets(["agency"], query="educação")

        assert "# Agregações" in result
        assert "mec" in result
        assert "5,326" in result

    @patch("govbrnews_mcp.tools.facets.get_typesense_client")
    def test_get_facets_multiple_fields(self, mock_get_client):
        """Test getting facets for multiple fields."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 10000,
            "facet_counts": [
                {
                    "field_name": "agency",
                    "counts": [{"value": "mec", "count": 5000}]
                },
                {
                    "field_name": "published_year",
                    "counts": [{"value": "2025", "count": 3000}]
                }
            ]
        }

        result = get_facets(["agency", "published_year"])

        assert "Agências" in result
        assert "Anos" in result
        assert "mec" in result
        assert "2025" in result

    def test_get_facets_invalid_fields(self):
        """Test get_facets with invalid fields."""
        result = get_facets(["invalid_field"])

        assert "# Erro" in result
        assert "invalid_field" in result
        assert "Campos válidos" in result

    def test_get_facets_empty_fields(self):
        """Test get_facets with empty field list."""
        result = get_facets([])

        assert "# Erro" in result
        assert "Nenhum campo de facet especificado" in result

    @patch("govbrnews_mcp.tools.facets.get_typesense_client")
    def test_get_facets_limit_adjustment(self, mock_get_client):
        """Test that max_values is adjusted if out of range."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 1000,
            "facet_counts": []
        }

        # Should adjust to 100
        result = get_facets(["agency"], max_values=500)

        # Verify it was called with max 100
        call_args = mock_client.client.collections.__getitem__.return_value.documents.search.call_args
        assert call_args[0][0]["max_facet_values"] == 100

    @patch("govbrnews_mcp.tools.facets.get_typesense_client")
    def test_get_facets_no_results(self, mock_get_client):
        """Test get_facets when no aggregations found."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 0,
            "facet_counts": []
        }

        result = get_facets(["agency"])

        assert "Nenhuma agregação encontrada" in result

    @patch("govbrnews_mcp.tools.facets.get_typesense_client")
    def test_get_facets_error_handling(self, mock_get_client):
        """Test get_facets error handling."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.side_effect = Exception("API error")

        result = get_facets(["agency"])

        assert "# Erro ao Obter Agregações" in result
        assert "API error" in result


class TestSimilarNewsTool:
    """Tests for similar_news tool."""

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_success(self, mock_get_client):
        """Test finding similar news successfully."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock reference document
        mock_client.get_document.return_value = {
            "id": "123",
            "title": "Test News",
            "agency": "mec",
            "theme_1_level_1": "02 - Educação",
            "published_year": 2025
        }

        # Mock similar documents
        mock_client.search.return_value = {
            "found": 2,
            "hits": [
                {
                    "document": {
                        "id": "123",  # Reference itself
                        "title": "Test News",
                        "agency": "mec"
                    }
                },
                {
                    "document": {
                        "id": "124",
                        "title": "Similar News 1",
                        "agency": "mec",
                        "published_at": 1609459200
                    }
                }
            ]
        }

        result = similar_news("123", limit=5)

        assert "# Notícias Similares" in result
        assert "Test News" in result
        assert "Similar News 1" in result
        assert "123" not in result.split("---")[1]  # Reference should be excluded from results

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_reference_not_found(self, mock_get_client):
        """Test similar_news when reference document not found."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.get_document.side_effect = Exception("Not found")

        result = similar_news("999")

        assert "# Erro" in result
        assert "999" in result
        assert "não encontrada" in result

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_no_similar_found(self, mock_get_client):
        """Test similar_news when no similar documents found."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock reference document
        mock_client.get_document.return_value = {
            "id": "123",
            "title": "Test News",
            "agency": "mec",
            "theme_1_level_1": "02 - Educação",
            "published_year": 2025
        }

        # Mock empty results (only reference itself)
        mock_client.search.return_value = {
            "found": 1,
            "hits": [
                {
                    "document": {
                        "id": "123",
                        "title": "Test News"
                    }
                }
            ]
        }

        result = similar_news("123")

        assert "Nenhuma notícia similar encontrada" in result

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_limit_adjustment(self, mock_get_client):
        """Test that limit is adjusted if out of range."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.get_document.return_value = {
            "id": "123",
            "title": "Test",
            "agency": "mec"
        }

        mock_client.search.return_value = {
            "found": 0,
            "hits": []
        }

        # Should adjust to 20
        result = similar_news("123", limit=100)

        # Verify it was called with max 21 (20 + 1 for reference)
        call_args = mock_client.search.call_args
        assert call_args[0][1]["per_page"] == 21

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_without_filters(self, mock_get_client):
        """Test similar_news with minimal reference data."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Reference with only year
        mock_client.get_document.return_value = {
            "id": "123",
            "title": "Test",
            "published_year": 2025
        }

        mock_client.search.return_value = {
            "found": 1,
            "hits": [
                {
                    "document": {
                        "id": "124",
                        "title": "Similar",
                        "published_at": 1609459200
                    }
                }
            ]
        }

        result = similar_news("123")

        assert "# Notícias Similares" in result

    @patch("govbrnews_mcp.tools.similar.get_typesense_client")
    def test_similar_news_error_handling(self, mock_get_client):
        """Test similar_news error handling."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.get_document.return_value = {
            "id": "123",
            "title": "Test"
        }

        mock_client.search.side_effect = Exception("Search error")

        result = similar_news("123")

        assert "# Erro ao Buscar Notícias Similares" in result
        assert "Search error" in result
