"""Tests for CacheManagementTool covering all branches."""

from unittest.mock import Mock

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.base import BaseTool
from hubspot_mcp.tools.cache_management_tool import CacheManagementTool


@pytest.fixture
def tool() -> CacheManagementTool:
    client = Mock(spec=HubSpotClient)
    client.api_key = "dummy-key"
    return CacheManagementTool(client=client)


@pytest.mark.asyncio
async def test_execute_info_with_data(tool: CacheManagementTool):
    """Ensure the `info` action returns formatted statistics with sample keys."""
    BaseTool.clear_cache()
    # populate cache with sample keys
    for idx in range(3):
        BaseTool._cache[f"k{idx}"] = f"v{idx}"

    result = await tool.execute({"action": "info"})
    text = result[0].text
    assert "HubSpot Cache Information" in text
    assert "Current size: 3" in text
    assert "Sample Cache Keys" in text


@pytest.mark.asyncio
async def test_execute_clear(tool: CacheManagementTool):
    """Ensure the `clear` action empties the cache and returns confirmation."""
    BaseTool.clear_cache()
    BaseTool._cache["temp"] = "value"
    assert len(BaseTool._cache) == 1
    result = await tool.execute({"action": "clear"})
    assert "Cache Cleared Successfully" in result[0].text
    assert len(BaseTool._cache) == 0


@pytest.mark.asyncio
async def test_execute_invalid_action(tool: CacheManagementTool):
    """Invalid action should return error message."""
    result = await tool.execute({"action": "unknown"})
    assert "Invalid Action" in result[0].text


def test_format_cache_info_empty(tool: CacheManagementTool):
    """Formatting on empty cache should mention empty keys."""
    info = {"size": 0, "maxsize": 1000, "ttl": 300, "keys": []}
    text = tool._format_cache_info(info)
    assert "None (cache is empty)" in text


def test_format_cache_info_with_data(tool: CacheManagementTool):
    """Test formatting of cache info with data."""
    cache_info = {
        "size": 5,
        "maxsize": 1000,
        "ttl": 300,
        "keys": ["key1", "key2", "key3", "key4", "key5"],
    }

    formatted = tool._format_cache_info(cache_info)

    assert "Current size: 5" in formatted
    assert "Cache utilization: 0.5%" in formatted
    assert "Sample Cache Keys" in formatted
    assert "key1" in formatted


@pytest.mark.asyncio
async def test_execute_handles_exception(tool: CacheManagementTool, monkeypatch):
    """Simulate unexpected error inside execute and ensure it's handled."""

    def boom(*args, **kwargs):  # type: ignore[return-value]
        raise RuntimeError("Unexpected boom")

    # Patch internal formatter to raise
    monkeypatch.setattr(tool, "_format_cache_info", boom)

    result = await tool.execute({"action": "info"})

    assert len(result) == 1
    assert "Unexpected error" in result[0].text
