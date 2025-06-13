"""MCP tool to search HubSpot contacts using CRM Search API."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class SearchContactsTool(BaseTool):
    """Tool for advanced contact search."""

    def get_tool_definition(self) -> types.Tool:  # noqa: D401
        """Return the tool definition."""
        return types.Tool(
            name="search_hubspot_contacts",
            description="Advanced search for contacts via HubSpot CRM Search API",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of contacts to return (default: 100, max: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Search filters object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Partial match on email (contains token)",
                            },
                            "firstname": {
                                "type": "string",
                                "description": "Partial match on first name",
                            },
                            "lastname": {
                                "type": "string",
                                "description": "Partial match on last name",
                            },
                            "company": {
                                "type": "string",
                                "description": "Partial match on company name",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:  # noqa: D401
        """Execute contact search."""
        try:
            limit: int = arguments.get("limit", 100)
            filters: Dict[str, Any] = arguments.get("filters", {})

            contacts = await self._cached_client_call(
                "search_contacts", limit=limit, filters=filters
            )
            formatted = HubSpotFormatter.format_contacts(contacts)
            return [types.TextContent(type="text", text=formatted)]
        except Exception as exc:  # pragma: no cover
            return self.handle_error(exc)
