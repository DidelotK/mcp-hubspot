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
            description="Lists HubSpot companies with pagination support",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of companies to return (default: 100, max: 100)",
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
        """Execute companies retrieval."""
        try:
            limit = arguments.get("limit", 100)
            after = arguments.get("after")

            companies = await self.client.get_companies(limit=limit, after=after)
            formatted_result = HubSpotFormatter.format_companies(companies)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
