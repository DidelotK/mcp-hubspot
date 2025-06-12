"""Formatage des données HubSpot pour l'affichage."""

from typing import Any, Dict, List, Optional


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

    @staticmethod
    def format_single_transaction(transaction: Optional[Dict[str, Any]]) -> str:
        """Formate une transaction unique pour l'affichage."""
        if not transaction:
            return "🔍 **Transaction non trouvée**\n\nAucune transaction ne correspond au nom spécifié."

        props = transaction.get("properties", {})
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

        result = f"💰 **Transaction HubSpot**\n\n"
        result += f"**{props.get('dealname', 'Transaction sans nom')}**\n"
        result += f"  💰 Montant: {amount_formatted}\n"
        result += f"  📊 Étape: {props.get('dealstage', 'N/A')}\n"
        result += f"  🔄 Pipeline: {props.get('pipeline', 'N/A')}\n"
        result += f"  📅 Date de clôture: {props.get('closedate', 'N/A')}\n"
        result += f"  📅 Créée: {props.get('createdate', 'N/A')}\n"
        result += f"  📅 Modifiée: {props.get('lastmodifieddate', 'N/A')}\n"
        result += f"  👤 Propriétaire: {props.get('hubspot_owner_id', 'N/A')}\n"
        result += f"  🆔 ID: {transaction.get('id')}\n"

        return result

    @staticmethod
    def format_contact_properties(properties: List[Dict[str, Any]]) -> str:
        """Formate la liste des propriétés de contacts pour l'affichage."""
        if not properties:
            return "❌ **Aucune propriété trouvée**\n\nImpossible de récupérer les propriétés des contacts."

        result = (
            f"🔧 **Propriétés des Contacts HubSpot** ({len(properties)} propriétés)\n\n"
        )

        # Grouper les propriétés par groupe
        grouped_properties = {}
        for prop in properties:
            group_name = prop.get("groupName", "Autres")
            if group_name not in grouped_properties:
                grouped_properties[group_name] = []
            grouped_properties[group_name].append(prop)

        # Afficher par groupe
        for group_name, group_props in grouped_properties.items():
            result += f"## 📁 {group_name}\n\n"

            for prop in group_props:
                name = prop.get("name", "N/A")
                label = prop.get("label", "N/A")
                type_info = prop.get("type", "N/A")
                field_type = prop.get("fieldType", "N/A")
                description = prop.get("description", "")

                # Icône selon le type de champ
                icon = "📝"
                if field_type == "date":
                    icon = "📅"
                elif field_type == "number":
                    icon = "🔢"
                elif field_type == "select":
                    icon = "📋"
                elif field_type == "checkbox":
                    icon = "☑️"
                elif field_type == "textarea":
                    icon = "📄"
                elif field_type == "file":
                    icon = "📎"
                elif name in ["email", "hs_email_domain"]:
                    icon = "📧"
                elif name in ["phone", "mobilephone"]:
                    icon = "📞"
                elif name in ["company", "associatedcompanyid"]:
                    icon = "🏢"

                result += f"**{icon} {label}**\n"
                result += f"  🏷️ Nom: `{name}`\n"
                result += f"  🔧 Type: {type_info} ({field_type})\n"

                if description:
                    result += f"  📝 Description: {description}\n"

                # Options pour les champs select
                if field_type == "select" and "options" in prop:
                    options = prop["options"]
                    if options:
                        option_labels = [
                            opt.get("label", opt.get("value", ""))
                            for opt in options[:5]
                        ]
                        if len(options) > 5:
                            option_labels.append(f"... et {len(options) - 5} autres")
                        result += f"  📋 Options: {', '.join(option_labels)}\n"

                result += "\n"

            result += "\n"

        return result
