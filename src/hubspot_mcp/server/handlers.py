"""Handlers for HubSpot MCP server."""

import logging
from typing import Any, Dict, List, Optional

import mcp.types as types

from ..client import HubSpotClient
from ..tools import (
    CompaniesTool,
    CompanyPropertiesTool,
    ContactPropertiesTool,
    ContactsTool,
    CreateDealTool,
    DealPropertiesTool,
    DealsTool,
    TransactionByNameTool,
)

logger = logging.getLogger(__name__)


class MCPHandlers:
    """MCP handlers manager for HubSpot."""

    def __init__(self, client: HubSpotClient):
        self.client = client
        self.contacts_tool = ContactsTool(client)
        self.companies_tool = CompaniesTool(client)
        self.deals_tool = DealsTool(client)
        self.create_deal_tool = CreateDealTool(client)
        self.transaction_by_name_tool = TransactionByNameTool(client)
        self.contact_properties_tool = ContactPropertiesTool(client)
        self.company_properties_tool = CompanyPropertiesTool(client)
        self.deal_properties_tool = DealPropertiesTool(client)

        # Tools mapping
        self.tools_map = {
            "list_hubspot_contacts": self.contacts_tool,
            "list_hubspot_companies": self.companies_tool,
            "list_hubspot_deals": self.deals_tool,
            "create_transaction": self.create_deal_tool,
            "get_transaction_by_name": self.transaction_by_name_tool,
            "get_hubspot_contact_properties": self.contact_properties_tool,
            "get_hubspot_company_properties": self.company_properties_tool,
            "get_hubspot_deal_properties": self.deal_properties_tool,
        }

    async def handle_list_tools(self) -> List[types.Tool]:
        """List all available tools."""
        tools = []
        for tool in self.tools_map.values():
            tools.append(tool.get_tool_definition())
        return tools

    async def handle_call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Execute the requested tool."""
        if self.client is None:
            return [
                types.TextContent(
                    type="text",
                    text="Error: HubSpot client not initialized. Check your API key.",
                )
            ]

        tool = self.tools_map.get(name)
        if tool is None:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        return await tool.execute(arguments)
