"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from hubspot_mcp.config.settings import HubSpotConfig


class TestHubSpotConfig:
    """Test HubSpot configuration."""

    def test_config_with_api_key(self) -> None:
        """Test configuration with API key.

        Vérifie que la configuration fonctionne correctement lorsque la variable d'environnement HUBSPOT_API_KEY est définie.
        """
        with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}):
            config = HubSpotConfig()
            assert config.api_key == "test_key"
            assert config.validate() is True
            assert config.get_missing_config() == []

    def test_config_without_api_key(self) -> None:
        """Test configuration without API key.

        Vérifie que la configuration détecte l'absence de la variable d'environnement HUBSPOT_API_KEY.
        """
        with patch.dict(os.environ, {}, clear=True):
            config = HubSpotConfig()
            assert config.api_key is None
            assert config.validate() is False
            assert "HUBSPOT_API_KEY environment variable" in config.get_missing_config()

    def test_base_url(self) -> None:
        """Test base URL configuration.

        Vérifie que l'URL de base est correctement définie.
        """
        config = HubSpotConfig()
        assert config.base_url == "https://api.hubapi.com"
