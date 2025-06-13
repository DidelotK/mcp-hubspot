"""Formatters for HubSpot data display."""

import html
from typing import Any, Dict, List, Optional, Union


class HubSpotFormatter:
    """Formatter for HubSpot data display.

    This class provides static methods to format various HubSpot data types
    (contacts, companies, deals, properties) into human-readable text.
    """

    @staticmethod
    def format_contacts(contacts: List[Dict[str, Any]]) -> str:
        """Format the contacts list for display.

        Args:
            contacts: List of contact dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of contacts
        """
        result = f"👥 **HubSpot Contacts** ({len(contacts)} found)\n\n"

        for contact in contacts:
            props = contact.get("properties", {})
            result += f"**{props.get('firstname', '')} {props.get('lastname', '')}**\n"
            result += f"  📧 Email: {props.get('email', 'N/A')}\n"
            result += f"  🏢 Company: {props.get('company', 'N/A')}\n"
            result += f"  📞 Phone: {props.get('phone', 'N/A')}\n"
            result += f"  📅 Created: {props.get('createdate', 'N/A')}\n"
            result += f"  📅 Modified: {props.get('lastmodifieddate', 'N/A')}\n"
            result += f"  🆔 ID: {contact.get('id')}\n\n"

        return result

    @staticmethod
    def format_companies(companies: List[Dict[str, Any]]) -> str:
        """Format the companies list for display.

        Args:
            companies: List of company dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of companies
        """
        result = f"🏢 **HubSpot Companies** ({len(companies)} found)\n\n"

        for company in companies:
            props = company.get("properties", {})
            result += f"**{props.get('name', 'Unnamed company')}**\n"
            result += f"  🌐 Domain: {props.get('domain', 'N/A')}\n"
            result += f"  📍 City: {props.get('city', 'N/A')}\n"
            result += f"  📍 State: {props.get('state', 'N/A')}\n"
            result += f"  🌍 Country: {props.get('country', 'N/A')}\n"
            result += f"  🏭 Industry: {props.get('industry', 'N/A')}\n"
            result += f"  📅 Created: {props.get('createdate', 'N/A')}\n"
            result += f"  📅 Modified: {props.get('lastmodifieddate', 'N/A')}\n"
            result += f"  🆔 ID: {company.get('id')}\n\n"

        return result

    @staticmethod
    def format_deals(deals: List[Dict[str, Any]]) -> str:
        """Format the deals list for display.

        Args:
            deals: List of deal dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of deals
        """
        result = f"💰 **HubSpot Deals** ({len(deals)} found)\n\n"

        for deal in deals:
            props = deal.get("properties", {})
            amount = props.get("amount", "0")

            # Format amount if available
            if amount and amount != "0":
                try:
                    amount_float = float(amount)
                    amount_formatted = f"${amount_float:,.2f}"
                except (ValueError, TypeError):
                    amount_formatted = f"${amount}"
            else:
                amount_formatted = "N/A"

            result += f"**{props.get('dealname', 'Unnamed deal')}**\n"
            result += f"  💰 Amount: {amount_formatted}\n"
            result += f"  📊 Stage: {props.get('dealstage', 'N/A')}\n"
            result += f"  🔄 Pipeline: {props.get('pipeline', 'N/A')}\n"
            result += f"  📅 Close date: {props.get('closedate', 'N/A')}\n"
            result += f"  📅 Created: {props.get('createdate', 'N/A')}\n"
            result += f"  👤 Owner: {props.get('hubspot_owner_id', 'N/A')}\n"
            result += f"  🆔 ID: {deal.get('id')}\n\n"

        return result

    @staticmethod
    def format_single_deal(deal: Optional[Dict[str, Any]]) -> str:
        """Format a single deal for display.

        Args:
            deal: Deal dictionary from HubSpot API or None if not found

        Returns:
            str: Formatted string representation of the deal
        """
        if not deal:
            return "🔍 **Deal not found**\n\nNo deal matches the specified name."

        props = deal.get("properties", {})
        amount = props.get("amount", "0")

        # Format amount if available
        if amount and amount != "0":
            try:
                amount_float = float(amount)
                amount_formatted = f"${amount_float:,.2f}"
            except (ValueError, TypeError):
                amount_formatted = f"${amount}"
        else:
            amount_formatted = "N/A"

        result = f"💰 **HubSpot Deal**\n\n"
        result += f"**{props.get('dealname', 'Unnamed deal')}**\n"
        result += f"  💰 Amount: {amount_formatted}\n"
        result += f"  📊 Stage: {props.get('dealstage', 'N/A')}\n"
        result += f"  🔄 Pipeline: {props.get('pipeline', 'N/A')}\n"
        result += f"  📅 Close date: {props.get('closedate', 'N/A')}\n"
        result += f"  📅 Created: {props.get('createdate', 'N/A')}\n"
        result += f"  📅 Modified: {props.get('lastmodifieddate', 'N/A')}\n"
        result += f"  👤 Owner: {props.get('hubspot_owner_id', 'N/A')}\n"
        result += f"  🆔 ID: {deal.get('id')}\n"

        return result

    @staticmethod
    def format_contact_properties(properties: List[Dict[str, Any]]) -> str:
        """Format the contact properties list for display.

        Args:
            properties: List of property dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of contact properties
        """
        if not properties:
            return (
                "❌ **No properties found**\n\nUnable to retrieve contact properties."
            )

        result = f"🔧 **HubSpot Contact Properties** ({len(properties)} properties)\n\n"

        # Group properties by group
        grouped_properties: Dict[str, List[Dict[str, Any]]] = {}
        for prop in properties:
            group_name = prop.get("groupName", "Other")
            if group_name not in grouped_properties:
                grouped_properties[group_name] = []
            grouped_properties[group_name].append(prop)

        # Display by group
        for group_name, group_props in grouped_properties.items():
            result += f"## 📁 {group_name}\n\n"

            for prop in group_props:
                name = prop.get("name", "N/A")
                label = prop.get("label", "N/A")
                type_info = prop.get("type", "N/A")
                field_type = prop.get("fieldType", "N/A")
                description = prop.get("description", "")

                # Icon based on field type
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
                result += f"  🏷️ Name: `{name}`\n"
                result += f"  🔧 Type: {type_info} ({field_type})\n"

                if description:
                    result += f"  📝 Description: {description}\n"

                # Options for select fields
                if field_type == "select" and "options" in prop:
                    options = prop["options"]
                    if options:
                        option_labels = [
                            opt.get("label", opt.get("value", ""))
                            for opt in options[:5]
                        ]
                        if len(options) > 5:
                            option_labels.append(f"... and {len(options) - 5} more")
                        result += f"  📋 Options: {', '.join(option_labels)}\n"

                result += "\n"

            result += "\n"

        return result

    @staticmethod
    def format_deal_properties(properties: List[Dict[str, Any]]) -> str:
        """Format the deal properties list for display.

        Args:
            properties: List of property dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of deal properties
        """
        if not properties:
            return "❌ **No properties found**\n\nUnable to retrieve deal properties."

        result = f"🔧 **HubSpot Deal Properties** ({len(properties)} properties)\n\n"

        # Group properties by group
        grouped_properties: Dict[str, List[Dict[str, Any]]] = {}
        for prop in properties:
            group_name = prop.get("groupName", "Other")
            if group_name not in grouped_properties:
                grouped_properties[group_name] = []
            grouped_properties[group_name].append(prop)

        # Display by group
        for group_name, group_props in grouped_properties.items():
            result += f"## 📁 {group_name}\n\n"

            for prop in group_props:
                name = prop.get("name", "N/A")
                label = prop.get("label", "N/A")
                type_info = prop.get("type", "N/A")
                field_type = prop.get("fieldType", "N/A")
                description = prop.get("description", "")

                # Icon based on field type
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
                elif name in ["amount", "hs_deal_amount"]:
                    icon = "💰"
                elif name in ["dealname", "hs_deal_name"]:
                    icon = "🏷️"
                elif name in ["dealstage", "hs_deal_stage"]:
                    icon = "📊"
                elif name in ["pipeline", "hs_pipeline"]:
                    icon = "🔄"
                elif name in ["closedate", "hs_closedate"]:
                    icon = "📅"

                result += f"**{icon} {label}**\n"
                result += f"  🏷️ Name: `{name}`\n"
                result += f"  🔧 Type: {type_info} ({field_type})\n"

                if description:
                    result += f"  📝 Description: {description}\n"

                # Options for select fields
                if field_type == "select" and "options" in prop:
                    options = prop["options"]
                    if options:
                        option_labels = [
                            opt.get("label", opt.get("value", ""))
                            for opt in options[:5]
                        ]
                        if len(options) > 5:
                            option_labels.append(f"... and {len(options) - 5} more")
                        result += f"  📋 Options: {', '.join(option_labels)}\n"

                result += "\n"

            result += "\n"

        return result

    @staticmethod
    def format_company_properties(properties: List[Dict[str, Any]]) -> str:
        """Format the company properties list for display.

        Args:
            properties: List of property dictionaries from HubSpot API

        Returns:
            str: Formatted string representation of company properties
        """
        if not properties:
            return (
                "❌ **No properties found**\n\nUnable to retrieve company properties."
            )

        result = f"🏢 **HubSpot Company Properties** ({len(properties)} properties)\n\n"

        # Group properties by group
        grouped_properties: Dict[str, List[Dict[str, Any]]] = {}
        for prop in properties:
            group_name = prop.get("groupName", "Other")
            if group_name not in grouped_properties:
                grouped_properties[group_name] = []
            grouped_properties[group_name].append(prop)

        # Display by group
        for group_name, group_props in grouped_properties.items():
            result += f"## 📁 {group_name}\n\n"

            for prop in group_props:
                name = prop.get("name", "N/A")
                label = prop.get("label", "N/A")
                type_info = prop.get("type", "N/A")
                field_type = prop.get("fieldType", "N/A")
                description = prop.get("description", "")

                # Icon based on field type
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
                elif name in ["domain", "website"]:
                    icon = "🌐"
                elif name in ["industry", "type"]:
                    icon = "🏭"
                elif name in ["city", "state", "country"]:
                    icon = "📍"

                result += f"**{icon} {label}**\n"
                result += f"  🏷️ Name: `{name}`\n"
                result += f"  🔧 Type: {type_info} ({field_type})\n"

                if description:
                    result += f"  📝 Description: {description}\n"

                # Options for select fields
                if field_type == "select" and "options" in prop:
                    options = prop["options"]
                    if options:
                        option_labels = [
                            opt.get("label", opt.get("value", ""))
                            for opt in options[:5]
                        ]
                        if len(options) > 5:
                            option_labels.append(f"... and {len(options) - 5} more")
                        result += f"  📋 Options: {', '.join(option_labels)}\n"

                result += "\n"

            result += "\n"

        return result

    @staticmethod
    def format_deal(deal: Dict[str, Any]) -> str:
        """Format a single deal for display.

        Args:
            deal: Deal dictionary from HubSpot API

        Returns:
            str: Formatted string representation of the deal
        """

        def clean(val: Any, default: str) -> str:
            """Clean a value for display.

            Args:
                val: Value to clean
                default: Default value if cleaning fails

            Returns:
                str: Cleaned value
            """
            if val is None:
                return default
            return str(val)

        props = deal.get("properties", {})
        amount = props.get("amount", "0")

        # Format amount if available
        if amount and amount != "0":
            try:
                amount_float = float(amount)
                amount_formatted = f"${amount_float:,.2f}"
            except (ValueError, TypeError):
                amount_formatted = f"${amount}"
        else:
            amount_formatted = "N/A"

        result = f"💰 **HubSpot Deal**\n\n"
        result += f"**{clean(props.get('dealname'), 'Unnamed deal')}**\n"
        result += f"  💰 Amount: {amount_formatted}\n"
        result += f"  📊 Stage: {clean(props.get('dealstage'), 'N/A')}\n"
        result += f"  🔄 Pipeline: {clean(props.get('pipeline'), 'N/A')}\n"
        result += f"  📅 Close date: {clean(props.get('closedate'), 'N/A')}\n"
        result += f"  📅 Created: {clean(props.get('createdate'), 'N/A')}\n"
        result += f"  📅 Modified: {clean(props.get('lastmodifieddate'), 'N/A')}\n"
        result += f"  👤 Owner: {clean(props.get('hubspot_owner_id'), 'N/A')}\n"
        result += f"  🆔 ID: {clean(deal.get('id'), 'N/A')}\n"

        return result

    @staticmethod
    def format_engagements(engagements: List[Dict[str, Any]]) -> str:
        """Formats a list of HubSpot engagements for display."""
        lines: List[str] = []
        lines.append(f"📞 **HubSpot Engagements** ({len(engagements)} found)\n")
        for eng in engagements:
            props = eng.get("properties", {})
            meta: Dict[str, Any] = props.get(
                "metadata", {}
            )  # May contain type-specific fields

            subject: str = (
                props.get("subject")
                or meta.get("subject")
                or meta.get("title")
                or "No subject"
            )
            body_preview: Optional[str] = meta.get("body") or meta.get("text")

            lines.append(f"**{subject}**")
            lines.append(f"  🔖 Type: {props.get('engagement_type', 'N/A')}")

            # Optional extra info
            if body_preview:
                snippet = body_preview[:60].replace("\n", " ")
                lines.append(f"  📝 Snippet: {snippet}…")

            lines.append(f"  🗓️ Created: {props.get('createdate')}")
            lines.append(f"  🔄 Updated: {props.get('lastmodifieddate')}")
            lines.append(f"  🆔 ID: {eng.get('id')}\n")
        return "\n".join(lines)
