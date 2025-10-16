"""Tests for Typesense client wrapper."""

import pytest
from unittest.mock import MagicMock, patch
from typesense.exceptions import ObjectNotFound, TypesenseClientError


@patch("govbrnews_mcp.typesense_client.settings")
@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_typesense_client_initialization(mock_client_class, mock_settings_patch):
    """Test TypesenseClient initialization."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Configure mock settings
    mock_settings_patch.typesense_host = "localhost"
    mock_settings_patch.typesense_port = 8108
    mock_settings_patch.typesense_protocol = "http"
    mock_settings_patch.typesense_api_key = "test_api_key"

    client = TypesenseClient()

    # Verify client was initialized with correct config
    mock_client_class.assert_called_once()
    call_args = mock_client_class.call_args[0][0]

    assert call_args["nodes"][0]["host"] == "localhost"
    assert call_args["nodes"][0]["port"] == "8108"
    assert call_args["nodes"][0]["protocol"] == "http"
    assert call_args["api_key"] == "test_api_key"


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_search_success(mock_client_class, mock_typesense_search_response, mock_settings):
    """Test successful search operation."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.collections.__getitem__.return_value.documents.search.return_value = (
        mock_typesense_search_response
    )

    client = TypesenseClient()
    results = client.search("news", {"q": "educação", "query_by": "title"})

    assert results["found"] == 3
    assert len(results["hits"]) == 3
    assert results["hits"][0]["document"]["title"] == "Notícia sobre educação"


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_search_collection_not_found(mock_client_class, mock_settings):
    """Test search with non-existent collection."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock to raise ObjectNotFound
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.collections.__getitem__.return_value.documents.search.side_effect = (
        ObjectNotFound("Collection not found")
    )

    client = TypesenseClient()

    with pytest.raises(ObjectNotFound):
        client.search("nonexistent", {"q": "test"})


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_get_collection_info_success(
    mock_client_class, mock_typesense_collection_info, mock_settings
):
    """Test successful collection info retrieval."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.collections.__getitem__.return_value.retrieve.return_value = (
        mock_typesense_collection_info
    )

    client = TypesenseClient()
    info = client.get_collection_info("news")

    assert info["name"] == "news"
    assert info["num_documents"] == 295511
    assert len(info["fields"]) == 5


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_get_document_success(mock_client_class, mock_settings):
    """Test successful document retrieval."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_doc = {
        "unique_id": "test123",
        "title": "Test Document",
        "agency": "Test Agency",
    }
    mock_instance.collections.__getitem__.return_value.documents.__getitem__.return_value.retrieve.return_value = mock_doc

    client = TypesenseClient()
    doc = client.get_document("news", "test123")

    assert doc["unique_id"] == "test123"
    assert doc["title"] == "Test Document"


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_get_document_not_found(mock_client_class, mock_settings):
    """Test document retrieval for non-existent document."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.collections.__getitem__.return_value.documents.__getitem__.return_value.retrieve.side_effect = ObjectNotFound(
        "Document not found"
    )

    client = TypesenseClient()

    with pytest.raises(ObjectNotFound):
        client.get_document("news", "nonexistent")


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_health_check_success(mock_client_class, mock_settings):
    """Test successful health check."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.operations.health.return_value = {"ok": True}

    client = TypesenseClient()
    is_healthy = client.health_check()

    assert is_healthy is True


@patch("govbrnews_mcp.typesense_client.typesense.Client")
def test_health_check_failure(mock_client_class, mock_settings):
    """Test failed health check."""
    from govbrnews_mcp.typesense_client import TypesenseClient

    # Setup mock
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.operations.health.side_effect = Exception("Connection refused")

    client = TypesenseClient()
    is_healthy = client.health_check()

    assert is_healthy is False
