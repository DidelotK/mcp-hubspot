"""Tests exercising *properties* list in ContactsTool & CompaniesTool.

These scenarios verify that the optional *properties* array is forwarded
as *extra_properties* to the underlying HubSpotClient method so that the
conditional branch in ``execute`` is executed (was previously
uncovered – line #52).
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

import mcp.types as types
import pytest

from hubspot_mcp.tools import CompaniesTool, ContactsTool


@pytest.mark.asyncio
async def test_contacts_tool_passes_extra_properties():  # noqa: D401
    """`properties` argument must be forwarded to client as extra_properties."""

    # Arrange -----------------------------------------------------------------
    mock_client = Mock()
    mock_client.get_contacts = AsyncMock(return_value=[])  # type: ignore[attr-defined]

    tool = ContactsTool(client=mock_client)

    # Act ---------------------------------------------------------------------
    result: List[types.TextContent] = await tool.execute(
        {"limit": 5, "properties": ["nickname"]}
    )

    # Assert ------------------------------------------------------------------
    # Branch executed -> mock called with the extra_properties kwarg
    mock_client.get_contacts.assert_awaited_once_with(  # type: ignore[attr-defined]
        limit=5, after=None, extra_properties=["nickname"]
    )
    # Validate result type for completeness
    assert len(result) == 1 and isinstance(result[0], types.TextContent)


@pytest.mark.asyncio
async def test_companies_tool_passes_extra_properties():  # noqa: D401
    """`properties` argument must be forwarded to client as extra_properties."""

    mock_client = Mock()
    mock_client.get_companies = AsyncMock(return_value=[])  # type: ignore[attr-defined]

    tool = CompaniesTool(client=mock_client)

    result: List[types.TextContent] = await tool.execute(
        {"limit": 3, "properties": ["numberofemployees"]}
    )

    mock_client.get_companies.assert_awaited_once_with(  # type: ignore[attr-defined]
        limit=3, after=None, extra_properties=["numberofemployees"]
    )
    assert len(result) == 1 and isinstance(result[0], types.TextContent)
