"""MCP tool to retrieve HubSpot company properties."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class CompanyPropertiesTool(BaseTool):
    """Tool to retrieve HubSpot company properties."""

    def get_tool_definition(self) -> types.Tool:
        """Return the company properties tool definition."""
        return types.Tool(
            name="get_hubspot_company_properties",
            description="Retrieves the list of available properties for HubSpot companies with their types and descriptions",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute company properties retrieval."""
        try:
            properties = await self.client.get_company_properties()
            formatted_result = HubSpotFormatter.format_company_properties(properties)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
