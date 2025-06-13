"""Integration tests for HubSpot API interactions.

These tests verify that the application correctly integrates with HubSpot API endpoints.
They use real API calls to staging/test environments or comprehensive mocks.
"""

from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.companies import CompaniesTool
from hubspot_mcp.tools.contacts import ContactsTool
from hubspot_mcp.tools.deals import DealsTool


class TestHubSpotAPIIntegration:
    """Integration tests for HubSpot API interactions."""

    @pytest.fixture
    def api_client(self, test_environment):
        """Create HubSpot client with test configuration."""
        return HubSpotClient(api_key=test_environment["HUBSPOT_ACCESS_TOKEN"])

    @pytest.mark.asyncio
    async def test_contacts_api_integration(self, api_client, mock_api_response):
        """Test integration between contacts tool and HubSpot API."""
        # Arrange
        mock_api_response["results"] = [
            {
                "id": "1",
                "properties": {
                    "email": "integration@test.com",
                    "firstname": "Integration",
                    "lastname": "Test",
                },
            }
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            response_mock = Mock(status_code=200)
            response_mock.json.return_value = mock_api_response
            response_mock.raise_for_status = Mock()
            mock_get.return_value = response_mock

            # Act
            contacts = await api_client.get_contacts(limit=10)

            # Assert
            assert len(contacts) == 1
            assert contacts[0]["properties"]["email"] == "integration@test.com"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_companies_api_integration(self, api_client, mock_api_response):
        """Test integration between companies tool and HubSpot API."""
        # Arrange
        mock_api_response["results"] = [
            {
                "id": "1",
                "properties": {"name": "Integration Corp", "domain": "integration.com"},
            }
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            response_mock = Mock(status_code=200)
            response_mock.json.return_value = mock_api_response
            response_mock.raise_for_status = Mock()
            mock_get.return_value = response_mock

            # Act
            companies = await api_client.get_companies(limit=10)

            # Assert
            assert len(companies) == 1
            assert companies[0]["properties"]["name"] == "Integration Corp"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_deals_api_integration(self, api_client, mock_api_response):
        """Test integration between deals tool and HubSpot API."""
        # Arrange
        mock_api_response["results"] = [
            {
                "id": "1",
                "properties": {
                    "dealname": "Integration Deal",
                    "amount": "5000",
                    "dealstage": "negotiation",
                },
            }
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            response_mock = Mock(status_code=200)
            response_mock.json.return_value = mock_api_response
            response_mock.raise_for_status = Mock()
            mock_get.return_value = response_mock

            # Act
            deals = await api_client.get_deals(limit=10)

            # Assert
            assert len(deals) == 1
            assert deals[0]["properties"]["dealname"] == "Integration Deal"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_error_handling_integration(self, api_client):
        """Test API error handling integration."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Mock API error response
            response_mock = Mock(status_code=401)
            response_mock.json.return_value = {
                "status": "error",
                "message": "This request is not authorized",
            }
            response_mock.raise_for_status = Mock(side_effect=Exception("401"))
            mock_get.return_value = response_mock

            # Act & Assert
            with pytest.raises(Exception):  # Should be specific exception type
                await api_client.get_contacts()

    @pytest.mark.asyncio
    async def test_pagination_integration(self, api_client):
        """Test API pagination handling integration."""
        # First page response
        first_page = {
            "results": [{"id": "1", "properties": {"email": "test1@example.com"}}],
            "paging": {"next": {"after": "cursor_123", "link": "?after=cursor_123"}},
        }

        # Second page response
        second_page = {
            "results": [{"id": "2", "properties": {"email": "test2@example.com"}}],
            "paging": {"next": None},
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            response_mock = Mock(status_code=200)
            response_mock.raise_for_status = Mock()
            response_mock.json.side_effect = [first_page, second_page]
            mock_get.return_value = response_mock

            # Act
            contacts = await api_client.get_contacts(limit=100)

            # Assert
            assert len(contacts) == 1
            assert contacts[0]["properties"]["email"] == "test1@example.com"
            # The current HubSpotClient implementation does not auto-fetch subsequent pages
            assert mock_get.call_count == 1  # Single API call


class TestToolAPIIntegration:
    """Integration tests between tools and API client."""

    @pytest.mark.asyncio
    async def test_contacts_tool_with_api_client(self, mock_hubspot_client):
        """Test contacts tool integration with API client."""
        # Arrange
        tool = ContactsTool(client=mock_hubspot_client)

        # Act
        result = await tool.execute({"limit": 5})

        # Assert
        assert len(result) == 1  # Should return formatted result
        mock_hubspot_client.get_contacts.assert_called_once_with(limit=5, filters={})

    @pytest.mark.asyncio
    async def test_companies_tool_with_api_client(self, mock_hubspot_client):
        """Test companies tool integration with API client."""
        # Arrange
        tool = CompaniesTool(client=mock_hubspot_client)

        # Act
        result = await tool.execute({"limit": 10})

        # Assert
        assert len(result) == 1  # Should return formatted result
        mock_hubspot_client.get_companies.assert_called_once_with(limit=10, filters={})

    @pytest.mark.asyncio
    async def test_deals_tool_with_api_client(self, mock_hubspot_client):
        """Test deals tool integration with API client."""
        # Arrange
        tool = DealsTool(client=mock_hubspot_client)

        # Act
        result = await tool.execute({"limit": 20})

        # Assert
        assert len(result) == 1  # Should return formatted result
        mock_hubspot_client.get_deals.assert_called_once_with(limit=20, after=None)
