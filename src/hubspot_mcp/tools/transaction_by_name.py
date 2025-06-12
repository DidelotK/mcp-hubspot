"""Outil MCP pour récupérer une transaction HubSpot par nom."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class TransactionByNameTool(BaseTool):
    """Outil pour récupérer une transaction HubSpot par nom."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil transaction par nom."""
        return types.Tool(
            name="get_transaction_by_name",
            description="Récupère une transaction HubSpot spécifique par son nom",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {
                        "type": "string",
                        "description": "Nom exact de la transaction à rechercher",
                        "minLength": 1,
                    }
                },
                "required": ["deal_name"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération de la transaction par nom."""
        try:
            deal_name = arguments.get("deal_name")
            
            if not deal_name:
                return [types.TextContent(
                    type="text", 
                    text="❌ **Erreur**: Le nom de la transaction est obligatoire."
                )]

            transaction = await self.client.get_transaction_by_name(deal_name)
            formatted_result = HubSpotFormatter.format_single_transaction(transaction)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e) 