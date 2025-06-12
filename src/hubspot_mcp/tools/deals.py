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
            description="Lists HubSpot deals with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deals to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters for search",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Search term to filter deals",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deals retrieval."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            deals = await self.client.get_deals(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
