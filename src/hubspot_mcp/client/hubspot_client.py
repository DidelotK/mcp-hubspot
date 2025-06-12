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
