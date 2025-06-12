"""MCP tool to manage HubSpot contacts."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class ContactsTool(BaseTool):
    """Tool to list HubSpot contacts."""

    def get_tool_definition(self) -> types.Tool:
        """Return the contacts tool definition."""
        return types.Tool(
            name="list_hubspot_contacts",
            description="Lists HubSpot contacts with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of contacts to return (default: 100)",
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
                                "description": "Search term to filter contacts",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute contacts retrieval."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            contacts = await self.client.get_contacts(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_contacts(contacts)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
