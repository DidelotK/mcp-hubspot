"""Unit tests for the caching system in BaseTool."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.base import BaseTool
from hubspot_mcp.tools.contacts import ContactsTool


class TestCachingSystem:
    """Test the centralized caching system."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock(spec=HubSpotClient)
        client.api_key = "test-api-key"
        return client

    @pytest.fixture
    def contacts_tool(self, mock_client):
        """Create a contacts tool with mock client."""
        return ContactsTool(client=mock_client)

    def test_cache_key_generation(self, contacts_tool):
        """Test that cache keys are generated consistently."""
        key1 = contacts_tool._generate_cache_key("get_contacts", limit=10, after=None)
        key2 = contacts_tool._generate_cache_key("get_contacts", limit=10, after=None)
        key3 = contacts_tool._generate_cache_key("get_contacts", limit=20, after=None)

        # Same parameters should generate same key
        assert key1 == key2
        # Different parameters should generate different keys
        assert key1 != key3

    def test_cache_key_with_different_order(self, contacts_tool):
        """Test that cache keys are consistent regardless of parameter order."""
        key1 = contacts_tool._generate_cache_key(
            "get_contacts", limit=10, after="cursor123"
        )
        key2 = contacts_tool._generate_cache_key(
            "get_contacts", after="cursor123", limit=10
        )

        # Should be the same regardless of parameter order
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_cache_miss_and_hit(self, contacts_tool, mock_client):
        """Test cache miss followed by cache hit."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        # Mock the client method
        mock_data = [{"id": "1", "properties": {"email": "test@example.com"}}]
        mock_client.get_contacts = AsyncMock(return_value=mock_data)

        # First call should be a cache miss
        result1 = await contacts_tool._cached_client_call("get_contacts", limit=10)
        assert result1 == mock_data
        assert mock_client.get_contacts.call_count == 1

        # Second call with same parameters should be a cache hit
        result2 = await contacts_tool._cached_client_call("get_contacts", limit=10)
        assert result2 == mock_data
        assert mock_client.get_contacts.call_count == 1  # Should not increase

    @pytest.mark.asyncio
    async def test_cache_different_parameters(self, contacts_tool, mock_client):
        """Test that different parameters result in different cache entries."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        mock_data1 = [{"id": "1", "properties": {"email": "test1@example.com"}}]
        mock_data2 = [{"id": "2", "properties": {"email": "test2@example.com"}}]

        # Mock different responses for different calls
        mock_client.get_contacts = AsyncMock(side_effect=[mock_data1, mock_data2])

        # Two calls with different parameters
        result1 = await contacts_tool._cached_client_call("get_contacts", limit=10)
        result2 = await contacts_tool._cached_client_call("get_contacts", limit=20)

        assert result1 == mock_data1
        assert result2 == mock_data2
        assert mock_client.get_contacts.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_shared_across_tools(self, mock_client):
        """Test that cache is shared across different tool instances."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        # Create two different tool instances
        tool1 = ContactsTool(client=mock_client)
        tool2 = ContactsTool(client=mock_client)

        mock_data = [{"id": "1", "properties": {"email": "test@example.com"}}]
        mock_client.get_contacts = AsyncMock(return_value=mock_data)

        # First tool makes the call
        result1 = await tool1._cached_client_call("get_contacts", limit=10)
        assert result1 == mock_data
        assert mock_client.get_contacts.call_count == 1

        # Second tool should get cached result
        result2 = await tool2._cached_client_call("get_contacts", limit=10)
        assert result2 == mock_data
        assert mock_client.get_contacts.call_count == 1  # Should not increase

    def test_clear_cache(self, contacts_tool):
        """Test cache clearing functionality."""
        # Add something to cache
        BaseTool._cache["test_key"] = "test_value"
        assert len(BaseTool._cache) > 0

        # Clear cache
        BaseTool.clear_cache()
        assert len(BaseTool._cache) == 0

    def test_get_cache_info(self, contacts_tool):
        """Test cache info retrieval."""
        # Clear cache first
        BaseTool.clear_cache()

        # Add some test data
        BaseTool._cache["test_key1"] = "test_value1"
        BaseTool._cache["test_key2"] = "test_value2"

        info = BaseTool.get_cache_info()

        assert info["size"] == 2
        assert info["maxsize"] == 1000
        assert info["ttl"] == 300
        assert len(info["keys"]) <= 10  # Should show max 10 keys

    @pytest.mark.asyncio
    async def test_cache_with_api_key_isolation(self, mock_client):
        """Test that different API keys result in different cache entries."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        # Create clients with different API keys
        client1 = Mock(spec=HubSpotClient)
        client1.api_key = "api-key-1"
        client1.get_contacts = AsyncMock(return_value=[{"id": "1"}])

        client2 = Mock(spec=HubSpotClient)
        client2.api_key = "api-key-2"
        client2.get_contacts = AsyncMock(return_value=[{"id": "2"}])

        tool1 = ContactsTool(client=client1)
        tool2 = ContactsTool(client=client2)

        # Both tools make the same call but with different API keys
        result1 = await tool1._cached_client_call("get_contacts", limit=10)
        result2 = await tool2._cached_client_call("get_contacts", limit=10)

        # Should get different results and both clients should be called
        assert result1 == [{"id": "1"}]
        assert result2 == [{"id": "2"}]
        assert client1.get_contacts.call_count == 1
        assert client2.get_contacts.call_count == 1

    @pytest.mark.asyncio
    async def test_cache_error_handling(self, contacts_tool, mock_client):
        """Test that errors are not cached."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        # Mock client to raise an error
        mock_client.get_contacts = AsyncMock(side_effect=Exception("API Error"))

        # First call should raise an error
        with pytest.raises(Exception, match="API Error"):
            await contacts_tool._cached_client_call("get_contacts", limit=10)

        # Cache should be empty (errors are not cached)
        assert len(BaseTool._cache) == 0

        # Second call should also raise an error (not cached)
        with pytest.raises(Exception, match="API Error"):
            await contacts_tool._cached_client_call("get_contacts", limit=10)

        # Client should be called twice (no caching of errors)
        assert mock_client.get_contacts.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_ttl_behavior(self, contacts_tool, mock_client):
        """Test that cache respects TTL (time-to-live)."""
        # This test would require mocking time, but we can at least test
        # that the TTL is set correctly in the cache configuration
        cache_info = BaseTool.get_cache_info()
        assert cache_info["ttl"] == 300  # 5 minutes

    @pytest.mark.asyncio
    async def test_full_tool_execution_with_cache(self, contacts_tool, mock_client):
        """Test full tool execution using the cache system."""
        # Clear cache to ensure clean state
        BaseTool.clear_cache()

        mock_data = [
            {
                "id": "1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john@example.com",
                },
            }
        ]
        mock_client.get_contacts = AsyncMock(return_value=mock_data)

        # First execution
        result1 = await contacts_tool.execute({"limit": 10})
        assert len(result1) == 1
        assert "John Doe" in result1[0].text
        assert mock_client.get_contacts.call_count == 1

        # Second execution with same parameters should use cache
        result2 = await contacts_tool.execute({"limit": 10})
        assert len(result2) == 1
        assert "John Doe" in result2[0].text
        assert mock_client.get_contacts.call_count == 1  # Should not increase
