"""Outil MCP pour récupérer les propriétés des contacts HubSpot."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class ContactPropertiesTool(BaseTool):
    """Outil pour récupérer les propriétés des contacts HubSpot."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil propriétés de contacts."""
        return types.Tool(
            name="get_hubspot_contact_properties",
            description="Récupère la liste des propriétés disponibles pour les contacts HubSpot avec leurs types et descriptions",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération des propriétés des contacts."""
        try:
            properties = await self.client.get_contact_properties()
            formatted_result = HubSpotFormatter.format_contact_properties(properties)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
