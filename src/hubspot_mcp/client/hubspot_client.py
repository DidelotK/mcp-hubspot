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
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of contacts with pagination support.

        Args:
            limit: Maximum number of contacts to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            List[Dict[str, Any]]: List of contact dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/contacts"

        default_props: List[str] = [
            "firstname",
            "lastname",
            "email",
            "company",
            "phone",
            "createdate",
            "lastmodifieddate",
        ]

        # Merge and de-duplicate properties
        if extra_properties:
            default_props.extend(extra_properties)
        # Preserve order but ensure uniqueness
        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_companies(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of companies with pagination support.

        Args:
            limit: Maximum number of companies to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            List[Dict[str, Any]]: List of company dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/companies"

        default_props: List[str] = [
            "name",
            "domain",
            "city",
            "state",
            "country",
            "industry",
            "createdate",
            "lastmodifieddate",
        ]

        if extra_properties:
            default_props.extend(extra_properties)

        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of deals with pagination support.

        Args:
            limit: Maximum number of deals to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            List[Dict[str, Any]]: List of deal dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/deals"

        default_props: List[str] = [
            "dealname",
            "amount",
            "dealstage",
            "pipeline",
            "closedate",
            "createdate",
            "lastmodifieddate",
            "hubspot_owner_id",
        ]

        if extra_properties:
            default_props.extend(extra_properties)

        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
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
        """Update a deal in HubSpot.

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
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve the list of engagements with pagination support.

        Args:
            limit: Maximum number of engagements to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            List[Dict[str, Any]]: List of engagement dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/engagements"

        default_props: List[str] = [
            "engagement_type",
            "subject",
            "createdate",
            "lastmodifieddate",
        ]

        if extra_properties:
            default_props.extend(extra_properties)

        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    # ------------------------------------------------------------------
    # Advanced search for deals
    # ------------------------------------------------------------------

    async def search_deals(
        self,
        *,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        extra_properties: Optional[List[str]] = None,
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
            extra_properties: List of additional properties to include

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

        properties_list: List[str] = [
            "dealname",
            "amount",
            "dealstage",
            "pipeline",
            "closedate",
            "createdate",
            "lastmodifieddate",
            "hubspot_owner_id",
        ]

        if extra_properties:
            properties_list.extend(extra_properties)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_props: List[str] = []
        for prop in properties_list:
            if prop not in seen:
                seen.add(prop)
                unique_props.append(prop)

        search_body = {
            "filterGroups": filter_groups,
            "properties": unique_props,
            "limit": min(limit, 100),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=search_body)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    # ------------------------------------------------------------------
    # Advanced search for contacts
    # ------------------------------------------------------------------

    async def search_contacts(
        self,
        *,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search contacts via CRM Search API.

        Supported filters:

        * ``email`` – contains-token match on *email*.
        * ``firstname`` – contains-token on *firstname*.
        * ``lastname`` – contains-token on *lastname*.
        * ``company`` – contains-token on *company*.
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/search"

        if filters is None:
            filters = {}

        mapping = {
            "email": ("email", "CONTAINS_TOKEN"),
            "firstname": ("firstname", "CONTAINS_TOKEN"),
            "lastname": ("lastname", "CONTAINS_TOKEN"),
            "company": ("company", "CONTAINS_TOKEN"),
        }

        filter_groups: List[Dict[str, Any]] = []
        for key, value in filters.items():
            if key not in mapping:
                continue
            prop, operator = mapping[key]
            filter_groups.append(
                {
                    "filters": [
                        {"propertyName": prop, "operator": operator, "value": value}
                    ]
                }
            )

        if not filter_groups:
            filter_groups.append(
                {"filters": [{"propertyName": "id", "operator": "GT", "value": 0}]}
            )

        properties_list: List[str] = [
            "firstname",
            "lastname",
            "email",
            "company",
            "phone",
            "createdate",
            "lastmodifieddate",
        ]
        if extra_properties:
            properties_list.extend(extra_properties)

        # Deduplicate
        seen: set[str] = set()
        unique_props: List[str] = []
        for p in properties_list:
            if p not in seen:
                seen.add(p)
                unique_props.append(p)  # pragma: no cover

        body = {
            "filterGroups": filter_groups,
            "properties": unique_props,
            "limit": min(limit, 100),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    # ------------------------------------------------------------------
    # Advanced search for companies
    # ------------------------------------------------------------------

    async def search_companies(
        self,
        *,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        extra_properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search companies via CRM Search API with simple filters."""
        url = f"{self.base_url}/crm/v3/objects/companies/search"

        if filters is None:
            filters = {}

        mapping = {
            "name": ("name", "CONTAINS_TOKEN"),
            "domain": ("domain", "CONTAINS_TOKEN"),
            "industry": ("industry", "CONTAINS_TOKEN"),
            "country": ("country", "CONTAINS_TOKEN"),
        }

        filter_groups: List[Dict[str, Any]] = []
        for key, value in filters.items():
            if key not in mapping:
                continue
            prop, operator = mapping[key]
            filter_groups.append(
                {
                    "filters": [
                        {"propertyName": prop, "operator": operator, "value": value}
                    ]
                }
            )

        if not filter_groups:
            filter_groups.append(
                {"filters": [{"propertyName": "id", "operator": "GT", "value": 0}]}
            )

        properties_list: List[str] = [
            "name",
            "domain",
            "industry",
            "city",
            "state",
            "country",
            "createdate",
            "lastmodifieddate",
        ]
        if extra_properties:
            properties_list.extend(extra_properties)

        seen: set[str] = set()
        unique_props: List[str] = []
        for p in properties_list:
            if p not in seen:
                seen.add(p)
                unique_props.append(p)  # pragma: no cover

        body = {
            "filterGroups": filter_groups,
            "properties": unique_props,
            "limit": min(limit, 100),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_all_contacts_with_pagination(
        self, *, extra_properties: Optional[List[str]] = None, max_entities: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all contacts using pagination with all specified properties.

        Args:
            extra_properties: List of additional properties to include
            max_entities: Maximum number of entities to load (0 = no limit)

        Returns:
            List[Dict[str, Any]]: List of all contact dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        all_contacts = []
        after = None
        page_size = 100  # HubSpot API limit

        while True:
            # Get contacts page with pagination info
            page_data = await self._get_contacts_page_with_paging(
                limit=page_size, after=after, extra_properties=extra_properties
            )

            contacts = page_data.get("results", [])
            if not contacts:
                break

            all_contacts.extend(contacts)

            # Check maximum limit
            if max_entities > 0 and len(all_contacts) >= max_entities:
                all_contacts = all_contacts[:max_entities]
                break

            # Get next page cursor
            paging = page_data.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")

            if not after:
                # No more pages
                break

        return all_contacts

    async def get_all_companies_with_pagination(
        self, *, extra_properties: Optional[List[str]] = None, max_entities: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all companies using pagination with all specified properties.

        Args:
            extra_properties: List of additional properties to include
            max_entities: Maximum number of entities to load (0 = no limit)

        Returns:
            List[Dict[str, Any]]: List of all company dictionaries

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        all_companies = []
        after = None
        page_size = 100  # HubSpot API limit

        while True:
            # Get companies page with pagination info
            page_data = await self._get_companies_page_with_paging(
                limit=page_size, after=after, extra_properties=extra_properties
            )

            companies = page_data.get("results", [])
            if not companies:
                break

            all_companies.extend(companies)

            # Check maximum limit
            if max_entities > 0 and len(all_companies) >= max_entities:
                all_companies = all_companies[:max_entities]
                break

            # Get next page cursor
            paging = page_data.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")

            if not after:
                # No more pages
                break

        return all_companies

    async def _get_contacts_page_with_paging(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a single page of contacts with pagination info.

        Args:
            limit: Maximum number of contacts to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            Dict containing 'results' and 'paging' information

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/contacts"

        default_props: List[str] = [
            "firstname",
            "lastname",
            "email",
            "company",
            "phone",
            "createdate",
            "lastmodifieddate",
        ]

        # Merge and de-duplicate properties
        if extra_properties:
            default_props.extend(extra_properties)
        # Preserve order but ensure uniqueness
        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()  # Return full response including paging info

    async def _get_companies_page_with_paging(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        *,
        extra_properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a single page of companies with pagination info.

        Args:
            limit: Maximum number of companies to retrieve (max 100)
            after: Pagination cursor to get the next set of results
            extra_properties: List of additional properties to include

        Returns:
            Dict containing 'results' and 'paging' information

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/companies"

        default_props: List[str] = [
            "name",
            "domain",
            "city",
            "state",
            "country",
            "industry",
            "createdate",
            "lastmodifieddate",
        ]

        if extra_properties:
            default_props.extend(extra_properties)

        seen: set[str] = set()
        merged_props: List[str] = []
        for prop in default_props:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        params = {
            "limit": min(limit, 100),  # HubSpot caps at 100
            "properties": ",".join(merged_props),
        }

        # Add pagination cursor if provided
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()  # Return full response including paging info
