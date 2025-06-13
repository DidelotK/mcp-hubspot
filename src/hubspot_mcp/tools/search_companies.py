"""MCP tool to search HubSpot companies using CRM Search API."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class SearchCompaniesTool(BaseTool):
    """Tool for advanced company search."""

    def get_tool_definition(self) -> types.Tool:  # noqa: D401
        return types.Tool(
            name="search_hubspot_companies",
            description="Advanced search for companies via HubSpot CRM Search API",
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
                    "filters": {
                        "type": "object",
                        "description": "Search filters object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Partial match on company name",
                            },
                            "domain": {
                                "type": "string",
                                "description": "Partial match on domain",
                            },
                            "industry": {
                                "type": "string",
                                "description": "Partial match on industry",
                            },
                            "country": {
                                "type": "string",
                                "description": "Partial match on country",
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
        try:
            limit: int = arguments.get("limit", 100)
            filters: Dict[str, Any] = arguments.get("filters", {})

            companies = await self._cached_client_call(
                "search_companies", limit=limit, filters=filters
            )
            formatted = HubSpotFormatter.format_companies(companies)
            return [types.TextContent(type="text", text=formatted)]
        except Exception as exc:  # pragma: no cover
            return self.handle_error(exc)
