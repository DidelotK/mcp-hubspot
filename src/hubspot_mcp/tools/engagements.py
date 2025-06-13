"""MCP tool to list HubSpot engagements."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class EngagementsTool(BaseTool):
    """Tool to list HubSpot engagements."""

    def get_tool_definition(self) -> types.Tool:  # noqa: D401
        """Return the engagements tool definition."""
        return types.Tool(
            name="list_hubspot_engagements",
            description="Lists HubSpot engagements with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of engagements to return (default: 100)",
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
                                "description": "Search term to filter engagements",
                            }
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
        """Execute engagements retrieval."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            engagements = await self.client.get_engagements(
                limit=limit, filters=filters
            )
            formatted_result = HubSpotFormatter.format_engagements(engagements)

            return [types.TextContent(type="text", text=formatted_result)]
        except Exception as exc:  # pragma: no cover
            return self.handle_error(exc)
