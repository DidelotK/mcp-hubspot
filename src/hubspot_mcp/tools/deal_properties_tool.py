"""MCP tool to retrieve HubSpot deal properties."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealPropertiesTool(BaseTool):
    """Tool to retrieve HubSpot deal properties."""

    def get_tool_definition(self) -> types.Tool:
        """Return the deal properties tool definition."""
        return types.Tool(
            name="get_hubspot_deal_properties",
            description="Retrieves the list of available properties for HubSpot deals",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deal properties retrieval."""
        try:
            # Use cached client call instead of direct client call
            properties = await self._cached_client_call("get_deal_properties")
            formatted_result = HubSpotFormatter.format_deal_properties(properties)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
