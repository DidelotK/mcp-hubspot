"""Outil MCP pour gérer les transactions HubSpot."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealsTool(BaseTool):
    """Outil pour lister les transactions HubSpot."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil transactions."""
        return types.Tool(
            name="list_hubspot_deals",
            description="Liste les transactions (deals) HubSpot avec possibilité de filtrage",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum de transactions à retourner (défaut: 100)",
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
                                "description": "Terme de recherche pour filtrer les transactions",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération des transactions."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            deals = await self.client.get_deals(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
