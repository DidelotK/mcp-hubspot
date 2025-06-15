"""Client to interact with HubSpot API."""

import logging
from typing import Any, Dict, List, Optional, Set

import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client to interact with HubSpot API.

    This class provides methods to interact with the HubSpot API, including
    retrieving and managing contacts, companies, and deals with automatic
    property loading for enhanced data richness.
    """

    def __init__(self, api_key: str, *, auto_load_properties: bool = True):
        """Initialize the HubSpot client.

        Args:
            api_key: The HubSpot API key to use for authentication
            auto_load_properties: If True, automatically loads all available properties
                for each entity type to ensure maximum data richness
        """
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.auto_load_properties = auto_load_properties

        # Cache for all available properties by entity type
        self._properties_cache: Dict[str, List[str]] = {}
        self._properties_loaded: Set[str] = set()

    async def _get_all_properties_for_entity(self, entity_type: str) -> List[str]:
        """Get all available property names for a specific entity type.

        Args:
            entity_type: The entity type (contacts, companies, deals, engagements)

        Returns:
            List of all available property names for the entity type
        """
        if not self.auto_load_properties:
            return []

        if entity_type in self._properties_cache:
            return self._properties_cache[entity_type]

        try:
            if entity_type == "contacts":
                properties_data = await self.get_contact_properties()
            elif entity_type == "companies":
                properties_data = await self.get_company_properties()
            elif entity_type == "deals":
                properties_data = await self.get_deal_properties()
            elif entity_type == "engagements":
                # For engagements, we'll use a reasonable default set since
                # HubSpot engagements API has different property structure
                self._properties_cache[entity_type] = []
                return []
            else:
                logger.warning(
                    f"Unknown entity type for property loading: {entity_type}"
                )
                self._properties_cache[entity_type] = []
                return []

            # Extract property names, filtering out calculated/system properties that can't be requested
            property_names = []
            for prop in properties_data:
                name = prop.get("name", "")
                if name and not self._is_excluded_property(name, entity_type):
                    property_names.append(name)

            self._properties_cache[entity_type] = property_names
            self._properties_loaded.add(entity_type)

            logger.info(f"Loaded {len(property_names)} properties for {entity_type}")
            return property_names

        except Exception as e:
            logger.warning(f"Failed to load properties for {entity_type}: {e}")
            # Cache empty list to avoid repeated failures
            self._properties_cache[entity_type] = []
            return []

    def _is_excluded_property(self, property_name: str, entity_type: str) -> bool:
        """Check if a property should be excluded from automatic loading.

        Args:
            property_name: Name of the property to check
            entity_type: Type of entity (contacts, companies, deals)

        Returns:
            True if the property should be excluded
        """
        # Common exclusions across all entity types
        common_exclusions = {
            "hs_all_owner_ids",
            "hs_all_team_ids",
            "hs_all_accessible_team_ids",
            "hs_calculated_phone_number",
            "hs_calculated_phone_number_area_code",
            "hs_calculated_phone_number_country_code",
            "hs_calculated_phone_number_region_code",
            "hubspot_team_id",
            "hs_all_assigned_business_unit_ids",
        }

        if property_name in common_exclusions:
            return True

        # Properties that start with these prefixes are usually calculated
        calculated_prefixes = [
            "hs_calculated_",
            "hs_all_",
            "hubspot_calculated_",
            "hs_analytics_",
            "hs_email_",
            "hs_social_",
            "hs_sales_email_",
            "hs_merged_object_ids",
            "hs_unique_creation_key",
            "hs_updated_by_user_id",
        ]

        for prefix in calculated_prefixes:
            if property_name.startswith(prefix):
                return True

        return False

    async def _merge_properties(
        self,
        default_props: List[str],
        extra_properties: Optional[List[str]],
        entity_type: str,
    ) -> List[str]:
        """Merge default properties, auto-loaded properties, and extra properties.

        Args:
            default_props: Default properties for the entity type
            extra_properties: Additional properties requested by user
            entity_type: Type of entity (contacts, companies, deals)

        Returns:
            List of unique property names preserving order
        """
        all_properties = default_props.copy()

        # Add all available properties if auto-loading is enabled
        if self.auto_load_properties:
            available_properties = await self._get_all_properties_for_entity(
                entity_type
            )
            all_properties.extend(available_properties)

        # Add any extra properties requested
        if extra_properties:
            all_properties.extend(extra_properties)

        # Deduplicate while preserving order
        seen: Set[str] = set()
        merged_props: List[str] = []
        for prop in all_properties:
            if prop not in seen:
                seen.add(prop)
                merged_props.append(prop)

        return merged_props

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
            List[Dict[str, Any]]: List of contact dictionaries with all available
                properties automatically loaded (if auto_load_properties=True)

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(
            default_props, extra_properties, "contacts"
        )

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
            List[Dict[str, Any]]: List of company dictionaries with all available
                properties automatically loaded (if auto_load_properties=True)

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(
            default_props, extra_properties, "companies"
        )

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
            List[Dict[str, Any]]: List of deal dictionaries with all available
                properties automatically loaded (if auto_load_properties=True)

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(
            default_props, extra_properties, "deals"
        )

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
            Optional[Dict[str, Any]]: Deal dictionary with all available properties
                automatically loaded (if auto_load_properties=True), None if not found

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/crm/v3/objects/deals/search"

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(default_props, None, "deals")

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
            "properties": merged_props,
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
            List[Dict[str, Any]]: List of engagement dictionaries with default
                properties (engagements don't support auto-property loading)

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

        # For engagements, we don't use auto-loading as the API structure is different
        # Just use the traditional merging approach
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

        # Use the new property merging system that auto-loads all properties
        unique_props = await self._merge_properties(
            default_props, extra_properties, "deals"
        )

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

        default_props: List[str] = [
            "firstname",
            "lastname",
            "email",
            "company",
            "phone",
            "createdate",
            "lastmodifieddate",
        ]

        # Use the new property merging system that auto-loads all properties
        unique_props = await self._merge_properties(
            default_props, extra_properties, "contacts"
        )

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

        default_props: List[str] = [
            "name",
            "domain",
            "industry",
            "city",
            "state",
            "country",
            "createdate",
            "lastmodifieddate",
        ]

        # Use the new property merging system that auto-loads all properties
        unique_props = await self._merge_properties(
            default_props, extra_properties, "companies"
        )

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(
            default_props, extra_properties, "contacts"
        )

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
            Dict containing 'results' and 'paging' information with all available
                properties automatically loaded (if auto_load_properties=True)

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

        # Use the new property merging system that auto-loads all properties
        merged_props = await self._merge_properties(
            default_props, extra_properties, "companies"
        )

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
