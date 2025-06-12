"""Handlers pour le serveur MCP HubSpot."""

import logging
from typing import Any, Dict, List, Optional

import mcp.types as types

from ..client import HubSpotClient
from ..tools import (
    CompaniesTool,
    ContactPropertiesTool,
    ContactsTool,
    DealsTool,
    TransactionByNameTool,
)

logger = logging.getLogger(__name__)


class MCPHandlers:
    """Gestionnaire des handlers MCP pour HubSpot."""

    def __init__(self, client: HubSpotClient):
        self.client = client
        self.contacts_tool = ContactsTool(client)
        self.companies_tool = CompaniesTool(client)
        self.deals_tool = DealsTool(client)
        self.transaction_by_name_tool = TransactionByNameTool(client)
        self.contact_properties_tool = ContactPropertiesTool(client)

        # Mappage des outils
        self.tools_map = {
            "list_hubspot_contacts": self.contacts_tool,
            "list_hubspot_companies": self.companies_tool,
            "list_hubspot_deals": self.deals_tool,
            "get_transaction_by_name": self.transaction_by_name_tool,
            "get_hubspot_contact_properties": self.contact_properties_tool,
        }

    async def handle_list_tools(self) -> List[types.Tool]:
        """Liste tous les outils disponibles."""
        tools = []
        for tool in self.tools_map.values():
            tools.append(tool.get_tool_definition())
        return tools

    async def handle_call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Exécute l'outil demandé."""
        if self.client is None:
            return [
                types.TextContent(
                    type="text",
                    text="Erreur: Client HubSpot non initialisé. Vérifiez votre clé API.",
                )
            ]

        tool = self.tools_map.get(name)
        if tool is None:
            return [types.TextContent(type="text", text=f"Outil inconnu: {name}")]

        return await tool.execute(arguments)
