"""Tests for HubSpot MCP configuration."""

import os
from unittest.mock import patch

import pytest

from src.hubspot_mcp.config.settings import Settings


def test_settings_init_with_api_key():
    """Test settings initialization with API key."""
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test-api-key"}):
        settings = Settings()

        assert settings.hubspot_api_key == "test-api-key"
        assert settings.server_name == "hubspot-mcp-server"
        assert settings.server_version == "1.0.0"
        assert settings.default_limit == 100
        assert settings.max_limit == 1000
        assert settings.hubspot_base_url == "https://api.hubapi.com"


def test_settings_init_without_api_key():
    """Test settings initialization without API key."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()

        assert settings.hubspot_api_key is None
        assert settings.server_name == "hubspot-mcp-server"
        assert settings.server_version == "1.0.0"
        assert settings.default_limit == 100
        assert settings.max_limit == 1000
        assert settings.hubspot_base_url == "https://api.hubapi.com"


def test_settings_validate_with_api_key():
    """Test settings validation with API key."""
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test-api-key"}):
        settings = Settings()

        assert settings.validate() is True


def test_settings_validate_without_api_key():
    """Test settings validation without API key."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()

        assert settings.validate() is False


def test_settings_get_missing_config_with_api_key():
    """Test get_missing_config with API key."""
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test-api-key"}):
        settings = Settings()

        missing = settings.get_missing_config()
        assert missing == []


def test_settings_get_missing_config_without_api_key():
    """Test get_missing_config without API key."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()

        missing = settings.get_missing_config()
        assert missing == ["HUBSPOT_API_KEY"]


def test_settings_with_empty_api_key():
    """Test settings with empty API key."""
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": ""}):
        settings = Settings()

        assert settings.hubspot_api_key == ""
        assert settings.validate() is False
        assert settings.get_missing_config() == ["HUBSPOT_API_KEY"]
