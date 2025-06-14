"""Extra edge-case tests to exercise duplicate handling in search_* methods."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, patch

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
async def test_search_contacts_deduplicates_extra_properties(monkeypatch):
    """Test that search_contacts deduplicates extra properties correctly."""
    dummy = DummyClient()
    monkeypatch.setattr("httpx.AsyncClient", lambda: dummy)

    client = HubSpotClient("key")
    # Provide duplicate extra properties to hit dedup loop (line 611 approx)
    await client.search_contacts(
        limit=9, extra_properties=["firstname", "email", "firstname"]
    )

    body = dummy.payload
    # Check that properties are deduplicated
    properties = body["properties"]
    assert "firstname" in properties
    assert "email" in properties
    # firstname should only appear once despite being in extra_properties twice
    assert properties.count("firstname") == 1


@pytest.mark.asyncio
async def test_search_companies_deduplicates_extra_properties(monkeypatch):
    """Test that search_companies deduplicates extra properties correctly."""
    dummy = DummyClient()
    monkeypatch.setattr("httpx.AsyncClient", lambda: dummy)

    client = HubSpotClient("key")
    # Provide duplicate extra properties to hit dedup loop (line 649 approx)
    await client.search_companies(limit=9, extra_properties=["name", "domain", "name"])

    body = dummy.payload
    # Check that properties are deduplicated
    properties = body["properties"]
    assert "name" in properties
    assert "domain" in properties
    # name should only appear once despite being in extra_properties twice
    assert properties.count("name") == 1
