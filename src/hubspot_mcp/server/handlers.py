"""Handlers for HubSpot MCP server."""

import logging
from typing import Any, Dict, List, Optional

import mcp.types as types

from ..client import HubSpotClient
from ..prompts import HubSpotPrompts
from ..tools import (
    BulkCacheLoaderTool,
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
    FaissDataTool,
    SearchCompaniesTool,
    SearchContactsTool,
    SearchDealsTool,
    SemanticSearchTool,
    UpdateDealTool,
)

logger = logging.getLogger(__name__)


class MCPHandlers:
    """MCP handlers manager for HubSpot.

    This class manages the available tools and prompts, and handles execution requests
    from the MCP server.
    """

    def __init__(self, client: HubSpotClient):
        """Initialize the MCP handlers.

        Args:
            client: The HubSpot client instance to use for API calls
        """
        self.client = client
        self.bulk_cache_loader_tool = BulkCacheLoaderTool(client)
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
        self.faiss_data_tool = FaissDataTool(client)

        # Tools mapping
        self.tools_map: Dict[str, Any] = {
            "semantic_search_hubspot": self.semantic_search_tool,
            "load_hubspot_entities_to_cache": self.bulk_cache_loader_tool,
            "list_hubspot_contacts": self.contacts_tool,
            "get_hubspot_contact_properties": self.contact_properties_tool,
            "list_hubspot_companies": self.companies_tool,
            "get_hubspot_company_properties": self.company_properties_tool,
            "list_hubspot_deals": self.deals_tool,
            "get_deal_by_name": self.deal_by_name_tool,
            "create_deal": self.create_deal_tool,
            "update_deal": self.update_deal_tool,
            "get_hubspot_deal_properties": self.deal_properties_tool,
            "list_hubspot_engagements": self.engagements_tool,
            "search_hubspot_deals": self.search_deals_tool,
            "search_hubspot_contacts": self.search_contacts_tool,
            "search_hubspot_companies": self.search_companies_tool,
            "manage_hubspot_cache": self.cache_management_tool,
            "browse_hubspot_indexed_data": self.faiss_data_tool,
            "manage_hubspot_embeddings": self.embedding_management_tool,
        }

        # Initialize prompts
        self.prompts = HubSpotPrompts()

    async def handle_list_tools(self) -> List[types.Tool]:
        """List all available tools.

        Returns:
            List[types.Tool]: List of tool definitions
        """
        tools: List[types.Tool] = []
        for tool in self.tools_map.values():
            tools.append(tool.get_tool_definition())
        return tools

    async def handle_list_prompts(self) -> List[types.Prompt]:
        """List all available prompts.

        Returns:
            List[types.Prompt]: List of prompt definitions
        """
        return self.prompts.get_prompt_definitions()

    async def handle_get_prompt(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> types.GetPromptResult:
        """Get prompt content by name.

        Args:
            name: Name of the prompt to get
            arguments: Optional arguments for the prompt

        Returns:
            types.GetPromptResult: The prompt result with generated content
        """
        if arguments is None:
            arguments = {}

        try:
            content = self.prompts.generate_prompt_content(name, arguments)
            return types.GetPromptResult(
                description=f"Generated guidance for {name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=content,
                        ),
                    )
                ],
            )
        except Exception as e:
            logger.error(f"Error generating prompt {name}: {str(e)}")
            return types.GetPromptResult(
                description=f"Error generating prompt {name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Error generating prompt {name}: {str(e)}",
                        ),
                    )
                ],
            )

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
