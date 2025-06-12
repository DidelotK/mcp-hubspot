"""HubSpot MCP configuration settings."""

import os
from typing import List


class HubSpotConfig:
    """Configuration class for HubSpot MCP server."""

    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY")
        self.base_url = "https://api.hubapi.com"

    def validate(self) -> bool:
        """Validates that all required configuration is present."""
        return self.api_key is not None

    def get_missing_config(self) -> List[str]:
        """Returns the list of missing configurations."""
        missing = []
        if not self.api_key:
            missing.append("HUBSPOT_API_KEY environment variable")
        return missing
