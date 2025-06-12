"""Outil MCP pour gérer les contacts HubSpot."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class ContactsTool(BaseTool):
    """Outil pour lister les contacts HubSpot."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil contacts."""
        return types.Tool(
            name="list_hubspot_contacts",
            description="Liste les contacts HubSpot avec possibilité de filtrage",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum de contacts à retourner (défaut: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtres optionnels pour la recherche",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Terme de recherche pour filtrer les contacts",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération des contacts."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            contacts = await self.client.get_contacts(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_contacts(contacts)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
