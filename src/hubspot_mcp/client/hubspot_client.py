"""Client to interact with HubSpot API."""

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client to interact with HubSpot API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get_contacts(
        self, limit: int = 100, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve the list of contacts with optional filtering."""
        url = f"{self.base_url}/crm/v3/objects/contacts"

        params = {
            "limit": limit,
            "properties": "firstname,lastname,email,company,phone,createdate,lastmodifieddate",
        }

        # Add filters if provided
        if filters:
            # HubSpot uses complex filters, we can add simple search
            if "search" in filters:
                params["search"] = filters["search"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_companies(
        self, limit: int = 100, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve the list of companies with optional filtering."""
        url = f"{self.base_url}/crm/v3/objects/companies"

        params = {
            "limit": limit,
            "properties": "name,domain,city,state,country,industry,createdate,lastmodifieddate",
        }

        # Add filters if provided
        if filters:
            if "search" in filters:
                params["search"] = filters["search"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deals(
        self, limit: int = 100, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve the list of deals with optional filtering."""
        url = f"{self.base_url}/crm/v3/objects/deals"

        params = {
            "limit": limit,
            "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,lastmodifieddate,hubspot_owner_id",
        }

        # Add filters if provided
        if filters:
            if "search" in filters:
                params["search"] = filters["search"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deal_by_name(self, deal_name: str) -> Optional[Dict]:
        """Retrieve a specific deal by its name."""
        url = f"{self.base_url}/crm/v3/objects/deals/search"

        # Request body to search by deal name
        search_body = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "dealname",
                            "operator": "EQ",
                            "value": deal_name,
                        }
                    ]
                }
            ],
            "properties": [
                "dealname",
                "amount",
                "dealstage",
                "pipeline",
                "closedate",
                "createdate",
                "lastmodifieddate",
                "hubspot_owner_id",
            ],
            "limit": 1,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=search_body)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            return results[0] if results else None

    async def get_contact_properties(self) -> List[Dict]:
        """Retrieve the list of available properties for contacts."""
        url = f"{self.base_url}/crm/v3/properties/contacts"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_company_properties(self) -> List[Dict]:
        """Retrieve the list of available properties for companies."""
        url = f"{self.base_url}/crm/v3/properties/companies"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deal_properties(self) -> List[Dict]:
        """Retrieve the list of available properties for deals."""
        url = f"{self.base_url}/crm/v3/properties/deals"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal in HubSpot."""
        url = f"{self.base_url}/crm/v3/objects/deals"

        # Structure data for HubSpot
        payload = {"properties": deal_data}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

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
