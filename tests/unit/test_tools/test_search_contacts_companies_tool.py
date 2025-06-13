"""Tests for SearchContactsTool and SearchCompaniesTool."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

import mcp.types as types
import pytest

from hubspot_mcp.tools import SearchCompaniesTool, SearchContactsTool


@pytest.mark.asyncio
async def test_search_contacts_tool_execute():
    mock_client = Mock()
    mock_client.search_contacts = AsyncMock(return_value=[])

    tool = SearchContactsTool(client=mock_client)
    result: List[types.TextContent] = await tool.execute({"filters": {"email": "foo"}})

    mock_client.search_contacts.assert_awaited_once()
    assert len(result) == 1 and isinstance(result[0], types.TextContent)


@pytest.mark.asyncio
async def test_search_companies_tool_execute():
    mock_client = Mock()
    mock_client.search_companies = AsyncMock(return_value=[])
    tool = SearchCompaniesTool(client=mock_client)
    result: List[types.TextContent] = await tool.execute({"filters": {"name": "bar"}})
    mock_client.search_companies.assert_awaited_once()
    assert len(result) == 1 and isinstance(result[0], types.TextContent)
