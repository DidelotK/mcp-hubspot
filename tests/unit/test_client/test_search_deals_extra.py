"""Additional tests for HubSpotClient.search_deals to reach full coverage."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyResp:  # noqa: D401
    status_code = 200

    def json(self):  # noqa: D401
        return {"results": []}

    def raise_for_status(self):  # noqa: D401
        return None


class DummyAsyncClient:
    def __init__(self):
        self.body: Optional[Dict[str, Any]] = None

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401, ANN001, ANN201
        return False

    async def post(
        self, url: str, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        self.body = json
        return DummyResp()


@pytest.mark.asyncio
async def test_search_deals_defaults_and_deduplicates():  # noqa: D401
    """Calling search_deals without filters exercises default filter branch."""

    dummy = DummyAsyncClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        # Provide duplicate extra properties to hit dedup loop (line 649 approx)
        await client.search_deals(
            limit=9, extra_properties=["dealname", "amount", "dealname"]
        )

        body = dummy.body
        assert body is not None
        # Default filter group id > 0 exists
        assert body["filterGroups"][0]["filters"][0] == {
            "propertyName": "id",
            "operator": "GT",
            "value": 0,
        }
        # dealname should appear only once in properties list after deduplication
        props = body["properties"]
        assert props.count("dealname") == 1 and "amount" in props

    # Add more tests as needed
    # ...
