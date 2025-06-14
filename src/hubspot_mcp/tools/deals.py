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
            description="Lists HubSpot deals with pagination support",
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
                    "after": {
                        "type": "string",
                        "description": "Pagination cursor to get the next set of results",
                    },
                    "properties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of additional deal properties to include in the response",
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deals retrieval."""
        try:
            limit = arguments.get("limit", 100)
            after = arguments.get("after")
            extra_props = arguments.get("properties")

            kwargs = {"limit": limit, "after": after}
            if extra_props:
                kwargs["extra_properties"] = extra_props

            deals = await self._cached_client_call("get_deals", **kwargs)
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
