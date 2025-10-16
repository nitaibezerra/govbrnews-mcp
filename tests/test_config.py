"""Tests for configuration module."""

import pytest
from pydantic import ValidationError


def test_settings_defaults(monkeypatch, tmp_path):
    """Test default settings values."""
    from govbrnews_mcp.config import Settings

    # Clear all environment variables to test defaults
    monkeypatch.delenv("TYPESENSE_API_KEY", raising=False)
    monkeypatch.delenv("TYPESENSE_HOST", raising=False)
    monkeypatch.delenv("TYPESENSE_PORT", raising=False)
    monkeypatch.delenv("TYPESENSE_PROTOCOL", raising=False)
    monkeypatch.delenv("CACHE_TTL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # Change to a temporary directory without .env file
    monkeypatch.chdir(tmp_path)

    # Should fail without API key (no .env file and no env vars)
    with pytest.raises(ValidationError):
        Settings()


def test_settings_with_api_key(monkeypatch):
    """Test settings with required API key."""
    from govbrnews_mcp.config import Settings

    monkeypatch.setenv("TYPESENSE_API_KEY", "test_key")

    settings = Settings()

    assert settings.typesense_host == "localhost"
    assert settings.typesense_port == 8108
    assert settings.typesense_protocol == "http"
    assert settings.typesense_api_key == "test_key"
    assert settings.cache_ttl == 300
    assert settings.log_level == "INFO"


def test_settings_custom_values(monkeypatch):
    """Test settings with custom values."""
    from govbrnews_mcp.config import Settings

    monkeypatch.setenv("TYPESENSE_HOST", "typesense.example.com")
    monkeypatch.setenv("TYPESENSE_PORT", "8109")
    monkeypatch.setenv("TYPESENSE_PROTOCOL", "https")
    monkeypatch.setenv("TYPESENSE_API_KEY", "custom_key")
    monkeypatch.setenv("CACHE_TTL", "600")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.typesense_host == "typesense.example.com"
    assert settings.typesense_port == 8109
    assert settings.typesense_protocol == "https"
    assert settings.typesense_api_key == "custom_key"
    assert settings.cache_ttl == 600
    assert settings.log_level == "DEBUG"
