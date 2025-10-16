"""Tests for search_news tool."""

import pytest
from unittest.mock import patch, MagicMock
from typesense.exceptions import TypesenseClientError


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_basic(mock_client, mock_typesense_search_response):
    """Test basic search functionality."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    result = search_news("educação")

    # Verify search was called correctly
    mock_client.search.assert_called_once()
    call_args = mock_client.search.call_args[0]
    assert call_args[0] == "news"  # collection name

    search_params = call_args[1]
    assert search_params["q"] == "educação"
    assert search_params["query_by"] == "title,content"
    assert search_params["per_page"] == 10

    # Verify result formatting
    assert "# Resultados da Busca" in result
    assert "3 notícias" in result
    assert "Notícia sobre educação" in result


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_with_agency_filter(mock_client, mock_typesense_search_response):
    """Test search with agency filter."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    result = search_news("educação", agencies=["Ministério da Educação"])

    # Verify filter was applied
    call_args = mock_client.search.call_args[0][1]
    assert "filter_by" in call_args
    assert "agency:=" in call_args["filter_by"]
    assert "Ministério da Educação" in call_args["filter_by"]


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_with_year_range(mock_client, mock_typesense_search_response):
    """Test search with year range filter."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    result = search_news("educação", year_from=2023, year_to=2024)

    # Verify year filters
    call_args = mock_client.search.call_args[0][1]
    assert "filter_by" in call_args
    assert "published_year:>=2023" in call_args["filter_by"]
    assert "published_year:<=2024" in call_args["filter_by"]


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_with_themes(mock_client, mock_typesense_search_response):
    """Test search with theme filter."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    result = search_news("educação", themes=["Educação e Cultura"])

    # Verify theme filter
    call_args = mock_client.search.call_args[0][1]
    assert "filter_by" in call_args
    assert "theme_1_level_1:=" in call_args["filter_by"]


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_limit_validation(mock_client, mock_typesense_search_response):
    """Test that limit is clamped to 1-100 range."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    # Test limit too low
    search_news("test", limit=0)
    assert mock_client.search.call_args[0][1]["per_page"] == 1

    # Test limit too high
    search_news("test", limit=200)
    assert mock_client.search.call_args[0][1]["per_page"] == 100

    # Test valid limit
    search_news("test", limit=50)
    assert mock_client.search.call_args[0][1]["per_page"] == 50


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_sort_newest(mock_client, mock_typesense_search_response):
    """Test sorting by newest first."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    search_news("test", sort="newest")

    call_args = mock_client.search.call_args[0][1]
    assert call_args["sort_by"] == "published_at:desc"


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_sort_oldest(mock_client, mock_typesense_search_response):
    """Test sorting by oldest first."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    search_news("test", sort="oldest")

    call_args = mock_client.search.call_args[0][1]
    assert call_args["sort_by"] == "published_at:asc"


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_sort_relevant(mock_client, mock_typesense_search_response):
    """Test default sorting (relevant)."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    search_news("test", sort="relevant")

    call_args = mock_client.search.call_args[0][1]
    # Relevant uses default ranking, so no sort_by param
    assert "sort_by" not in call_args


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_multiple_filters(mock_client, mock_typesense_search_response):
    """Test search with multiple filters combined."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = mock_typesense_search_response

    result = search_news(
        "educação",
        agencies=["Ministério da Educação", "MEC"],
        year_from=2023,
        themes=["Educação e Cultura"],
        limit=20,
        sort="newest",
    )

    call_args = mock_client.search.call_args[0][1]

    # All filters should be present
    assert "filter_by" in call_args
    filter_str = call_args["filter_by"]
    assert "agency:=" in filter_str
    assert "published_year:>=2023" in filter_str
    assert "theme_1_level_1:=" in filter_str

    # Other params
    assert call_args["per_page"] == 20
    assert call_args["sort_by"] == "published_at:desc"


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_error_handling(mock_client):
    """Test error handling when search fails."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.side_effect = TypesenseClientError("Connection failed")

    result = search_news("test")

    # Should return error message, not raise exception
    assert "Erro ao buscar notícias" in result
    assert "Typesense" in result


@patch("govbrnews_mcp.tools.search.typesense_client")
def test_search_news_empty_results(mock_client):
    """Test search with no results."""
    from govbrnews_mcp.tools.search import search_news

    mock_client.search.return_value = {"found": 0, "hits": []}

    result = search_news("xyzabc123nonexistent")

    assert "0 notícias" in result
    assert "Nenhuma notícia encontrada" in result
