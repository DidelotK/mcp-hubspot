from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.hubspot_mcp.client.hubspot_client import HubSpotClient


@pytest.fixture
def client():
    """Create a HubSpot client instance for testing."""
    return HubSpotClient(api_key="test_api_key")


@pytest.mark.asyncio
async def test_get_contacts_success(client):
    """Test successful contact listing."""
    mock_response = {
        "results": [
            {
                "id": "123",
                "properties": {
                    "email": "test@example.com",
                    "firstname": "John",
                    "lastname": "Doe",
                    "company": "Test Corp",
                    "phone": "1234567890",
                },
            }
        ],
        "paging": {"next": {"after": "123"}},
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        contacts: List[Dict[str, Any]] = await client.get_contacts(limit=1)
        assert len(contacts) == 1
        assert contacts[0]["id"] == "123"
        assert contacts[0]["properties"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_contacts_error(client):
    """Test contact listing with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_contacts()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_companies_success(client):
    """Test successful company listing."""
    mock_response = {
        "results": [
            {
                "id": "456",
                "properties": {
                    "name": "Test Corp",
                    "domain": "testcorp.com",
                    "industry": "Technology",
                    "numberofemployees": "100",
                },
            }
        ],
        "paging": {"next": {"after": "456"}},
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        companies: List[Dict[str, Any]] = await client.get_companies(limit=1)
        assert len(companies) == 1
        assert companies[0]["id"] == "456"
        assert companies[0]["properties"]["name"] == "Test Corp"


@pytest.mark.asyncio
async def test_get_companies_error(client):
    """Test company listing with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_companies()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_deals_success(client):
    """Test successful deal listing."""
    mock_response = {
        "results": [
            {
                "id": "789",
                "properties": {
                    "dealname": "Test Deal",
                    "amount": "10000",
                    "dealstage": "appointmentscheduled",
                    "pipeline": "default",
                    "closedate": "2024-12-31",
                },
            }
        ],
        "paging": {"next": {"after": "789"}},
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        deals: List[Dict[str, Any]] = await client.get_deals(limit=1)
        assert len(deals) == 1
        assert deals[0]["id"] == "789"
        assert deals[0]["properties"]["dealname"] == "Test Deal"


@pytest.mark.asyncio
async def test_get_deals_error(client):
    """Test deal listing with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_deals()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_deal_success(client):
    """Test successful deal creation."""
    mock_response = {
        "id": "789",
        "properties": {
            "dealname": "New Deal",
            "amount": "10000",
            "dealstage": "appointmentscheduled",
            "pipeline": "default",
            "closedate": "2024-12-31",
        },
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 201
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        deal_data: Dict[str, Any] = {
            "dealname": "New Deal",
            "amount": "10000",
            "dealstage": "appointmentscheduled",
            "pipeline": "default",
            "closedate": "2024-12-31",
        }
        deal: Dict[str, Any] = await client.create_deal(deal_data)
        assert deal["id"] == "789"
        assert deal["properties"]["dealname"] == "New Deal"


@pytest.mark.asyncio
async def test_create_deal_error(client):
    """Test deal creation with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 400
    mock_response_obj.json.return_value = {"message": "Invalid deal properties"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "400 Bad Request",
        request=httpx.Request("POST", "http://test"),
        response=httpx.Response(400),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.create_deal({"dealname": "New Deal"})
        assert "400" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_deal_by_name_success(client):
    """Test successful deal retrieval by name."""
    mock_response = {
        "results": [
            {
                "id": "789",
                "properties": {
                    "dealname": "Test Deal",
                    "amount": "10000",
                    "dealstage": "appointmentscheduled",
                    "pipeline": "default",
                    "closedate": "2024-12-31",
                },
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        deal: Optional[Dict[str, Any]] = await client.get_deal_by_name("Test Deal")
        assert deal is not None
        assert deal["id"] == "789"
        assert deal["properties"]["dealname"] == "Test Deal"


@pytest.mark.asyncio
async def test_get_deal_by_name_not_found(client):
    """Test deal retrieval by name when not found."""
    mock_response = {"results": []}

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        deal: Optional[Dict[str, Any]] = await client.get_deal_by_name(
            "Non-existent Deal"
        )
        assert deal is None


@pytest.mark.asyncio
async def test_get_deal_by_name_error(client):
    """Test deal retrieval by name with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("POST", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_deal_by_name("Test Deal")
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_contact_properties_success(client):
    """Test successful contact properties retrieval."""
    mock_response = {
        "results": [
            {
                "name": "email",
                "label": "Email Address",
                "type": "string",
                "fieldType": "text",
                "description": "The contact's email address",
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        properties: List[Dict[str, Any]] = await client.get_contact_properties()
        assert len(properties) == 1
        assert properties[0]["name"] == "email"
        assert properties[0]["label"] == "Email Address"


@pytest.mark.asyncio
async def test_get_contact_properties_error(client):
    """Test contact properties retrieval with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_contact_properties()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_company_properties_success(client):
    """Test successful company properties retrieval."""
    mock_response = {
        "results": [
            {
                "name": "name",
                "label": "Company Name",
                "type": "string",
                "fieldType": "text",
                "description": "The company name",
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        properties: List[Dict[str, Any]] = await client.get_company_properties()
        assert len(properties) == 1
        assert properties[0]["name"] == "name"
        assert properties[0]["label"] == "Company Name"


@pytest.mark.asyncio
async def test_get_company_properties_error(client):
    """Test company properties retrieval with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_company_properties()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_deal_properties_success(client):
    """Test successful deal properties retrieval."""
    mock_response = {
        "results": [
            {
                "name": "dealname",
                "label": "Deal Name",
                "type": "string",
                "fieldType": "text",
                "description": "The name of the deal",
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        properties: List[Dict[str, Any]] = await client.get_deal_properties()
        assert len(properties) == 1
        assert properties[0]["name"] == "dealname"
        assert properties[0]["label"] == "Deal Name"


@pytest.mark.asyncio
async def test_get_deal_properties_error(client):
    """Test deal properties retrieval with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 401
    mock_response_obj.json.return_value = {"message": "Invalid API key"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=httpx.Request("GET", "http://test"),
        response=httpx.Response(401),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_deal_properties()
        assert "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_deal_success(client):
    """Test successful deal update."""
    mock_response = {
        "id": "789",
        "properties": {
            "dealname": "Updated Deal",
            "amount": "20000",
            "dealstage": "contractsent",
            "pipeline": "default",
            "closedate": "2024-12-31",
        },
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = mock_response

    with patch("httpx.AsyncClient.patch", new_callable=AsyncMock) as mock_patch:
        mock_patch.return_value = mock_response_obj

        properties: Dict[str, Any] = {
            "dealname": "Updated Deal",
            "amount": "20000",
            "dealstage": "contractsent",
        }
        updated_deal: Dict[str, Any] = await client.update_deal("789", properties)
        assert updated_deal["id"] == "789"
        assert updated_deal["properties"]["dealname"] == "Updated Deal"
        assert updated_deal["properties"]["amount"] == "20000"


@pytest.mark.asyncio
async def test_update_deal_error(client):
    """Test deal update with API error."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 400
    mock_response_obj.json.return_value = {"message": "Invalid deal properties"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "400 Bad Request",
        request=httpx.Request("PATCH", "http://test"),
        response=httpx.Response(400),
    )

    with patch("httpx.AsyncClient.patch", new_callable=AsyncMock) as mock_patch:
        mock_patch.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.update_deal("789", {"dealname": "Updated Deal"})
        assert "400" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_deal_not_found(client):
    """Test deal update when deal not found."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 404
    mock_response_obj.json.return_value = {"message": "Deal not found"}
    mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=httpx.Request("PATCH", "http://test"),
        response=httpx.Response(404),
    )

    with patch("httpx.AsyncClient.patch", new_callable=AsyncMock) as mock_patch:
        mock_patch.return_value = mock_response_obj

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.update_deal("999", {"dealname": "Updated Deal"})
        assert "404" in str(exc_info.value)
