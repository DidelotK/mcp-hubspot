"""MCP tool to manage HubSpot deals."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealsTool(BaseTool):
    """Tool to list HubSpot deals."""

    def get_tool_definition(self) -> types.Tool:
        """Return the deals tool definition."""
        return types.Tool(
            name="list_hubspot_deals",
            description="Lists HubSpot deals with pagination support",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deals to return (default: 100, max: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "after": {
                        "type": "string",
                        "description": "Pagination cursor to get the next set of results",
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deals retrieval."""
        try:
            limit = arguments.get("limit", 100)
            after = arguments.get("after")

            deals = await self.client.get_deals(limit=limit, after=after)
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
