"""Handlers for HubSpot MCP server."""

import logging
from typing import Any, Dict, List, Optional

import mcp.types as types

from ..client import HubSpotClient
from ..tools import (
    CacheManagementTool,
    CompaniesTool,
    CompanyPropertiesTool,
    ContactPropertiesTool,
    ContactsTool,
    CreateDealTool,
    DealByNameTool,
    DealPropertiesTool,
    DealsTool,
    EmbeddingManagementTool,
    EngagementsTool,
    SearchCompaniesTool,
    SearchContactsTool,
    SearchDealsTool,
    SemanticSearchTool,
    UpdateDealTool,
)

logger = logging.getLogger(__name__)


class MCPHandlers:
    """MCP handlers manager for HubSpot.

    This class manages the available tools and handles tool execution requests
    from the MCP server.
    """

    def __init__(self, client: HubSpotClient):
        """Initialize the MCP handlers.

        Args:
            client: The HubSpot client instance to use for API calls
        """
        self.client = client
        self.cache_management_tool = CacheManagementTool(client)
        self.contacts_tool = ContactsTool(client)
        self.companies_tool = CompaniesTool(client)
        self.deals_tool = DealsTool(client)
        self.create_deal_tool = CreateDealTool(client)
        self.deal_by_name_tool = DealByNameTool(client)
        self.contact_properties_tool = ContactPropertiesTool(client)
        self.company_properties_tool = CompanyPropertiesTool(client)
        self.deal_properties_tool = DealPropertiesTool(client)
        self.update_deal_tool = UpdateDealTool(client)
        self.engagements_tool = EngagementsTool(client)
        self.search_deals_tool = SearchDealsTool(client)
        self.search_contacts_tool = SearchContactsTool(client)
        self.search_companies_tool = SearchCompaniesTool(client)
        self.semantic_search_tool = SemanticSearchTool(client)
        self.embedding_management_tool = EmbeddingManagementTool(client)

        # Tools mapping
        self.tools_map: Dict[str, Any] = {
            "manage_hubspot_cache": self.cache_management_tool,
            "list_hubspot_contacts": self.contacts_tool,
            "list_hubspot_companies": self.companies_tool,
            "list_hubspot_deals": self.deals_tool,
            "create_deal": self.create_deal_tool,
            "list_hubspot_engagements": self.engagements_tool,
            "get_deal_by_name": self.deal_by_name_tool,
            "get_hubspot_contact_properties": self.contact_properties_tool,
            "get_hubspot_company_properties": self.company_properties_tool,
            "get_hubspot_deal_properties": self.deal_properties_tool,
            "update_deal": self.update_deal_tool,
            "search_hubspot_deals": self.search_deals_tool,
            "search_hubspot_contacts": self.search_contacts_tool,
            "search_hubspot_companies": self.search_companies_tool,
            "semantic_search_hubspot": self.semantic_search_tool,
            "manage_hubspot_embeddings": self.embedding_management_tool,
        }

    async def handle_list_tools(self) -> List[types.Tool]:
        """List all available tools.

        Returns:
            List[types.Tool]: List of tool definitions
        """
        tools: List[types.Tool] = []
        for tool in self.tools_map.values():
            tools.append(tool.get_tool_definition())
        return tools

    async def handle_call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Execute the requested tool.

        Args:
            name: Name of the tool to execute
            arguments: Dictionary of arguments for the tool

        Returns:
            List[types.TextContent]: List of text content items representing the tool's output

        Raises:
            Exception: If the tool execution fails
        """
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

        try:
            return await tool.execute(arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}",
                )
            ]
