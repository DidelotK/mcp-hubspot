"""HubSpot MCP configuration settings."""

import os
from typing import List, Optional


class HubSpotConfig:
    """Configuration class for HubSpot MCP server.

    This class manages the configuration settings for the HubSpot MCP server,
    including API keys and base URLs.
    """

    def __init__(self):
        """Initialize the HubSpot configuration.

        The configuration is loaded from environment variables.
        """
        self.api_key: Optional[str] = os.getenv("HUBSPOT_API_KEY")
        self.base_url: str = "https://api.hubapi.com"

    def validate(self) -> bool:
        """Validates that all required configuration is present.

        Returns:
            bool: True if all required configuration is present, False otherwise
        """
        return self.api_key is not None

    def get_missing_config(self) -> List[str]:
        """Returns the list of missing configurations.

        Returns:
            List[str]: List of missing configuration items
        """
        missing: List[str] = []
        if not self.api_key:
            missing.append("HUBSPOT_API_KEY environment variable")
        return missing
