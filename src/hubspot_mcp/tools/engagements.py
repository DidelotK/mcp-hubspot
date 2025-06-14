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
            description="Lists HubSpot engagements with pagination support",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of engagements to return (default: 100, max: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "after": {
                        "type": "string",
                        "description": "Pagination cursor to get the next set of results",
                    },
                    "properties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of additional engagement properties to include in the response",
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
            after = arguments.get("after")
            extra_props = arguments.get("properties")

            kwargs = {"limit": limit, "after": after}
            if extra_props:
                kwargs["extra_properties"] = extra_props

            engagements = await self._cached_client_call("get_engagements", **kwargs)
            formatted_result = HubSpotFormatter.format_engagements(engagements)

            return [types.TextContent(type="text", text=formatted_result)]
        except Exception as exc:  # pragma: no cover
            return self.handle_error(exc)
