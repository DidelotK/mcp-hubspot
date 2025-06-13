from typing import Any, Dict

import httpx


class HubSpotClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def update_deal(
        self, deal_id: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Updates a deal in HubSpot.

        Args:
            deal_id: The ID of the deal to update
            properties: Dictionary of properties to update

        Returns:
            The updated deal data
        """
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"

        data = {"properties": properties}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
