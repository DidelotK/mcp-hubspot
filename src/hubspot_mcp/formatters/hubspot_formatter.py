"""Formatage des données HubSpot pour l'affichage."""

from typing import Any, Dict, List


class HubSpotFormatter:
    """Classe de formatage des données HubSpot."""

    @staticmethod
    def format_contacts(contacts: List[Dict[str, Any]]) -> str:
        """Formate la liste des contacts pour l'affichage."""
        result = f"📋 **Contacts HubSpot** ({len(contacts)} trouvés)\n\n"

        for contact in contacts:
            props = contact.get("properties", {})
            result += f"**{props.get('firstname', '')} {props.get('lastname', '')}**\n"
            result += f"  📧 Email: {props.get('email', 'N/A')}\n"
            result += f"  🏢 Entreprise: {props.get('company', 'N/A')}\n"
            result += f"  📞 Téléphone: {props.get('phone', 'N/A')}\n"
            result += f"  📅 Créé: {props.get('createdate', 'N/A')}\n"
            result += f"  🆔 ID: {contact.get('id')}\n\n"

        return result

    @staticmethod
    def format_companies(companies: List[Dict[str, Any]]) -> str:
        """Formate la liste des entreprises pour l'affichage."""
        result = f"🏢 **Entreprises HubSpot** ({len(companies)} trouvées)\n\n"

        for company in companies:
            props = company.get("properties", {})
            location = ", ".join(
                filter(
                    None,
                    [
                        props.get("city", ""),
                        props.get("state", ""),
                        props.get("country", ""),
                    ],
                )
            )

            result += f"**{props.get('name', 'Nom non spécifié')}**\n"
            result += f"  🌐 Domaine: {props.get('domain', 'N/A')}\n"
            result += f"  📍 Localisation: {location or 'N/A'}\n"
            result += f"  🏭 Secteur: {props.get('industry', 'N/A')}\n"
            result += f"  📅 Créée: {props.get('createdate', 'N/A')}\n"
            result += f"  🆔 ID: {company.get('id')}\n\n"

        return result

    @staticmethod
    def format_deals(deals: List[Dict[str, Any]]) -> str:
        """Formate la liste des transactions pour l'affichage."""
        result = f"💰 **Transactions HubSpot** ({len(deals)} trouvées)\n\n"

        for deal in deals:
            props = deal.get("properties", {})
            amount = props.get("amount", "0")
            
            # Formatage du montant si disponible
            if amount and amount != "0":
                try:
                    amount_float = float(amount)
                    amount_formatted = f"{amount_float:,.2f} €"
                except (ValueError, TypeError):
                    amount_formatted = f"{amount} €"
            else:
                amount_formatted = "N/A"

            result += f"**{props.get('dealname', 'Transaction sans nom')}**\n"
            result += f"  💰 Montant: {amount_formatted}\n"
            result += f"  📊 Étape: {props.get('dealstage', 'N/A')}\n"
            result += f"  🔄 Pipeline: {props.get('pipeline', 'N/A')}\n"
            result += f"  📅 Date de clôture: {props.get('closedate', 'N/A')}\n"
            result += f"  📅 Créée: {props.get('createdate', 'N/A')}\n"
            result += f"  👤 Propriétaire: {props.get('hubspot_owner_id', 'N/A')}\n"
            result += f"  🆔 ID: {deal.get('id')}\n\n"

        return result
