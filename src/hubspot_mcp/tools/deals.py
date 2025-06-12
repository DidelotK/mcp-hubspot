"""MCP tool to manage HubSpot deals."""

from typing import Any, Dict, List

import mcp.types as types

from ..formatters import HubSpotFormatter
from .base import BaseTool


class DealsTool(BaseTool):
    """Tool to list HubSpot deals."""

    def get_tool_definition(self) -> types.Tool:
        """Return the deals tool definition."""
        return types.Tool(
            name="list_hubspot_deals",
            description="Lists HubSpot deals with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deals to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters for search",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Search term to filter deals",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute deals retrieval."""
        try:
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})

            deals = await self.client.get_deals(limit=limit, filters=filters)
            formatted_result = HubSpotFormatter.format_deals(deals)

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)


class CreateDealTool(BaseTool):
    """Outil pour créer un nouveau deal HubSpot."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil de création de deal."""
        return types.Tool(
            name="create_deal",
            description="Crée un nouveau deal dans HubSpot",
            inputSchema={
                "type": "object",
                "properties": {
                    "dealname": {
                        "type": "string",
                        "description": "Nom du deal (obligatoire)",
                    },
                    "amount": {
                        "type": "string",
                        "description": "Montant du deal",
                    },
                    "dealstage": {
                        "type": "string",
                        "description": "Étape du deal (ex: 'appointmentscheduled', 'qualifiedtobuy', 'presentationscheduled', 'decisionmakerboughtin', 'contractsent', 'closedwon', 'closedlost')",
                    },
                    "pipeline": {
                        "type": "string",
                        "description": "Pipeline du deal",
                    },
                    "closedate": {
                        "type": "string",
                        "description": "Date de clôture prévue (format: YYYY-MM-DD)",
                    },
                    "hubspot_owner_id": {
                        "type": "string",
                        "description": "ID du propriétaire du deal",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description du deal",
                    },
                },
                "required": ["dealname"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la création du deal."""
        try:
            # Valider les arguments requis
            if not arguments.get("dealname"):
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Erreur de validation**\n\nLe nom du deal (dealname) est obligatoire.",
                    )
                ]

            # Préparer les données du deal
            deal_data = {
                "dealname": arguments["dealname"],
            }

            # Ajouter les champs optionnels s'ils sont fournis
            optional_fields = [
                "amount",
                "dealstage",
                "pipeline",
                "closedate",
                "hubspot_owner_id",
                "description",
            ]

            for field in optional_fields:
                if field in arguments and arguments[field]:
                    deal_data[field] = arguments[field]

            # Créer le deal
            created_deal = await self.client.create_deal(deal_data)

            # Formater la réponse de succès
            result_text = "✅ **Deal créé avec succès !**\n\n"
            result_text += f"**{deal_data['dealname']}**\n"
            result_text += f"🆔 ID: {created_deal.get('id')}\n"

            # Afficher les propriétés créées
            properties = created_deal.get("properties", {})
            if properties.get("amount"):
                try:
                    amount_float = float(properties["amount"])
                    amount_formatted = f"{amount_float:,.2f} €"
                except (ValueError, TypeError):
                    amount_formatted = f"{properties['amount']} €"
                result_text += f"💰 Montant: {amount_formatted}\n"

            if properties.get("dealstage"):
                result_text += f"📊 Étape: {properties['dealstage']}\n"

            if properties.get("pipeline"):
                result_text += f"🔄 Pipeline: {properties['pipeline']}\n"

            if properties.get("closedate"):
                result_text += f"📅 Date de clôture: {properties['closedate']}\n"

            if properties.get("createdate"):
                result_text += f"📅 Créée le: {properties['createdate']}\n"

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            return self.handle_error(e)
