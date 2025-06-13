"""Client to interact with HubSpot API."""

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client to interact with HubSpot API.

    This class provides methods to interact with the HubSpot API, including
    retrieving and managing contacts, companies, and deals.
    """

    def __init__(self, api_key: str):
        """Initialize the HubSpot client.

        Args:
            api_key: The HubSpot API key to use for authentication
        """
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get_contacts(
        self, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of contacts with optional filtering.

        Args:
            limit: Maximum number of contacts to retrieve
            filters: Optional search filters

        Returns:
            List[Dict[str, Any]]: List of contact dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
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
        self, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of companies with optional filtering.

        Args:
            limit: Maximum number of companies to retrieve
            filters: Optional search filters

        Returns:
            List[Dict[str, Any]]: List of company dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
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
        self, limit: int = 100, after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of deals with pagination support.

        Args:
            limit: Maximum number of deals to retrieve (max 100)
            after: Pagination cursor to get the next set of results

        Returns:
            List[Dict[str, Any]]: List of deal dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/deals"

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,lastmodifieddate,hubspot_owner_id",
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deal_by_name(self, deal_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific deal by its name.

        Args:
            deal_name: The exact name of the deal to search for

        Returns:
            Optional[Dict[str, Any]]: Deal dictionary if found, None otherwise

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
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

    async def get_contact_properties(self) -> List[Dict[str, Any]]:
        """Retrieve the list of available properties for contacts.

        Returns:
            List[Dict[str, Any]]: List of contact property dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/properties/contacts"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_company_properties(self) -> List[Dict[str, Any]]:
        """Retrieve the list of available properties for companies.

        Returns:
            List[Dict[str, Any]]: List of company property dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/properties/companies"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deal_properties(self) -> List[Dict[str, Any]]:
        """Retrieve the list of available properties for deals.

        Returns:
            List[Dict[str, Any]]: List of deal property dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/properties/deals"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal in HubSpot.

        Args:
            deal_data: Dictionary containing deal properties

        Returns:
            Dict[str, Any]: Created deal data

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
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
            Dict[str, Any]: The updated deal data

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"

        data = {"properties": properties}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

    async def get_engagements(
        self, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of engagements with optional filtering.

        Args:
            limit: Maximum number of engagements to retrieve
            filters: Optional search filters

        Returns:
            List[Dict[str, Any]]: List of engagement dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/engagements"

        params = {
            "limit": limit,
            "properties": "engagement_type,subject,createdate,lastmodifieddate",
        }

        if filters and "search" in filters:
            params["search"] = filters["search"]

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    # ------------------------------------------------------------------
    # Advanced search for deals
    # ------------------------------------------------------------------

    async def search_deals(
        self, *, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search deals using the CRM Search API.

        This method leverages the ``POST /crm/v3/objects/deals/search`` endpoint
        which supports advanced filtering. Currently the implementation supports
        simple *contains-token* queries on a subset of commonly-used deal
        properties. It can easily be extended with additional filters.

        Args:
            limit: Maximum number of deals to return (1-100). HubSpot caps page
                size to 100.
            filters: Optional dictionary with one or more of the following
                keys:

                * ``dealname`` – partial match on *dealname* using the
                  ``CONTAINS_TOKEN`` operator.
                * ``owner_id`` – exact match on *hubspot_owner_id*.
                * ``dealstage`` – exact match on *dealstage*.
                * ``pipeline`` – exact match on *pipeline*.

        Returns:
            A list of deal objects matching the criteria.
        """

        url = f"{self.base_url}/crm/v3/objects/deals/search"

        # Build filter groups based on provided filters ------------
        filter_groups: List[Dict[str, Any]] = []

        if filters is None:
            filters = {}

        # Mapping of allowed filters to property names/operators
        mapping = {
            "dealname": ("dealname", "CONTAINS_TOKEN"),
            "owner_id": ("hubspot_owner_id", "EQ"),
            "dealstage": ("dealstage", "EQ"),
            "pipeline": ("pipeline", "EQ"),
        }

        for key, value in filters.items():
            if key not in mapping:
                # Ignore unsupported filters silently to avoid HubSpot errors
                continue

            property_name, operator = mapping[key]
            filter_groups.append(
                {
                    "filters": [
                        {
                            "propertyName": property_name,
                            "operator": operator,
                            "value": value,
                        }
                    ]
                }
            )

        # If no filters specified default to return latest deals (similar to list)
        if not filter_groups:
            filter_groups.append(
                {"filters": [{"propertyName": "id", "operator": "GT", "value": 0}]}
            )

        search_body = {
            "filterGroups": filter_groups,
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
            "limit": min(limit, 100),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=search_body)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
