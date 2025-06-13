"""MCP tool for searching HubSpot deals using the CRM search API."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class SearchDealsTool(BaseTool):
    """Tool for searching HubSpot deals with advanced filters."""

    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition for MCP."""
        return types.Tool(
            name="search_hubspot_deals",
            description="Searches HubSpot deals using advanced filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deals to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filters to apply to the deal search.",
                        "properties": {
                            "dealname": {
                                "type": "string",
                                "description": "Partial deal name to search (contains token)",
                            },
                            "owner_id": {
                                "type": "string",
                                "description": "Exact HubSpot owner ID",
                            },
                            "dealstage": {
                                "type": "string",
                                "description": "Exact deal stage",
                            },
                            "pipeline": {
                                "type": "string",
                                "description": "Exact pipeline ID",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute the search and return formatted deals."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            deals = await self.client.search_deals(limit=limit, filters=filters)
            formatted = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted)]

        except Exception as error:  # noqa: BLE001
            return self.handle_error(error)
