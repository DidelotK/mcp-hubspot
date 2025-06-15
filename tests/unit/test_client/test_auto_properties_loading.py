"""Tests for automatic properties loading functionality in HubSpot client."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient


class TestAutoPropertiesLoading:
    """Test cases for automatic properties loading in HubSpot client."""

    @pytest.fixture
    def sample_contact_properties(self) -> List[Dict[str, Any]]:
        """Sample contact properties data."""
        return [
            {"name": "firstname", "type": "string", "fieldType": "text"},
            {"name": "lastname", "type": "string", "fieldType": "text"},
            {"name": "email", "type": "string", "fieldType": "text"},
            {"name": "phone", "type": "string", "fieldType": "text"},
            {"name": "jobtitle", "type": "string", "fieldType": "text"},
            {"name": "company", "type": "string", "fieldType": "text"},
            {"name": "website", "type": "string", "fieldType": "text"},
            {"name": "lifecyclestage", "type": "enumeration", "fieldType": "select"},
            {
                "name": "hs_calculated_phone_number",
                "type": "string",
                "fieldType": "calculated",
            },  # Should be excluded
            {
                "name": "hs_all_owner_ids",
                "type": "string",
                "fieldType": "calculated",
            },  # Should be excluded
            {"name": "createdate", "type": "datetime", "fieldType": "date"},
            {"name": "lastmodifieddate", "type": "datetime", "fieldType": "date"},
        ]

    @pytest.fixture
    def sample_company_properties(self) -> List[Dict[str, Any]]:
        """Sample company properties data."""
        return [
            {"name": "name", "type": "string", "fieldType": "text"},
            {"name": "domain", "type": "string", "fieldType": "text"},
            {"name": "industry", "type": "enumeration", "fieldType": "select"},
            {"name": "city", "type": "string", "fieldType": "text"},
            {"name": "state", "type": "string", "fieldType": "text"},
            {"name": "country", "type": "string", "fieldType": "text"},
            {"name": "numberofemployees", "type": "number", "fieldType": "number"},
            {"name": "annualrevenue", "type": "number", "fieldType": "number"},
            {
                "name": "hs_calculated_revenue",
                "type": "number",
                "fieldType": "calculated",
            },  # Should be excluded
            {"name": "createdate", "type": "datetime", "fieldType": "date"},
            {"name": "lastmodifieddate", "type": "datetime", "fieldType": "date"},
        ]

    @pytest.fixture
    def sample_deal_properties(self) -> List[Dict[str, Any]]:
        """Sample deal properties data."""
        return [
            {"name": "dealname", "type": "string", "fieldType": "text"},
            {"name": "amount", "type": "number", "fieldType": "number"},
            {"name": "dealstage", "type": "enumeration", "fieldType": "select"},
            {"name": "pipeline", "type": "enumeration", "fieldType": "select"},
            {"name": "closedate", "type": "datetime", "fieldType": "date"},
            {"name": "probability", "type": "number", "fieldType": "number"},
            {
                "name": "deal_currency_code",
                "type": "enumeration",
                "fieldType": "select",
            },
            {
                "name": "hs_analytics_source",
                "type": "string",
                "fieldType": "calculated",
            },  # Should be excluded
            {"name": "createdate", "type": "datetime", "fieldType": "date"},
            {"name": "lastmodifieddate", "type": "datetime", "fieldType": "date"},
        ]

    @pytest.fixture
    def client_with_auto_loading(self) -> HubSpotClient:
        """Create a client with auto-loading enabled."""
        return HubSpotClient("test-api-key", auto_load_properties=True)

    @pytest.fixture
    def client_without_auto_loading(self) -> HubSpotClient:
        """Create a client with auto-loading disabled."""
        return HubSpotClient("test-api-key", auto_load_properties=False)

    @pytest.mark.asyncio
    async def test_contacts_auto_loading_enabled(
        self, client_with_auto_loading, sample_contact_properties
    ):
        """Test contacts retrieval with auto-loading enabled."""
        expected_properties = [
            "firstname",
            "lastname",
            "email",
            "phone",
            "jobtitle",
            "company",
            "website",
            "lifecyclestage",
            "createdate",
            "lastmodifieddate",
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API call
            properties_response = Mock()
            properties_response.json.return_value = {
                "results": sample_contact_properties
            }
            properties_response.raise_for_status = Mock()

            # Mock contacts API call
            contacts_response = Mock()
            contacts_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            contacts_response.raise_for_status = Mock()

            # Configure mock to return different responses for different URLs
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/contacts" in url:
                    return properties_response
                else:
                    return contacts_response

            mock_get.side_effect = side_effect

            # Call get_contacts
            result = await client_with_auto_loading.get_contacts(limit=10)

            # Verify properties API was called
            properties_calls = [
                call
                for call in mock_get.call_args_list
                if "properties/contacts" in str(call)
            ]
            assert len(properties_calls) == 1

            # Verify contacts API was called with all properties
            contacts_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/contacts" in str(call)
            ]
            assert len(contacts_calls) == 1

            # Extract the properties parameter from the call
            contacts_call_kwargs = contacts_calls[0].kwargs
            properties_param = contacts_call_kwargs.get("params", {}).get(
                "properties", ""
            )
            properties_list = properties_param.split(",")

            # Verify all expected properties are included
            for prop in expected_properties:
                assert prop in properties_list

            # Verify excluded properties are not included
            assert "hs_calculated_phone_number" not in properties_list
            assert "hs_all_owner_ids" not in properties_list

    @pytest.mark.asyncio
    async def test_contacts_auto_loading_disabled(self, client_without_auto_loading):
        """Test contacts retrieval with auto-loading disabled."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            contacts_response = Mock()
            contacts_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            contacts_response.raise_for_status = Mock()
            mock_get.return_value = contacts_response

            # Call get_contacts
            result = await client_without_auto_loading.get_contacts(limit=10)

            # Verify properties API was NOT called
            properties_calls = [
                call
                for call in mock_get.call_args_list
                if "properties/contacts" in str(call)
            ]
            assert len(properties_calls) == 0

            # Verify only default properties are used
            contacts_call_kwargs = mock_get.call_args.kwargs
            properties_param = contacts_call_kwargs.get("params", {}).get(
                "properties", ""
            )
            properties_list = properties_param.split(",")

            expected_default = [
                "firstname",
                "lastname",
                "email",
                "company",
                "phone",
                "createdate",
                "lastmodifieddate",
            ]
            assert len(properties_list) == len(expected_default)
            for prop in expected_default:
                assert prop in properties_list

    @pytest.mark.asyncio
    async def test_companies_auto_loading_enabled(
        self, client_with_auto_loading, sample_company_properties
    ):
        """Test companies retrieval with auto-loading enabled."""
        expected_properties = [
            "name",
            "domain",
            "industry",
            "city",
            "state",
            "country",
            "numberofemployees",
            "annualrevenue",
            "createdate",
            "lastmodifieddate",
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API call
            properties_response = Mock()
            properties_response.json.return_value = {
                "results": sample_company_properties
            }
            properties_response.raise_for_status = Mock()

            # Mock companies API call
            companies_response = Mock()
            companies_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            companies_response.raise_for_status = Mock()

            # Configure mock responses
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/companies" in url:
                    return properties_response
                else:
                    return companies_response

            mock_get.side_effect = side_effect

            # Call get_companies
            result = await client_with_auto_loading.get_companies(limit=10)

            # Verify properties API was called
            properties_calls = [
                call
                for call in mock_get.call_args_list
                if "properties/companies" in str(call)
            ]
            assert len(properties_calls) == 1

            # Verify companies API was called with all properties
            companies_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/companies" in str(call)
            ]
            assert len(companies_calls) == 1

            # Extract and verify properties
            companies_call_kwargs = companies_calls[0].kwargs
            properties_param = companies_call_kwargs.get("params", {}).get(
                "properties", ""
            )
            properties_list = properties_param.split(",")

            for prop in expected_properties:
                assert prop in properties_list

            # Verify excluded properties are not included
            assert "hs_calculated_revenue" not in properties_list

    @pytest.mark.asyncio
    async def test_deals_auto_loading_enabled(
        self, client_with_auto_loading, sample_deal_properties
    ):
        """Test deals retrieval with auto-loading enabled."""
        expected_properties = [
            "dealname",
            "amount",
            "dealstage",
            "pipeline",
            "closedate",
            "probability",
            "deal_currency_code",
            "createdate",
            "lastmodifieddate",
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API call
            properties_response = Mock()
            properties_response.json.return_value = {"results": sample_deal_properties}
            properties_response.raise_for_status = Mock()

            # Mock deals API call
            deals_response = Mock()
            deals_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            deals_response.raise_for_status = Mock()

            # Configure mock responses
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/deals" in url:
                    return properties_response
                else:
                    return deals_response

            mock_get.side_effect = side_effect

            # Call get_deals
            result = await client_with_auto_loading.get_deals(limit=10)

            # Verify properties API was called
            properties_calls = [
                call
                for call in mock_get.call_args_list
                if "properties/deals" in str(call)
            ]
            assert len(properties_calls) == 1

            # Verify deals API was called with all properties
            deals_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/deals" in str(call)
            ]
            assert len(deals_calls) == 1

            # Extract and verify properties
            deals_call_kwargs = deals_calls[0].kwargs
            properties_param = deals_call_kwargs.get("params", {}).get("properties", "")
            properties_list = properties_param.split(",")

            for prop in expected_properties:
                assert prop in properties_list

            # Verify excluded properties are not included
            assert "hs_analytics_source" not in properties_list

    @pytest.mark.asyncio
    async def test_properties_caching(
        self, client_with_auto_loading, sample_contact_properties
    ):
        """Test that properties are cached and not fetched multiple times."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API call
            properties_response = Mock()
            properties_response.json.return_value = {
                "results": sample_contact_properties
            }
            properties_response.raise_for_status = Mock()

            # Mock contacts API call
            contacts_response = Mock()
            contacts_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            contacts_response.raise_for_status = Mock()

            # Configure mock responses
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/contacts" in url:
                    return properties_response
                else:
                    return contacts_response

            mock_get.side_effect = side_effect

            # Call get_contacts twice
            result1 = await client_with_auto_loading.get_contacts(limit=10)
            result2 = await client_with_auto_loading.get_contacts(limit=5)

            # Verify properties API was called only once (cached)
            properties_calls = [
                call
                for call in mock_get.call_args_list
                if "properties/contacts" in str(call)
            ]
            assert len(properties_calls) == 1

            # Verify contacts API was called twice
            contacts_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/contacts" in str(call)
            ]
            assert len(contacts_calls) == 2

    @pytest.mark.asyncio
    async def test_extra_properties_merged_with_auto_loaded(
        self, client_with_auto_loading, sample_contact_properties
    ):
        """Test that extra properties are merged with auto-loaded properties."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API call
            properties_response = Mock()
            properties_response.json.return_value = {
                "results": sample_contact_properties
            }
            properties_response.raise_for_status = Mock()

            # Mock contacts API call
            contacts_response = Mock()
            contacts_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            contacts_response.raise_for_status = Mock()

            # Configure mock responses
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/contacts" in url:
                    return properties_response
                else:
                    return contacts_response

            mock_get.side_effect = side_effect

            # Call get_contacts with extra properties
            extra_props = ["custom_field_1", "custom_field_2"]
            result = await client_with_auto_loading.get_contacts(
                limit=10, extra_properties=extra_props
            )

            # Verify contacts API was called with merged properties
            contacts_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/contacts" in str(call)
            ]
            assert len(contacts_calls) == 1

            contacts_call_kwargs = contacts_calls[0].kwargs
            properties_param = contacts_call_kwargs.get("params", {}).get(
                "properties", ""
            )
            properties_list = properties_param.split(",")

            # Verify extra properties are included
            for prop in extra_props:
                assert prop in properties_list

            # Verify auto-loaded properties are also included
            assert "jobtitle" in properties_list  # From auto-loaded properties
            assert "website" in properties_list  # From auto-loaded properties

    @pytest.mark.asyncio
    async def test_search_methods_use_auto_loading(
        self, client_with_auto_loading, sample_deal_properties
    ):
        """Test that search methods also use auto-loading."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
                # Mock properties API call
                properties_response = Mock()
                properties_response.json.return_value = {
                    "results": sample_deal_properties
                }
                properties_response.raise_for_status = Mock()
                mock_get.return_value = properties_response

                # Mock search API call
                search_response = Mock()
                search_response.json.return_value = {
                    "results": [{"id": "1", "properties": {}}]
                }
                search_response.raise_for_status = Mock()
                mock_post.return_value = search_response

                # Call search_deals
                result = await client_with_auto_loading.search_deals(
                    filters={"dealname": "test deal"}
                )

                # Verify properties API was called
                assert mock_get.called

                # Verify search API was called with auto-loaded properties
                assert mock_post.called
                search_call_kwargs = mock_post.call_args.kwargs
                search_body = search_call_kwargs.get("json", {})
                properties_list = search_body.get("properties", [])

                # Verify auto-loaded properties are included
                assert "probability" in properties_list  # From auto-loaded
                assert "deal_currency_code" in properties_list  # From auto-loaded

                # Verify excluded properties are not included
                assert "hs_analytics_source" not in properties_list

    @pytest.mark.asyncio
    async def test_property_exclusion_logic(self, client_with_auto_loading):
        """Test the property exclusion logic."""
        # Test various property names that should be excluded
        test_cases = [
            ("hs_calculated_revenue", True),
            ("hs_all_owner_ids", True),
            ("hubspot_calculated_score", True),
            ("hs_analytics_source", True),
            ("hs_email_bounce", True),
            ("hs_social_linkedin_clicks", True),
            ("hs_sales_email_last_opened", True),
            ("hs_merged_object_ids", True),
            ("hs_unique_creation_key", True),
            ("hs_updated_by_user_id", True),
            ("normal_property", False),
            ("firstname", False),
            ("custom_field", False),
        ]

        for property_name, should_be_excluded in test_cases:
            result = client_with_auto_loading._is_excluded_property(
                property_name, "contacts"
            )
            assert (
                result == should_be_excluded
            ), f"Property {property_name} exclusion test failed"

    @pytest.mark.asyncio
    async def test_properties_loading_error_handling(self, client_with_auto_loading):
        """Test error handling during properties loading."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock properties API to raise an error
            properties_response = Mock()
            properties_response.raise_for_status.side_effect = Exception("API Error")

            # Mock contacts API call
            contacts_response = Mock()
            contacts_response.json.return_value = {
                "results": [{"id": "1", "properties": {}}]
            }
            contacts_response.raise_for_status = Mock()

            # Configure mock responses
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "properties/contacts" in url:
                    return properties_response
                else:
                    return contacts_response

            mock_get.side_effect = side_effect

            # Call get_contacts - should handle the error gracefully
            result = await client_with_auto_loading.get_contacts(limit=10)

            # Verify it still works with default properties
            contacts_calls = [
                call
                for call in mock_get.call_args_list
                if "crm/v3/objects/contacts" in str(call)
            ]
            assert len(contacts_calls) == 1

            contacts_call_kwargs = contacts_calls[0].kwargs
            properties_param = contacts_call_kwargs.get("params", {}).get(
                "properties", ""
            )
            properties_list = properties_param.split(",")

            # Should still include default properties
            default_props = [
                "firstname",
                "lastname",
                "email",
                "company",
                "phone",
                "createdate",
                "lastmodifieddate",
            ]
            for prop in default_props:
                assert prop in properties_list
