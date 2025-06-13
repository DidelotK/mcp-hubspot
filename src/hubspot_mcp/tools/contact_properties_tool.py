"""MCP tool to retrieve HubSpot contact properties."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class ContactPropertiesTool(BaseTool):
    """Tool to retrieve HubSpot contact properties."""

    def get_tool_definition(self) -> types.Tool:
        """Return the contact properties tool definition."""
        return types.Tool(
            name="get_hubspot_contact_properties",
            description="Retrieves the list of available properties for HubSpot contacts",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute contact properties retrieval."""
        try:
            # Use cached client call instead of direct client call
            properties = await self._cached_client_call("get_contact_properties")
            formatted_result = HubSpotFormatter.format_contact_properties(properties)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
