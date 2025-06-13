"""Extra tests to hit remaining uncovered lines in HubSpotClient search methods."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyResponse:  # noqa: D401
    def __init__(self):
        self.status_code = 200

    def json(self):  # noqa: D401
        return {"results": []}

    def raise_for_status(self):  # noqa: D401
        return None


class DummyAsyncClient:  # noqa: D401
    def __init__(self):
        self.last_json: Optional[Dict[str, Any]] = None

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
        return False

    async def post(
        self, url: str, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        self.last_json = json
        return DummyResponse()


@pytest.mark.asyncio
async def test_search_deals_with_duplicate_extra_properties():
    """Ensure deduplication logic executes when extra_properties repeats defaults."""

    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_deals(extra_properties=["dealname", "custom"])
        body = dummy.last_json
        assert body is not None
        # dedup -> dealname should appear once, custom present
        assert body["properties"].count("dealname") == 1
        assert "custom" in body["properties"]


@pytest.mark.asyncio
async def test_search_companies_multiple_filters_groups():
    """Providing several supported filters results in >1 filterGroups list."""

    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_companies(
            filters={"name": "A", "domain": "acme.com"}, extra_properties=["industry"]
        )
        body = dummy.last_json
        assert body is not None
        # Two supported filters -> 2 groups
        assert len(body["filterGroups"]) == 2
        assert "industry" in body["properties"]
