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


class CreateDealTool(BaseTool):
    """Outil pour créer une nouvelle transaction HubSpot."""

    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil de création de transaction."""
        return types.Tool(
            name="create_transaction",
            description="Crée une nouvelle transaction (deal) dans HubSpot",
            inputSchema={
                "type": "object",
                "properties": {
                    "dealname": {
                        "type": "string",
                        "description": "Nom de la transaction (obligatoire)",
                    },
                    "amount": {
                        "type": "string",
                        "description": "Montant de la transaction",
                    },
                    "dealstage": {
                        "type": "string",
                        "description": "Étape de la transaction (ex: 'appointmentscheduled', 'qualifiedtobuy', 'presentationscheduled', 'decisionmakerboughtin', 'contractsent', 'closedwon', 'closedlost')",
                    },
                    "pipeline": {
                        "type": "string",
                        "description": "Pipeline de la transaction",
                    },
                    "closedate": {
                        "type": "string",
                        "description": "Date de clôture prévue (format: YYYY-MM-DD)",
                    },
                    "hubspot_owner_id": {
                        "type": "string",
                        "description": "ID du propriétaire de la transaction",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description de la transaction",
                    },
                },
                "required": ["dealname"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute la création de la transaction."""
        try:
            # Valider les arguments requis
            if not arguments.get("dealname"):
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Erreur de validation**\n\nLe nom de la transaction (dealname) est obligatoire.",
                    )
                ]

            # Préparer les données de la transaction
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

            # Créer la transaction
            created_deal = await self.client.create_deal(deal_data)

            # Formater la réponse de succès
            result_text = "✅ **Transaction créée avec succès !**\n\n"
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
