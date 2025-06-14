"""Unit tests for HubSpotClient.search_contacts and search_companies."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyResponse:  # noqa: D401
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {"results": [{"id": "1"}]}
        self.status_code = 200

    def json(self):  # noqa: D401
        return self._data

    def raise_for_status(self):  # noqa: D401
        return None


class DummyAsyncClient:  # noqa: D401
    def __init__(self):
        self.last_json: Optional[Dict[str, Any]] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(
        self, url: str, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        self.last_json = json
        return DummyResponse()


@pytest.mark.asyncio
async def test_search_contacts_builds_correct_payload():
    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        filters = {"email": "alice", "unsupported": "ignored"}
        _ = await client.search_contacts(
            limit=5, filters=filters, extra_properties=["phone"]
        )

        body = dummy.last_json
        assert body is not None
        # ensure phone included once
        assert "phone" in body["properties"]
        # only one filter group for supported key
        assert len(body["filterGroups"]) == 1


@pytest.mark.asyncio
async def test_search_companies_builds_correct_payload():
    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        filters = {"name": "acme"}
        _ = await client.search_companies(limit=8, filters=filters)
        body = dummy.last_json
        assert body is not None and body["filterGroups"]
        filt = body["filterGroups"][0]["filters"][0]
        assert filt["propertyName"] == "name" and filt["operator"] == "CONTAINS_TOKEN"


# ---------------------------------------------------------------------------
# Additional tests to hit default-filter branches for 100 % coverage
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_contacts_defaults_to_id_gt_zero():
    """Calling *search_contacts* without filters should add id > 0 filter group."""

    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_contacts(limit=2)  # no filters

        body = dummy.last_json
        assert body is not None
        fg = body["filterGroups"]
        assert len(fg) == 1
        assert fg[0]["filters"][0] == {
            "propertyName": "id",
            "operator": "GT",
            "value": 0,
        }


@pytest.mark.asyncio
async def test_search_companies_defaults_to_id_gt_zero_on_unsupported_filter():
    """Unsupported filters should be ignored and default filter added."""

    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_companies(limit=3, filters={"unsupported": "x"})

        body = dummy.last_json
        assert body is not None
        assert len(body["filterGroups"]) == 1
        filt = body["filterGroups"][0]["filters"][0]
        assert filt["propertyName"] == "id" and filt["operator"] == "GT"
