"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from hubspot_mcp.config.settings import HubSpotConfig, Settings, settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_default_values(self) -> None:
        """Test settings with default values when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()

            # HubSpot API Configuration
            assert test_settings.hubspot_api_key is None
            assert test_settings.hubspot_base_url == "https://api.hubapi.com"

            # MCP Server Configuration
            assert test_settings.mcp_auth_key is None
            assert test_settings.mcp_auth_header == "X-API-Key"

            # Server Configuration
            assert test_settings.server_name == "hubspot-mcp-server"
            assert test_settings.server_version == "1.0.0"
            assert test_settings.host == "localhost"
            assert test_settings.port == 8080
            assert test_settings.mode == "stdio"

            # Security Configuration
            assert test_settings.faiss_data_secure is True

            # Logging Configuration
            assert test_settings.log_level == "INFO"

    def test_settings_with_environment_variables(self) -> None:
        """Test settings with all environment variables set."""
        test_env = {
            "HUBSPOT_API_KEY": "test_api_key",
            "HUBSPOT_BASE_URL": "https://custom.hubapi.com",
            "MCP_AUTH_KEY": "test_auth_key",
            "MCP_AUTH_HEADER": "X-Custom-Key",
            "MCP_SERVER_NAME": "custom-server",
            "MCP_SERVER_VERSION": "2.0.0",
            "HOST": "0.0.0.0",
            "PORT": "9000",
            "MODE": "sse",
            "FAISS_DATA_SECURE": "false",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, test_env, clear=True):
            test_settings = Settings()

            # HubSpot API Configuration
            assert test_settings.hubspot_api_key == "test_api_key"
            assert test_settings.hubspot_base_url == "https://custom.hubapi.com"

            # MCP Server Configuration
            assert test_settings.mcp_auth_key == "test_auth_key"
            assert test_settings.mcp_auth_header == "X-Custom-Key"

            # Server Configuration
            assert test_settings.server_name == "custom-server"
            assert test_settings.server_version == "2.0.0"
            assert test_settings.host == "0.0.0.0"
            assert test_settings.port == 9000
            assert test_settings.mode == "sse"

            # Security Configuration
            assert test_settings.faiss_data_secure is False

            # Logging Configuration
            assert test_settings.log_level == "DEBUG"

    def test_bool_env_parsing(self) -> None:
        """Test boolean environment variable parsing."""
        test_settings = Settings()

        # Test true values
        assert test_settings._get_bool_env("TEST_TRUE", False) is False  # not set

        true_values = ["true", "1", "yes", "on", "TRUE", "Yes", "ON"]
        for value in true_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                assert test_settings._get_bool_env("TEST_BOOL", False) is True

        # Test false values
        false_values = [
            "false",
            "0",
            "no",
            "off",
            "FALSE",
            "No",
            "OFF",
            "anything_else",
        ]
        for value in false_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                assert test_settings._get_bool_env("TEST_BOOL", True) is False

    def test_validate_method(self) -> None:
        """Test configuration validation."""
        # Test with API key
        with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}, clear=True):
            test_settings = Settings()
            assert test_settings.validate() is True
            assert test_settings.get_missing_config() == []

        # Test without API key
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            assert test_settings.validate() is False
            missing = test_settings.get_missing_config()
            assert "HUBSPOT_API_KEY environment variable" in missing

    def test_is_authentication_enabled(self) -> None:
        """Test authentication status checking."""
        # Test with auth key
        with patch.dict(os.environ, {"MCP_AUTH_KEY": "test_auth"}, clear=True):
            test_settings = Settings()
            assert test_settings.is_authentication_enabled() is True

        # Test without auth key
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            assert test_settings.is_authentication_enabled() is False

    def test_get_hubspot_config(self) -> None:
        """Test HubSpot configuration getter."""
        with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}, clear=True):
            test_settings = Settings()
            config = test_settings.get_hubspot_config()

            assert config["api_key"] == "test_key"
            assert config["base_url"] == "https://api.hubapi.com"

    def test_get_server_config(self) -> None:
        """Test server configuration getter."""
        test_env = {
            "MCP_SERVER_NAME": "test-server",
            "MCP_SERVER_VERSION": "1.5.0",
            "HOST": "0.0.0.0",
            "PORT": "9000",
            "MODE": "sse",
        }

        with patch.dict(os.environ, test_env, clear=True):
            test_settings = Settings()
            config = test_settings.get_server_config()

            assert config["name"] == "test-server"
            assert config["version"] == "1.5.0"
            assert config["host"] == "0.0.0.0"
            assert config["port"] == 9000
            assert config["mode"] == "sse"

    def test_get_auth_config(self) -> None:
        """Test authentication configuration getter."""
        # Test with auth enabled
        test_env = {
            "MCP_AUTH_KEY": "test_auth_key",
            "MCP_AUTH_HEADER": "X-Test-Key",
        }

        with patch.dict(os.environ, test_env, clear=True):
            test_settings = Settings()
            config = test_settings.get_auth_config()

            assert config["auth_key"] == "test_auth_key"
            assert config["auth_header"] == "X-Test-Key"
            assert config["enabled"] is True

        # Test with auth disabled
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            config = test_settings.get_auth_config()

            assert config["auth_key"] is None
            assert config["auth_header"] == "X-API-Key"
            assert config["enabled"] is False

    def test_global_settings_instance(self) -> None:
        """Test that global settings instance works correctly."""
        # The global settings instance should be available
        assert settings is not None
        assert isinstance(settings, Settings)

        # Test that it has the expected attributes
        assert hasattr(settings, "hubspot_api_key")
        assert hasattr(settings, "validate")
        assert hasattr(settings, "get_hubspot_config")

    def test_port_type_conversion(self) -> None:
        """Test that PORT environment variable is properly converted to int."""
        with patch.dict(os.environ, {"PORT": "3000"}, clear=True):
            test_settings = Settings()
            assert test_settings.port == 3000
            assert isinstance(test_settings.port, int)

        # Test with invalid port (should raise ValueError)
        with patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                Settings()


class TestHubSpotConfig:
    """Test HubSpot configuration (backward compatibility)."""

    def test_backward_compatibility_with_settings(self) -> None:
        """Test that HubSpotConfig uses the global settings instance."""
        with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key_123"}, clear=True):
            # Create new settings instance to pick up environment
            from hubspot_mcp.config.settings import Settings

            test_settings = Settings()

            # Mock the global settings
            with patch("hubspot_mcp.config.settings.settings", test_settings):
                config = HubSpotConfig()
                assert config.api_key == "test_key_123"
                assert config.validate() is True

    def test_config_with_api_key(self) -> None:
        """Test configuration with API key."""
        with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}, clear=True):
            # Create new settings instance to pick up environment
            from hubspot_mcp.config.settings import Settings

            test_settings = Settings()

            # Mock the global settings
            with patch("hubspot_mcp.config.settings.settings", test_settings):
                config = HubSpotConfig()
                assert config.api_key == "test_key"
                assert config.validate() is True
                assert config.get_missing_config() == []

    def test_config_without_api_key(self) -> None:
        """Test configuration without API key."""
        with patch.dict(os.environ, {}, clear=True):
            # Create new settings instance to pick up environment
            from hubspot_mcp.config.settings import Settings

            test_settings = Settings()

            # Mock the global settings
            with patch("hubspot_mcp.config.settings.settings", test_settings):
                config = HubSpotConfig()
                assert config.api_key is None
                assert config.validate() is False
                assert (
                    "HUBSPOT_API_KEY environment variable"
                    in config.get_missing_config()
                )

    def test_base_url(self) -> None:
        """Test base URL configuration."""
        with patch.dict(os.environ, {}, clear=True):
            # Create new settings instance to pick up environment
            from hubspot_mcp.config.settings import Settings

            test_settings = Settings()

            # Mock the global settings
            with patch("hubspot_mcp.config.settings.settings", test_settings):
                config = HubSpotConfig()
                assert config.base_url == "https://api.hubapi.com"
