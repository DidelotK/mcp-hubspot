"""Base class for HubSpot MCP tools."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import httpx
import mcp.types as types

from ..client import HubSpotClient

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all HubSpot tools.

    This abstract base class defines the interface that all HubSpot tools must implement.
    It provides common functionality for error handling and client management.
    """

    def __init__(self, client: HubSpotClient):
        """Initialize the tool with a HubSpot client.

        Args:
            client: The HubSpot client instance to use for API calls
        """
        self.client = client

    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition for MCP.

        Returns:
            types.Tool: The tool definition containing name, description, and input schema
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute the tool with provided arguments.

        Args:
            arguments: Dictionary containing the tool's input parameters

        Returns:
            List[types.TextContent]: List of text content items representing the tool's output
        """
        pass

    def handle_error(self, error: Exception) -> List[types.TextContent]:
        """Handle errors in a unified way.

        Args:
            error: The exception that occurred during tool execution

        Returns:
            List[types.TextContent]: List containing a single text content item with the error message
        """
        if isinstance(error, httpx.HTTPStatusError):
            error_msg = f"HubSpot API Error ({error.response.status_code}): {error.response.text}"
        else:
            error_msg = f"Unexpected error: {str(error)}"

        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
