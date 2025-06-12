"""Outil MCP pour récupérer un deal HubSpot par nom."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealByNameTool(BaseTool):
    """Outil pour récupérer un deal HubSpot par nom."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil deal par nom."""
        return types.Tool(
            name="get_deal_by_name",
            description="Récupère un deal HubSpot spécifique par son nom",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {
                        "type": "string",
                        "description": "Nom exact du deal à rechercher",
                    }
                },
                "required": ["deal_name"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération du deal par nom."""
        try:
            deal_name = arguments.get("deal_name")

            if not deal_name:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Erreur**: Le nom du deal est obligatoire.",
                    )
                ]

            deal = await self.client.get_deal_by_name(deal_name)
            formatted_result = HubSpotFormatter.format_single_deal(deal)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)
