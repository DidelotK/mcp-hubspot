"""HubSpot MCP configuration settings."""

import os
from typing import Any, Dict, List, Optional


class Settings:
    """Centralized configuration class for HubSpot MCP server.

    This class manages all configuration settings for the HubSpot MCP server,
    loading them from environment variables with appropriate defaults.
    """

    def __init__(self):
        """Initialize the configuration from environment variables."""
        # HubSpot API Configuration
        self.hubspot_api_key: Optional[str] = os.getenv("HUBSPOT_API_KEY")
        self.hubspot_base_url: str = os.getenv(
            "HUBSPOT_BASE_URL", "https://api.hubapi.com"
        )

        # MCP Server Configuration
        self.mcp_auth_key: Optional[str] = os.getenv("MCP_AUTH_KEY")
        self.mcp_auth_header: str = os.getenv("MCP_AUTH_HEADER", "X-API-Key")

        # Server Configuration
        self.server_name: str = os.getenv("MCP_SERVER_NAME", "hubspot-mcp-server")
        self.server_version: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
        self.host: str = os.getenv("HOST", "localhost")
        self.port: int = int(os.getenv("PORT", "8080"))
        self.mode: str = os.getenv("MODE", "stdio")

        # Security Configuration
        self.faiss_data_secure: bool = self._get_bool_env("FAISS_DATA_SECURE", True)
        self.data_protection_disabled: bool = self._get_bool_env(
            "DATA_PROTECTION_DISABLED", False
        )

        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable.

        Args:
            key: Environment variable key
            default: Default value if not set

        Returns:
            Boolean value from environment variable
        """
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def validate(self) -> bool:
        """Validate that all required settings are configured."""
        return self.hubspot_api_key is not None

    def get_missing_config(self) -> List[str]:
        """Return the list of missing required configurations.

        Returns:
            List[str]: List of missing configuration items
        """
        missing: List[str] = []
        if not self.hubspot_api_key:
            missing.append("HUBSPOT_API_KEY environment variable")
        return missing

    def is_authentication_enabled(self) -> bool:
        """Check if MCP server authentication is enabled."""
        return self.mcp_auth_key is not None

    def get_hubspot_config(self) -> Dict[str, Any]:
        """Get HubSpot-specific configuration."""
        return {
            "api_key": self.hubspot_api_key,
            "base_url": self.hubspot_base_url,
        }

    def get_server_config(self) -> Dict[str, Any]:
        """Get server-specific configuration."""
        return {
            "name": self.server_name,
            "version": self.server_version,
            "host": self.host,
            "port": self.port,
            "mode": self.mode,
        }

    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication-specific configuration."""
        return {
            "enabled": self.is_authentication_enabled(),
            "auth_key": self.mcp_auth_key,
            "auth_header": self.mcp_auth_header,
            "faiss_data_secure": self.faiss_data_secure,
        }


# Global settings instance
settings = Settings()


# Backward compatibility - deprecated, use settings directly
class HubSpotConfig:
    """Legacy HubSpot configuration class for backward compatibility."""

    def __init__(self):
        """Initialize configuration from global settings."""
        self.api_key: Optional[str] = settings.hubspot_api_key
        self.base_url: str = settings.hubspot_base_url

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        return settings.validate()

    def get_missing_config(self) -> List[str]:
        """Return the list of missing configurations."""
        return settings.get_missing_config()
