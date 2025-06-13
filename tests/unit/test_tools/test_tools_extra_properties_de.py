"""Tests to cover extra_properties branch in DealsTool & EngagementsTool."""

from __future__ import annotations

from typing import List
from unittest.mock import AsyncMock, Mock

import mcp.types as types
import pytest

from hubspot_mcp.tools import DealsTool, EngagementsTool


@pytest.mark.asyncio
async def test_deals_tool_passes_extra_properties():
    """`properties` array should be forwarded as extra_properties in DealsTool."""

    mock_client = Mock()
    mock_client.get_deals = AsyncMock(return_value=[])

    tool = DealsTool(client=mock_client)

    result: List[types.TextContent] = await tool.execute(
        {"limit": 7, "properties": ["foobar"]}
    )

    mock_client.get_deals.assert_awaited_once_with(  # type: ignore[attr-defined]
        limit=7, after=None, extra_properties=["foobar"]
    )
    assert len(result) == 1 and isinstance(result[0], types.TextContent)


@pytest.mark.asyncio
async def test_engagements_tool_passes_extra_properties():
    """`properties` array should be forwarded as extra_properties in EngagementsTool."""

    mock_client = Mock()
    mock_client.get_engagements = AsyncMock(return_value=[])

    tool = EngagementsTool(client=mock_client)

    result: List[types.TextContent] = await tool.execute(
        {"limit": 4, "properties": ["body"]}
    )

    mock_client.get_engagements.assert_awaited_once_with(  # type: ignore[attr-defined]
        limit=4, after=None, extra_properties=["body"]
    )
    assert len(result) == 1 and isinstance(result[0], types.TextContent)
