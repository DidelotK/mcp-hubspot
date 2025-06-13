"""Unit tests for HubSpotClient.search_deals."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyResponse:
    """Minimal mock of httpx.Response."""

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:  # noqa: D401
        self._data = data or {"results": []}
        self.status_code = 200

    def json(self) -> Dict[str, Any]:  # noqa: D401
        return self._data

    def raise_for_status(self) -> None:  # noqa: D401
        pass


class DummyAsyncClient:  # pylint: disable=too-few-public-methods
    """Mocked *async* httpx.AsyncClient capturing request payloads."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401, ANN401
        self.last_json: Optional[Dict[str, Any]] = None

    async def __aenter__(self) -> "DummyAsyncClient":  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401, ANN001, ANN201
        return False

    async def post(
        self, url: str, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        self.last_json = json
        return DummyResponse({"results": [{"id": "42"}]})


@pytest.mark.asyncio
async def test_search_deals_with_various_filters():
    """search_deals builds correct filter groups for supported keys."""

    dummy = DummyAsyncClient()

    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("test-key")
        filters = {
            "dealname": "renewal",
            "owner_id": "123",
            "dealstage": "contractsent",
            "pipeline": "enterprise",
            "unsupported": "ignored",  # should be ignored silently
        }
        results = await client.search_deals(limit=10, filters=filters)

        # Verify returned data shape
        assert results == [{"id": "42"}]

        # Inspect built request body
        body = dummy.last_json
        assert body is not None
        # 4 supported filters -> 4 filterGroups
        assert len(body["filterGroups"]) == 4
        # ensure operator types
        operators = {f["filters"][0]["operator"] for f in body["filterGroups"]}
        assert {"CONTAINS_TOKEN", "EQ"}.issubset(operators)


@pytest.mark.asyncio
async def test_search_deals_without_filters_defaults_to_id_gt_zero():
    """When no filters provided, a default id > 0 filter is sent."""

    dummy = DummyAsyncClient()

    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        _ = await client.search_deals()

        body = dummy.last_json
        assert body is not None
        assert len(body["filterGroups"]) == 1
        filt = body["filterGroups"][0]["filters"][0]
        assert filt == {"propertyName": "id", "operator": "GT", "value": 0}
