"""Pytest configuration and fixtures for GovBRNews MCP Server tests."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_typesense_search_response():
    """Mock successful search response from Typesense."""
    return {
        "found": 3,
        "hits": [
            {
                "document": {
                    "unique_id": "test1",
                    "title": "Notícia sobre educação",
                    "agency": "Ministério da Educação",
                    "published_at": 1704067200,  # 2024-01-01
                    "category": "Educação",
                    "theme_1_level_1": "Educação e Cultura",
                    "url": "https://example.gov.br/noticia1",
                    "content": "Conteúdo da notícia sobre educação...",
                }
            },
            {
                "document": {
                    "unique_id": "test2",
                    "title": "Programa educacional lançado",
                    "agency": "Ministério da Educação",
                    "published_at": 1704153600,  # 2024-01-02
                    "category": "Educação",
                    "url": "https://example.gov.br/noticia2",
                    "content": "Novo programa educacional...",
                }
            },
            {
                "document": {
                    "unique_id": "test3",
                    "title": "Investimento em escolas",
                    "agency": "Ministério da Educação",
                    "published_at": 1704240000,  # 2024-01-03
                    "url": "https://example.gov.br/noticia3",
                }
            },
        ],
    }


@pytest.fixture
def mock_typesense_collection_info():
    """Mock collection info response."""
    return {
        "name": "news",
        "num_documents": 295511,
        "fields": [
            {"name": "unique_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "agency", "type": "string", "facet": True},
            {"name": "published_at", "type": "int64"},
            {"name": "published_year", "type": "int32", "facet": True},
        ],
        "default_sorting_field": "published_at",
    }


@pytest.fixture
def mock_typesense_facets_response():
    """Mock faceted search response."""
    return {
        "found": 10000,
        "facet_counts": [
            {
                "field_name": "agency",
                "counts": [
                    {"value": "Ministério da Educação", "count": 5432},
                    {"value": "Ministério da Saúde", "count": 4321},
                    {"value": "Ministério da Economia", "count": 3210},
                ],
            }
        ],
        "hits": [],
    }


@pytest.fixture
def mock_typesense_client(
    mock_typesense_search_response, mock_typesense_collection_info
):
    """Mock Typesense client."""
    mock_client = MagicMock()

    # Mock search method
    mock_client.search.return_value = mock_typesense_search_response

    # Mock get_collection_info
    mock_client.get_collection_info.return_value = mock_typesense_collection_info

    # Mock health_check
    mock_client.health_check.return_value = True

    return mock_client


@pytest.fixture
def mock_settings():
    """Mock settings with test values."""
    with patch("govbrnews_mcp.config.settings") as mock:
        mock.typesense_host = "localhost"
        mock.typesense_port = 8108
        mock.typesense_protocol = "http"
        mock.typesense_api_key = "test_api_key"
        mock.cache_ttl = 300
        mock.log_level = "INFO"
        yield mock
