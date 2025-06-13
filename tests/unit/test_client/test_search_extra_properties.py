"""Extra edge-case tests to exercise duplicate handling in search_* methods."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyResp:  # noqa: D401
    def __init__(self):
        self.status_code = 200

    def json(self):  # noqa: D401
        return {"results": []}

    def raise_for_status(self):  # noqa: D401
        return None


class DummyClient:
    def __init__(self):
        self.payload: Optional[Dict[str, Any]] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(
        self, url: str, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        self.payload = json
        return DummyResp()


@pytest.mark.asyncio
async def test_search_contacts_deduplicates_extra_properties():  # noqa: D401
    dummy = DummyClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_contacts(
            filters={"firstname": "bob"},
            extra_properties=["email", "email", "phone"],
        )
        props = dummy.payload["properties"]  # type: ignore[index]
        # email should appear only once
        assert props.count("email") == 1 and "phone" in props


@pytest.mark.asyncio
async def test_search_companies_deduplicates_extra_properties():  # noqa: D401
    dummy = DummyClient()
    with patch.object(httpx, "AsyncClient", return_value=dummy):
        client = HubSpotClient("key")
        await client.search_companies(
            filters={"name": "acme"},
            extra_properties=["name", "domain", "domain"],
        )
        props = dummy.payload["properties"]  # type: ignore[index]
        assert props.count("domain") == 1 and "name" in props
