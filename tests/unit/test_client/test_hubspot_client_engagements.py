"""Unit tests for HubSpotClient.get_engagements."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient


@pytest.fixture
def client() -> HubSpotClient:
    """Return a HubSpot client instance for testing."""
    return HubSpotClient(api_key="dummy")


@pytest.mark.asyncio
async def test_get_engagements_success(client: HubSpotClient) -> None:
    """get_engagements should return parsed results on success."""
    sample_response: Dict[str, Any] = {
        "results": [
            {
                "id": "1",
                "properties": {
                    "engagement_type": "CALL",
                    "subject": "Follow-up",
                    "createdate": "2024-01-01T00:00:00.000Z",
                    "lastmodifieddate": "2024-01-02T00:00:00.000Z",
                },
            }
        ]
    }

    response_mock = Mock(spec=httpx.Response)
    response_mock.json.return_value = sample_response
    response_mock.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = response_mock

        engagements: List[Dict[str, Any]] = await client.get_engagements(limit=5)

        assert engagements == sample_response["results"]
        # Verify correct endpoint and params were used
        called_url = mock_get.call_args.args[0]
        called_params = mock_get.call_args.kwargs["params"]
        assert "/crm/v3/objects/engagements" in called_url
        assert called_params["limit"] == 5
        assert "properties" in called_params


@pytest.mark.asyncio
async def test_get_engagements_error(client: HubSpotClient) -> None:
    """get_engagements should raise the underlying HTTPStatusError."""
    err_response = httpx.Response(
        status_code=401, request=httpx.Request("GET", "https://api.hubapi.com")
    )
    http_error = httpx.HTTPStatusError(
        "401", request=err_response.request, response=err_response
    )

    response_mock = Mock(spec=httpx.Response)
    response_mock.raise_for_status.side_effect = http_error

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = response_mock

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_engagements()

        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_engagements_with_search_filter(client: HubSpotClient) -> None:
    """Ensure search filter is forwarded as query param."""
    response_mock = Mock(spec=httpx.Response)
    response_mock.json.return_value = {"results": []}
    response_mock.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = response_mock

        await client.get_engagements(limit=20, filters={"search": "call"})

        called_params = mock_get.call_args.kwargs["params"]
        assert called_params["search"] == "call"
        assert called_params["limit"] == 20
