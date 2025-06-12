"""MCP tool to manage HubSpot companies."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class CompaniesTool(BaseTool):
    """Tool to list HubSpot companies."""

    def get_tool_definition(self) -> types.Tool:
        """Return the companies tool definition."""
        return types.Tool(
            name="list_hubspot_companies",
            description="Lists HubSpot companies with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of companies to return (default: 100)",
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
                                "description": "Search term to filter companies",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute companies retrieval."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            companies = await self.client.get_companies(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_companies(companies)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
