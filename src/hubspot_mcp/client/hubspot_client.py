"""Client pour interagir avec l'API HubSpot."""

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client pour interagir avec l'API HubSpot."""

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
        """Récupère la liste des contacts avec filtrage optionnel."""
        url = f"{self.base_url}/crm/v3/objects/contacts"

        params = {
            "limit": limit,
            "properties": "firstname,lastname,email,company,phone,createdate,lastmodifieddate",
        }

        # Ajouter des filtres si fournis
        if filters:
            # HubSpot utilise des filtres complexes, on peut ajouter une recherche simple
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
        """Récupère la liste des entreprises avec filtrage optionnel."""
        url = f"{self.base_url}/crm/v3/objects/companies"

        params = {
            "limit": limit,
            "properties": "name,domain,city,state,country,industry,createdate,lastmodifieddate",
        }

        # Ajouter des filtres si fournis
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
        """Récupère la liste des deals avec filtrage optionnel."""
        url = f"{self.base_url}/crm/v3/objects/deals"

        params = {
            "limit": limit,
            "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,lastmodifieddate,hubspot_owner_id",
        }

        # Ajouter des filtres si fournis
        if filters:
            if "search" in filters:
                params["search"] = filters["search"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deal_by_name(self, deal_name: str) -> Optional[Dict]:
        """Récupère un deal spécifique par son nom."""
        url = f"{self.base_url}/crm/v3/objects/deals/search"

        # Corps de la requête pour rechercher par nom de deal
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
        """Récupère la liste des propriétés disponibles pour les contacts."""
        url = f"{self.base_url}/crm/v3/properties/contacts"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_company_properties(self) -> List[Dict]:
        """Récupère la liste des propriétés disponibles pour les entreprises."""
        url = f"{self.base_url}/crm/v3/properties/companies"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau deal dans HubSpot."""
        url = f"{self.base_url}/crm/v3/objects/deals"

        # Structure des données pour HubSpot
        payload = {"properties": deal_data}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
