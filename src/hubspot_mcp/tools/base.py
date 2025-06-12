"""Base class for HubSpot MCP tools."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import httpx
import mcp.types as types

from ..client import HubSpotClient

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all HubSpot tools."""

    def __init__(self, client: HubSpotClient):
        self.client = client

    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition for MCP."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute the tool with provided arguments."""
        pass

    def handle_error(self, error: Exception) -> List[types.TextContent]:
        """Handle errors in a unified way."""
        if isinstance(error, httpx.HTTPStatusError):
            error_msg = f"HubSpot API Error ({error.response.status_code}): {error.response.text}"
        else:
            error_msg = f"Unexpected error: {str(error)}"

        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
