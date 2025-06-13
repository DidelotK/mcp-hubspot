from typing import Any, Dict


class Formatters:
    @staticmethod
    def format_deal(deal: Dict[str, Any]) -> str:
        """Formats a single deal for display.

        Args:
            deal: The deal data to format

        Returns:
            Formatted string representation of the deal
        """
        properties = deal.get("properties", {})

        result = [
            "💰 **HubSpot Deal Updated**\n",
            f"**{properties.get('dealname', 'Unnamed Deal')}**",
            f"  💰 Amount: {properties.get('amount', 'N/A')}",
            f"  📊 Stage: {properties.get('dealstage', 'N/A')}",
            f"  🔄 Pipeline: {properties.get('pipeline', 'N/A')}",
            f"  📅 Close Date: {properties.get('closedate', 'N/A')}",
            f"  📝 Description: {properties.get('description', 'N/A')}",
            f"  🆔 ID: {deal.get('id', 'N/A')}",
        ]

        return "\n".join(result)
