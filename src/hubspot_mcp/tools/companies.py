"""Outil MCP pour gérer les entreprises HubSpot."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class CompaniesTool(BaseTool):
    """Outil pour lister les entreprises HubSpot."""
    
    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil entreprises."""
        return types.Tool(
            name="list_hubspot_companies",
            description="Liste les entreprises HubSpot avec possibilité de filtrage",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum d'entreprises à retourner (défaut: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtres optionnels pour la recherche",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Terme de recherche pour filtrer les entreprises"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la récupération des entreprises."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})
            
            companies = await self.client.get_companies(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_companies(companies)
            
            return [types.TextContent(type="text", text=formatted_result)]
        
        except Exception as e:
            return self.handle_error(e) 