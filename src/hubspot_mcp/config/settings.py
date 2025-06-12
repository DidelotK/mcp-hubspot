"""Configuration du serveur MCP HubSpot."""

import os
from typing import Optional


class Settings:
    """Configuration du serveur MCP HubSpot."""

    def __init__(self):
        self.hubspot_api_key: Optional[str] = os.getenv("HUBSPOT_API_KEY")
        self.server_name: str = "hubspot-mcp-server"
        self.server_version: str = "1.0.0"
        self.default_limit: int = 100
        self.max_limit: int = 1000
        self.hubspot_base_url: str = "https://api.hubapi.com"

    def validate(self) -> bool:
        """Valide la configuration."""
        if not self.hubspot_api_key:
            return False
        return True

    def get_missing_config(self) -> list[str]:
        """Retourne la liste des configurations manquantes."""
        missing = []
        if not self.hubspot_api_key:
            missing.append("HUBSPOT_API_KEY")
        return missing
