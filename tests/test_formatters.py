"""Tests for formatting utilities."""

import pytest
from govbrnews_mcp.utils.formatters import (
    format_timestamp,
    format_search_results,
    format_facets_results,
    format_document_full,
)


def test_format_timestamp():
    """Test timestamp formatting."""
    # Valid timestamp (2024-01-01)
    assert format_timestamp(1704067200) == "01/01/2024"

    # None
    assert format_timestamp(None) == "N/A"

    # Zero
    assert format_timestamp(0) == "N/A"

    # Negative
    assert format_timestamp(-1) == "N/A"


def test_format_search_results_with_hits(mock_typesense_search_response):
    """Test formatting search results with hits."""
    result = format_search_results(mock_typesense_search_response)

    assert "# Resultados da Busca" in result
    assert "**Total encontrado:** 3 notícias" in result
    assert "**Mostrando:** 3 resultados" in result
    assert "Notícia sobre educação" in result
    assert "Ministério da Educação" in result
    assert "https://example.gov.br/noticia1" in result


def test_format_search_results_empty():
    """Test formatting empty search results."""
    empty_results = {"found": 0, "hits": []}

    result = format_search_results(empty_results)

    assert "# Resultados da Busca" in result
    assert "**Total encontrado:** 0 notícias" in result
    assert "Nenhuma notícia encontrada" in result


def test_format_search_results_content_truncation():
    """Test that long content is truncated."""
    long_content = "A" * 600  # Content longer than 500 chars

    results = {
        "found": 1,
        "hits": [
            {
                "document": {
                    "title": "Test",
                    "content": long_content,
                }
            }
        ],
    }

    result = format_search_results(results)

    # Should be truncated with ellipsis
    assert "..." in result
    assert len(result) < len(long_content) + 200  # Some overhead for formatting


def test_format_facets_results(mock_typesense_facets_response):
    """Test formatting faceted results."""
    result = format_facets_results(mock_typesense_facets_response)

    assert "# Agregações" in result
    assert "## Agências" in result  # Translated field name
    assert "Ministério da Educação" in result
    assert "5,432" in result  # Formatted number
    assert "| Item | Quantidade |" in result  # Table header


def test_format_facets_results_empty():
    """Test formatting empty facets."""
    empty_results = {"facet_counts": []}

    result = format_facets_results(empty_results)

    assert "Nenhuma agregação disponível" in result


def test_format_document_full():
    """Test formatting full document."""
    document = {
        "unique_id": "test123",
        "title": "Título da Notícia",
        "agency": "Ministério da Educação",
        "published_at": 1704067200,
        "category": "Educação",
        "theme_1_level_1": "Educação e Cultura",
        "url": "https://example.gov.br/test",
        "content": "Este é o conteúdo completo da notícia...",
    }

    result = format_document_full(document)

    assert "# Título da Notícia" in result
    assert "## Metadados" in result
    assert "**ID:** test123" in result
    assert "**Agência:** Ministério da Educação" in result
    assert "01/01/2024" in result
    assert "## Conteúdo" in result
    assert "Este é o conteúdo completo" in result


def test_format_document_minimal():
    """Test formatting document with minimal fields."""
    document = {"title": "Título Mínimo"}

    result = format_document_full(document)

    assert "# Título Mínimo" in result
    assert "## Metadados" in result
