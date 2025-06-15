"""Tests for HubSpot client pagination functionality."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


@pytest.fixture
def mock_hubspot_client():
    """Create a mock HubSpot client."""
    return HubSpotClient(api_key="test-api-key")


class TestPaginationMethods:
    """Test class for pagination-related methods."""

    @pytest.mark.asyncio
    async def test_get_all_contacts_with_pagination_single_page(
        self, mock_hubspot_client
    ):
        """Test get_all_contacts_with_pagination with single page of results."""
        mock_response_data = {
            "results": [
                {
                    "id": "1",
                    "properties": {
                        "firstname": "John",
                        "lastname": "Doe",
                        "email": "john@example.com",
                    },
                }
            ],
            "paging": {},  # No next page
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            assert len(result) == 1
            assert result[0]["id"] == "1"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_contacts_with_pagination_multiple_pages(
        self, mock_hubspot_client
    ):
        """Test get_all_contacts_with_pagination with multiple pages."""
        # First page response
        page1_response = {
            "results": [
                {"id": "1", "properties": {"firstname": "John"}},
                {"id": "2", "properties": {"firstname": "Jane"}},
            ],
            "paging": {"next": {"after": "cursor123"}},
        }

        # Second page response
        page2_response = {
            "results": [
                {"id": "3", "properties": {"firstname": "Bob"}},
                {"id": "4", "properties": {"firstname": "Alice"}},
            ],
            "paging": {},  # No next page
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.side_effect = [page1_response, page2_response]
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            assert len(result) == 4
            assert result[0]["id"] == "1"
            assert result[3]["id"] == "4"
            assert mock_get.call_count == 2

            # Verify second call includes the pagination cursor
            second_call_args = mock_get.call_args_list[1]
            assert "after" in second_call_args[1]["params"]
            assert second_call_args[1]["params"]["after"] == "cursor123"

    @pytest.mark.asyncio
    async def test_get_all_contacts_with_pagination_max_entities_limit(
        self, mock_hubspot_client
    ):
        """Test get_all_contacts_with_pagination with max_entities limit."""
        page1_response = {
            "results": [
                {"id": "1", "properties": {"firstname": "John"}},
                {"id": "2", "properties": {"firstname": "Jane"}},
                {"id": "3", "properties": {"firstname": "Bob"}},
            ],
            "paging": {"next": {"after": "cursor123"}},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = page1_response
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            # Limit to 2 entities
            result = await mock_hubspot_client.get_all_contacts_with_pagination(
                max_entities=2
            )

            assert len(result) == 2
            assert result[0]["id"] == "1"
            assert result[1]["id"] == "2"
            # Should only call once since we hit the limit
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_contacts_with_pagination_empty_results(
        self, mock_hubspot_client
    ):
        """Test get_all_contacts_with_pagination with empty results."""
        empty_response = {"results": [], "paging": {}}

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = empty_response
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            assert len(result) == 0
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_contacts_with_pagination_with_extra_properties(
        self, mock_hubspot_client
    ):
        """Test get_all_contacts_with_pagination with extra properties."""
        mock_response_data = {
            "results": [
                {
                    "id": "1",
                    "properties": {"firstname": "John", "custom_field": "value"},
                }
            ],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination(
                extra_properties=["custom_field", "another_field"]
            )

            assert len(result) == 1
            # Verify extra properties were passed to the API call
            call_args = mock_get.call_args
            properties_param = call_args[1]["params"]["properties"]
            assert "custom_field" in properties_param
            assert "another_field" in properties_param

    @pytest.mark.asyncio
    async def test_get_all_companies_with_pagination_single_page(
        self, mock_hubspot_client
    ):
        """Test get_all_companies_with_pagination with single page."""
        mock_response_data = {
            "results": [
                {
                    "id": "1",
                    "properties": {"name": "Company A", "domain": "companya.com"},
                },
                {
                    "id": "2",
                    "properties": {"name": "Company B", "domain": "companyb.com"},
                },
            ],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_companies_with_pagination()

            assert len(result) == 2
            assert result[0]["id"] == "1"
            assert result[1]["id"] == "2"

    @pytest.mark.asyncio
    async def test_get_all_companies_with_pagination_multiple_pages(
        self, mock_hubspot_client
    ):
        """Test get_all_companies_with_pagination with multiple pages."""
        page1_response = {
            "results": [
                {"id": "1", "properties": {"name": "Company A"}},
                {"id": "2", "properties": {"name": "Company B"}},
            ],
            "paging": {"next": {"after": "company_cursor"}},
        }

        page2_response = {
            "results": [
                {"id": "3", "properties": {"name": "Company C"}},
                {"id": "4", "properties": {"name": "Company D"}},
            ],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.side_effect = [page1_response, page2_response]
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_companies_with_pagination()

            assert len(result) == 4
            assert mock_get.call_count == 2

            # Verify pagination cursor was used
            second_call_args = mock_get.call_args_list[1]
            assert second_call_args[1]["params"]["after"] == "company_cursor"

    @pytest.mark.asyncio
    async def test_get_all_companies_with_pagination_max_entities_limit(
        self, mock_hubspot_client
    ):
        """Test get_all_companies_with_pagination with max_entities limit."""
        page_response = {
            "results": [
                {"id": "1", "properties": {"name": "Company A"}},
                {"id": "2", "properties": {"name": "Company B"}},
                {"id": "3", "properties": {"name": "Company C"}},
                {"id": "4", "properties": {"name": "Company D"}},
                {"id": "5", "properties": {"name": "Company E"}},
            ],
            "paging": {"next": {"after": "cursor"}},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = page_response
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            # Limit to 3 entities
            result = await mock_hubspot_client.get_all_companies_with_pagination(
                max_entities=3
            )

            assert len(result) == 3
            assert result[0]["id"] == "1"
            assert result[2]["id"] == "3"
            # Should only call once since we hit the limit
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_companies_with_pagination_empty_results(
        self, mock_hubspot_client
    ):
        """Test get_all_companies_with_pagination with empty results."""
        empty_response = {"results": [], "paging": {}}

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = empty_response
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_companies_with_pagination()

            assert len(result) == 0
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contacts_page_with_paging_basic(self, mock_hubspot_client):
        """Test _get_contacts_page_with_paging basic functionality."""
        mock_response_data = {
            "results": [{"id": "1", "properties": {"firstname": "John"}}],
            "paging": {"next": {"after": "cursor123"}},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client._get_contacts_page_with_paging(limit=50)

            assert result == mock_response_data
            mock_get.assert_called_once()

            # Verify the API call parameters
            call_args = mock_get.call_args
            assert call_args[1]["params"]["limit"] == 50
            assert "properties" in call_args[1]["params"]

    @pytest.mark.asyncio
    async def test_get_contacts_page_with_paging_with_after_cursor(
        self, mock_hubspot_client
    ):
        """Test _get_contacts_page_with_paging with after cursor."""
        mock_response_data = {
            "results": [{"id": "2", "properties": {"firstname": "Jane"}}],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client._get_contacts_page_with_paging(
                limit=25, after="test_cursor"
            )

            assert result == mock_response_data

            # Verify after cursor was included in the request
            call_args = mock_get.call_args
            assert call_args[1]["params"]["after"] == "test_cursor"

    @pytest.mark.asyncio
    async def test_get_contacts_page_with_paging_with_extra_properties(
        self, mock_hubspot_client
    ):
        """Test _get_contacts_page_with_paging with extra properties and deduplication."""
        mock_response_data = {
            "results": [
                {
                    "id": "1",
                    "properties": {"firstname": "John", "custom_field": "value"},
                }
            ],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            # Include duplicate properties to test deduplication
            result = await mock_hubspot_client._get_contacts_page_with_paging(
                extra_properties=[
                    "custom_field",
                    "firstname",
                    "another_field",
                    "firstname",
                ]
            )

            assert result == mock_response_data

            # Verify properties parameter and deduplication
            call_args = mock_get.call_args
            properties_param = call_args[1]["params"]["properties"]
            properties_list = properties_param.split(",")

            # Should include standard properties plus extra ones, deduplicated
            assert "firstname" in properties_list
            assert "custom_field" in properties_list
            assert "another_field" in properties_list
            # firstname should only appear once (deduplication test)
            assert properties_list.count("firstname") == 1

    @pytest.mark.asyncio
    async def test_get_companies_page_with_paging_basic(self, mock_hubspot_client):
        """Test _get_companies_page_with_paging basic functionality."""
        mock_response_data = {
            "results": [{"id": "1", "properties": {"name": "Company A"}}],
            "paging": {"next": {"after": "company_cursor"}},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client._get_companies_page_with_paging(limit=75)

            assert result == mock_response_data
            mock_get.assert_called_once()

            # Verify the API call parameters
            call_args = mock_get.call_args
            assert call_args[1]["params"]["limit"] == 75
            assert "properties" in call_args[1]["params"]

    @pytest.mark.asyncio
    async def test_get_companies_page_with_paging_with_after_cursor(
        self, mock_hubspot_client
    ):
        """Test _get_companies_page_with_paging with after cursor."""
        mock_response_data = {
            "results": [{"id": "2", "properties": {"name": "Company B"}}],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client._get_companies_page_with_paging(
                limit=50, after="company_test_cursor"
            )

            assert result == mock_response_data

            # Verify after cursor was included
            call_args = mock_get.call_args
            assert call_args[1]["params"]["after"] == "company_test_cursor"

    @pytest.mark.asyncio
    async def test_get_companies_page_with_paging_with_extra_properties(
        self, mock_hubspot_client
    ):
        """Test _get_companies_page_with_paging with extra properties and deduplication."""
        mock_response_data = {
            "results": [
                {"id": "1", "properties": {"name": "Company A", "industry": "Tech"}}
            ],
            "paging": {},
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response_data
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            # Include duplicate properties to test deduplication
            result = await mock_hubspot_client._get_companies_page_with_paging(
                extra_properties=["industry", "name", "custom_company_field", "name"]
            )

            assert result == mock_response_data

            # Verify properties parameter and deduplication
            call_args = mock_get.call_args
            properties_param = call_args[1]["params"]["properties"]
            properties_list = properties_param.split(",")

            # Should include standard properties plus extra ones, deduplicated
            assert "name" in properties_list
            assert "industry" in properties_list
            assert "custom_company_field" in properties_list
            # name should only appear once (deduplication test)
            assert properties_list.count("name") == 1

    @pytest.mark.asyncio
    async def test_pagination_error_handling(self, mock_hubspot_client):
        """Test error handling in pagination methods."""
        mock_response_obj = Mock()
        mock_response_obj.status_code = 500
        mock_response_obj.json.return_value = {"message": "Internal Server Error"}
        mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=httpx.Request("GET", "http://test"),
            response=httpx.Response(500),
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            with pytest.raises(httpx.HTTPStatusError):
                await mock_hubspot_client.get_all_contacts_with_pagination()

    @pytest.mark.asyncio
    async def test_pagination_missing_paging_info(self, mock_hubspot_client):
        """Test pagination when paging info is missing from response."""
        # Response without paging key
        response_without_paging = {
            "results": [{"id": "1", "properties": {"firstname": "John"}}]
            # No "paging" key
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = response_without_paging
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            # Should handle missing paging gracefully and return results
            assert len(result) == 1
            assert result[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_pagination_missing_next_info(self, mock_hubspot_client):
        """Test pagination when next page info is missing."""
        # Response with paging but no next key
        response_with_empty_paging = {
            "results": [{"id": "1", "properties": {"firstname": "John"}}],
            "paging": {
                # No "next" key
            },
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = response_with_empty_paging
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            # Should handle missing next info gracefully
            assert len(result) == 1
            assert result[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_pagination_missing_after_cursor(self, mock_hubspot_client):
        """Test pagination when after cursor is missing from next info."""
        # Response with paging.next but no after key
        response_missing_after = {
            "results": [{"id": "1", "properties": {"firstname": "John"}}],
            "paging": {
                "next": {
                    # No "after" key
                }
            },
        }

        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = response_missing_after
        mock_response_obj.raise_for_status = Mock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_obj

            result = await mock_hubspot_client.get_all_contacts_with_pagination()

            # Should handle missing after cursor gracefully and stop pagination
            assert len(result) == 1
            assert result[0]["id"] == "1"
