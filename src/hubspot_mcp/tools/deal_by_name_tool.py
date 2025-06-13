"""MCP tool to retrieve a specific HubSpot deal by name."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealByNameTool(BaseTool):
    """Tool to retrieve a specific HubSpot deal by name."""

    def get_tool_definition(self) -> types.Tool:
        """Return the deal by name tool definition."""
        return types.Tool(
            name="get_deal_by_name",
            description="Retrieves a specific HubSpot deal by its exact name",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {
                        "type": "string",
                        "description": "The exact name of the deal to search for",
                    }
                },
                "required": ["deal_name"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deal by name retrieval."""
        try:
            deal_name = arguments.get("deal_name")
            if not deal_name:
                return [
                    types.TextContent(type="text", text="Error: Deal name is required")
                ]

            # Use cached client call instead of direct client call
            deal = await self._cached_client_call(
                "get_deal_by_name", deal_name=deal_name
            )

            formatted_result = HubSpotFormatter.format_single_deal(deal)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
