"""Additional tests for HubSpotClient to reach 100% coverage.

These tests specifically exercise code paths that were previously
uncovered (lines 65, 123, 181, 379, 490) by providing both an *after*
parameter and *extra_properties* lists. Instead of relying on real HTTP
calls, an in-memory dummy ``httpx.AsyncClient`` is injected which records
request parameters for later inspection.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import patch

import httpx
import pytest

from hubspot_mcp.client import HubSpotClient


class DummyAsyncClient:  # pylint: disable=too-few-public-methods
    """Minimal async replacement for *httpx.AsyncClient*.

    It captures the *params* or *json* payload supplied for assertion and
    returns a generic OK response body.
    """

    def __init__(self):
        self.last_params: Optional[Dict[str, Any]] = None
        self.last_json: Optional[Dict[str, Any]] = None

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401, ANN001, ANN201
        return False

    async def get(
        self, url: str, *, headers: Dict[str, str], params: Dict[str, Any]
    ):  # noqa: D401
        # Record query params for later verification
        self.last_params = params
        return _dummy_response()

    async def post(
        self, url: str, *, headers: Dict[str, str], json: Dict[str, Any]
    ):  # noqa: D401
        # Record JSON payload for later verification
        self.last_json = json
        return _dummy_response()


class _dummy_response:  # pylint: disable=too-few-public-methods
    """Very small stub that mimics *httpx.Response* relevant bits."""

    status_code: int = 200

    def json(self):  # noqa: D401
        return {"results": []}

    def raise_for_status(self):  # noqa: D401
        return None


@pytest.fixture()
def client() -> HubSpotClient:  # noqa: D401
    """Return a HubSpotClient instance bound to a fake API key."""

    return HubSpotClient("key")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,extra",
    [
        ("get_contacts", ["nickname"]),
        ("get_companies", ["numberofemployees"]),
        ("get_deals", ["custom_field"]),
        ("get_engagements", ["metadata"]),
    ],
)
async def test_list_methods_support_after_and_extra_properties(
    client, method: str, extra: List[str]
):  # noqa: D401
    """Each *list* method should honour *after* and *extra_properties*."""

    dummy = DummyAsyncClient()

    with patch.object(httpx, "AsyncClient", return_value=dummy):
        # Dynamically call the required method
        func = getattr(client, method)
        await func(limit=5, after="cursor-123", extra_properties=extra)

        # Ensure the dummy captured query params
        assert dummy.last_params is not None
        # *after* must be propagated
        assert dummy.last_params["after"] == "cursor-123"
        # All extra properties must be present in the *properties* CSV field
        for prop in extra:
            assert prop in dummy.last_params["properties"].split(",")


@pytest.mark.asyncio
async def test_search_deals_includes_extra_properties_and_deduplicates(
    client,
):  # noqa: D401
    """search_deals must merge & deduplicate the *extra_properties* list."""

    dummy = DummyAsyncClient()

    with patch.object(httpx, "AsyncClient", return_value=dummy):
        await client.search_deals(
            limit=10,
            filters={"dealname": "test"},
            extra_properties=["dealname", "foo", "bar"],
        )

        # JSON body should have been captured
        assert dummy.last_json is not None
        props: List[str] = dummy.last_json["properties"]
        # *dealname* should appear only once after de-duplication
        assert props.count("dealname") == 1
        # Extra props included
        for prop in ("foo", "bar"):
            assert prop in props
