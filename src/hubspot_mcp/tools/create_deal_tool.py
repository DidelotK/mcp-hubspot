"""MCP tool to create HubSpot deals."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class CreateDealTool(BaseTool):
    """Tool to create HubSpot deals."""

    def get_tool_definition(self) -> types.Tool:
        """Return the create deal tool definition."""
        return types.Tool(
            name="create_deal",
            description="Creates a new deal in HubSpot",
            inputSchema={
                "type": "object",
                "properties": {
                    "dealname": {
                        "type": "string",
                        "description": "Name of the deal (required)",
                        "minLength": 1,
                    },
                    "amount": {
                        "type": "string",
                        "description": "Deal amount",
                    },
                    "dealstage": {
                        "type": "string",
                        "description": "Deal stage (e.g., 'appointmentscheduled', 'qualifiedtobuy', 'presentationscheduled', 'decisionmakerboughtin', 'contractsent', 'closedwon', 'closedlost')",
                    },
                    "pipeline": {
                        "type": "string",
                        "description": "Deal pipeline",
                    },
                    "closedate": {
                        "type": "string",
                        "description": "Expected close date (format: YYYY-MM-DD)",
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
                "required": ["dealname"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deal creation."""
        try:
            # Validate required arguments
            if not arguments.get("dealname"):
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Validation Error**\n\nDeal name (dealname) is required.",
                    )
                ]

            # Prepare deal data
            deal_data = {
                "dealname": arguments["dealname"],
            }

            # Add optional fields if provided
            optional_fields = [
                "amount",
                "dealstage",
                "pipeline",
                "closedate",
                "hubspot_owner_id",
                "description",
            ]

            for field in optional_fields:
                if field in arguments and arguments[field]:
                    deal_data[field] = arguments[field]

            # Create the deal
            created_deal = await self.client.create_deal(deal_data)

            # Format success response
            result_text = "✅ **Deal created successfully!**\n\n"
            result_text += f"**{deal_data['dealname']}**\n"
            result_text += f"🆔 ID: {created_deal.get('id')}\n"

            # Display created properties
            properties = created_deal.get("properties", {})
            if properties.get("amount"):
                try:
                    amount_float = float(properties["amount"])
                    amount_formatted = f"${amount_float:,.2f}"
                except (ValueError, TypeError):
                    amount_formatted = f"${properties['amount']}"
                result_text += f"💰 Amount: {amount_formatted}\n"

            if properties.get("dealstage"):
                result_text += f"📊 Stage: {properties['dealstage']}\n"

            if properties.get("pipeline"):
                result_text += f"🔄 Pipeline: {properties['pipeline']}\n"

            if properties.get("closedate"):
                result_text += f"📅 Close date: {properties['closedate']}\n"

            if properties.get("createdate"):
                result_text += f"📅 Created: {properties['createdate']}\n"

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            return self.handle_error(e)
