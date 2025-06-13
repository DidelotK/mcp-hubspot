"""MCP tool for searching HubSpot deals using the CRM Search API."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class SearchDealsTool(BaseTool):
    """Tool for searching HubSpot deals with advanced filtering."""

    def get_tool_definition(self) -> types.Tool:
        """Return the search deals tool definition."""
        return types.Tool(
            name="search_hubspot_deals",
            description="Search HubSpot deals using the CRM Search API with advanced filtering",
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
                    "filters": {
                        "type": "object",
                        "description": "Search filters object",
                        "properties": {
                            "dealname": {
                                "type": "string",
                                "description": "Partial match on deal name (contains token)",
                            },
                            "owner_id": {
                                "type": "string",
                                "description": "Exact match on HubSpot owner ID",
                            },
                            "dealstage": {
                                "type": "string",
                                "description": "Exact match on deal stage",
                            },
                            "pipeline": {
                                "type": "string",
                                "description": "Exact match on pipeline ID",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deals search."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            # Use cached client call instead of direct client call
            deals = await self._cached_client_call(
                "search_deals", limit=limit, filters=filters
            )
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
