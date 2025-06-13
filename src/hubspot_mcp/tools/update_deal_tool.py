"""MCP tool to update HubSpot deals."""

from typing import Any, Dict, List, Optional

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class UpdateDealTool(BaseTool):
    """Tool to update HubSpot deals."""

    def get_tool_definition(self) -> types.Tool:
        """Return the update deal tool definition.

        Returns:
            types.Tool: The tool definition for updating deals
        """
        return types.Tool(
            name="update_deal",
            description="Updates an existing deal in HubSpot",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_id": {
                        "type": "string",
                        "description": "ID of the deal to update",
                    },
                    "properties": {
                        "type": "object",
                        "description": "Properties to update",
                        "properties": {
                            "dealname": {
                                "type": "string",
                                "description": "Name of the deal",
                            },
                            "amount": {
                                "type": "string",
                                "description": "Deal amount",
                            },
                            "dealstage": {
                                "type": "string",
                                "description": "Deal stage",
                            },
                            "pipeline": {
                                "type": "string",
                                "description": "Deal pipeline",
                            },
                            "closedate": {
                                "type": "string",
                                "description": "Expected close date (YYYY-MM-DD)",
                            },
                            "hubspot_owner_id": {
                                "type": "string",
                                "description": "Deal owner ID",
                            },
                            "description": {
                                "type": "string",
                                "description": "Deal description",
                            },
                        },
                        "additionalProperties": True,
                    },
                },
                "required": ["deal_id", "properties"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deal update.

        Args:
            arguments: Dictionary containing deal_id and properties to update

        Returns:
            List[types.TextContent]: List containing the formatted result or error message
        """
        try:
            deal_id: Optional[str] = arguments.get("deal_id")
            properties: Dict[str, Any] = arguments.get("properties", {})

            if not deal_id:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ Error: deal_id is required for updating a deal",
                    )
                ]

            if not properties:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ Error: properties object is required for updating a deal",
                    )
                ]

            updated_deal = await self.client.update_deal(
                deal_id=deal_id, properties=properties
            )
            formatted_result = HubSpotFormatter.format_deal(updated_deal)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
