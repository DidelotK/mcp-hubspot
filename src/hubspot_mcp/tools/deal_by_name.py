"""MCP tool to retrieve a HubSpot transaction by name."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class TransactionByNameTool(BaseTool):
    """Tool to retrieve a HubSpot transaction by name."""

    def get_tool_definition(self) -> types.Tool:
        """Return the transaction by name tool definition."""
        return types.Tool(
            name="get_transaction_by_name",
            description="Retrieves a specific HubSpot transaction by its name",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {
                        "type": "string",
                        "description": "Exact name of the transaction to search for",
                        "minLength": 1,
                    }
                },
                "required": ["deal_name"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute transaction retrieval by name."""
        try:
            deal_name = arguments.get("deal_name")

            if not deal_name:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Error**: Transaction name is required.",
                    )
                ]

            deal = await self.client.get_transaction_by_name(deal_name)
            formatted_result = HubSpotFormatter.format_single_deal(deal)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
