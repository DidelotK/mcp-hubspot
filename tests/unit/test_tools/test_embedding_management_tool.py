"""Unit tests for the EmbeddingManagementTool class."""

from unittest.mock import AsyncMock, Mock

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.embedding_management_tool import EmbeddingManagementTool


class TestEmbeddingManagementTool:
    """Test the EmbeddingManagementTool class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock(spec=HubSpotClient)
        client.api_key = "test-key"
        return client

    @pytest.fixture
    def tool(self, mock_client):
        """Create an EmbeddingManagementTool instance for testing."""
        return EmbeddingManagementTool(client=mock_client)

    def test_get_tool_definition(self, tool):
        """Test tool definition generation."""
        definition = tool.get_tool_definition()

        assert definition.name == "manage_hubspot_embeddings"
        assert "embedding indexes" in definition.description.lower()

        # Check schema structure
        schema = definition.inputSchema
        assert "action" in schema["properties"]
        assert "entity_types" in schema["properties"]
        assert "limit" in schema["properties"]

        # Check action enum values
        action_enum = schema["properties"]["action"]["enum"]
        assert "info" in action_enum
        assert "build" in action_enum
        assert "clear" in action_enum
        assert "rebuild" in action_enum

    @pytest.mark.asyncio
    async def test_execute_info_action_disabled(self, tool):
        """Test info action when embeddings are disabled."""
        # Mock disabled embeddings
        tool.get_embedding_stats = Mock(return_value={"enabled": False})

        result = await tool.execute({"action": "info"})

        assert len(result) == 1
        assert "Disabled" in result[0].text
        assert "embedding system is not currently enabled" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_info_action_enabled_no_entities(self, tool):
        """Test info action when embeddings are enabled but no entities indexed."""
        # Mock enabled but empty embeddings
        tool.get_embedding_stats = Mock(
            return_value={
                "enabled": True,
                "status": "ready",
                "total_entities": 0,
                "dimension": 384,
                "index_type": "flat",
                "model_name": "all-MiniLM-L6-v2",
                "cache_size": 0,
            }
        )

        result = await tool.execute({"action": "info"})

        assert len(result) == 1
        text = result[0].text
        assert "HubSpot Embedding System Information" in text
        assert "Status**: ready" in text
        assert "Total indexed entities: 0" in text
        assert "Available for Semantic Search**: No" in text
        assert "To start using semantic search" in text

    @pytest.mark.asyncio
    async def test_execute_info_action_enabled_with_entities(self, tool):
        """Test info action when embeddings are enabled with indexed entities."""
        # Mock enabled with entities
        tool.get_embedding_stats = Mock(
            return_value={
                "enabled": True,
                "status": "ready",
                "total_entities": 150,
                "dimension": 384,
                "index_type": "flat",
                "model_name": "all-MiniLM-L6-v2",
                "cache_size": 25,
            }
        )

        result = await tool.execute({"action": "info"})

        assert len(result) == 1
        text = result[0].text
        assert "HubSpot Embedding System Information" in text
        assert "Total indexed entities: 150" in text
        assert "Available for Semantic Search**: Yes" in text
        assert "Try semantic search" in text

    @pytest.mark.asyncio
    async def test_execute_build_action_disabled(self, tool):
        """Test build action when embeddings are disabled."""
        # Mock disabled embeddings
        tool.enable_embeddings = False

        result = await tool.execute({"action": "build", "entity_types": ["contacts"]})

        assert len(result) == 1
        assert "Embeddings Disabled" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_build_action_success(self, tool):
        """Test successful build action."""
        # Mock successful build
        tool.build_embedding_index = AsyncMock(
            return_value={
                "success": True,
                "entity_type": "contacts",
                "entities_indexed": 50,
                "index_stats": {"dimension": 384, "model_name": "all-MiniLM-L6-v2"},
            }
        )

        tool.get_embedding_stats = Mock(
            return_value={
                "enabled": True,
                "dimension": 384,
                "model_name": "all-MiniLM-L6-v2",
            }
        )

        result = await tool.execute(
            {"action": "build", "entity_types": ["contacts"], "limit": 100}
        )

        assert len(result) == 1
        text = result[0].text
        assert "Building Embedding Indexes" in text
        assert "Indexed 50 contacts" in text
        assert "Build Complete" in text
        assert "Total Entities Indexed**: 50" in text

    @pytest.mark.asyncio
    async def test_execute_build_action_multiple_entity_types(self, tool):
        """Test build action with multiple entity types."""

        # Mock builds for different entity types
        async def mock_build_index(entity_type, limit):
            if entity_type == "contacts":
                return {"success": True, "entities_indexed": 30}
            elif entity_type == "companies":
                return {"success": True, "entities_indexed": 20}
            else:
                return {"success": False, "error": "No data found"}

        tool.build_embedding_index = mock_build_index
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        result = await tool.execute(
            {"action": "build", "entity_types": ["contacts", "companies", "deals"]}
        )

        assert len(result) == 1
        text = result[0].text
        assert "Indexed 30 contacts" in text
        assert "Indexed 20 companies" in text
        assert "Failed:" in text  # For deals

    @pytest.mark.asyncio
    async def test_execute_build_action_with_error(self, tool):
        """Test build action when an error occurs."""
        # Mock build error
        tool.build_embedding_index = AsyncMock(side_effect=Exception("Build failed"))

        result = await tool.execute({"action": "build", "entity_types": ["contacts"]})

        assert len(result) == 1
        text = result[0].text
        assert "Error: Build failed" in text

    @pytest.mark.asyncio
    async def test_execute_rebuild_action(self, tool):
        """Test rebuild action."""
        # Mock clear and build operations
        tool.clear_embedding_cache = Mock()
        tool.build_embedding_index = AsyncMock(
            return_value={"success": True, "entities_indexed": 25}
        )
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        result = await tool.execute({"action": "rebuild", "entity_types": ["contacts"]})

        assert len(result) == 1
        text = result[0].text
        assert "Rebuilding Embedding Indexes" in text
        assert "Clearing existing indexes" in text
        assert "Building New Indexes" in text

        # Verify clear was called
        tool.clear_embedding_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_clear_action(self, tool):
        """Test clear action."""
        # Mock clear operation
        tool.clear_embedding_cache = Mock()

        result = await tool.execute({"action": "clear"})

        assert len(result) == 1
        text = result[0].text
        assert "Embedding Cache Cleared" in text
        assert "All embedding indexes and cache have been cleared" in text
        assert "Semantic search is no longer available" in text

        # Verify clear was called
        tool.clear_embedding_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_clear_action_with_error(self, tool):
        """Test clear action when an error occurs."""
        # Mock clear error
        tool.clear_embedding_cache = Mock(side_effect=Exception("Clear failed"))

        result = await tool.execute({"action": "clear"})

        assert len(result) == 1
        text = result[0].text
        assert "Error Clearing Embeddings" in text
        assert "Clear failed" in text

    @pytest.mark.asyncio
    async def test_execute_invalid_action(self, tool):
        """Test execution with invalid action."""
        result = await tool.execute({"action": "invalid"})

        assert len(result) == 1
        text = result[0].text
        assert "Invalid Action" in text
        assert "Unknown action: invalid" in text

    @pytest.mark.asyncio
    async def test_get_embedding_info_disabled(self, tool):
        """Test _get_embedding_info when disabled."""
        tool.get_embedding_stats = Mock(return_value={"enabled": False})

        result = await tool._get_embedding_info()

        assert "Status**: Disabled" in result
        assert "missing dependencies" in result

    @pytest.mark.asyncio
    async def test_build_indexes_success(self, tool):
        """Test _build_indexes with successful builds."""
        tool.build_embedding_index = AsyncMock(
            return_value={"success": True, "entities_indexed": 40}
        )
        tool.get_embedding_stats = Mock(
            return_value={"enabled": True, "dimension": 384, "model_name": "test-model"}
        )

        result = await tool._build_indexes(["contacts"], 100)

        assert "Building Embedding Indexes" in result
        assert "Indexed 40 contacts" in result
        assert "Total Entities Indexed**: 40" in result

    @pytest.mark.asyncio
    async def test_build_indexes_failure(self, tool):
        """Test _build_indexes with build failures."""
        tool.build_embedding_index = AsyncMock(
            return_value={"success": False, "error": "No data available"}
        )

        result = await tool._build_indexes(["contacts"], 100)

        assert "Failed: No data available" in result

    @pytest.mark.asyncio
    async def test_rebuild_indexes(self, tool):
        """Test _rebuild_indexes functionality."""
        tool.clear_embedding_cache = Mock()
        tool._build_indexes = AsyncMock(return_value="Build result")

        result = await tool._rebuild_indexes(["contacts"], 100)

        assert "Rebuilding Embedding Indexes" in result
        assert "Clearing existing indexes" in result
        assert "Build result" in result

        # Verify clear was called
        tool.clear_embedding_cache.assert_called_once()

    def test_clear_embeddings_success(self, tool):
        """Test _clear_embeddings successful operation."""
        tool.clear_embedding_cache = Mock()

        result = tool._clear_embeddings()

        assert "Embedding Cache Cleared" in result
        assert "All embedding indexes and cache have been cleared" in result

        # Verify clear was called
        tool.clear_embedding_cache.assert_called_once()

    def test_clear_embeddings_error(self, tool):
        """Test _clear_embeddings with error."""
        tool.clear_embedding_cache = Mock(side_effect=Exception("Clear error"))

        result = tool._clear_embeddings()

        assert "Error Clearing Embeddings" in result
        assert "Clear error" in result

    def test_format_build_summary(self, tool):
        """Test _format_build_summary functionality."""
        build_results = {
            "contacts": {"success": True, "entities_indexed": 50},
            "companies": {"success": True, "entities_indexed": 30},
            "deals": {"success": False, "error": "No data"},
        }

        summary = tool._format_build_summary(build_results)

        assert "Build Summary" in summary
        assert "Successful: 2/3" in summary
        assert "Failed: 1/3" in summary
        assert "Total entities indexed: 80" in summary

    @pytest.mark.asyncio
    async def test_execute_with_default_parameters(self, tool):
        """Test execution with default parameters."""
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Test info action (default)
        result = await tool.execute({})

        assert len(result) == 1
        # Should call info action by default
        assert "HubSpot Embedding System Information" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_with_exception(self, tool):
        """Test execution when an unexpected exception occurs."""
        # Mock an exception in get_embedding_stats
        tool.get_embedding_stats = Mock(side_effect=Exception("Unexpected error"))

        result = await tool.execute({"action": "info"})

        assert len(result) == 1
        # Should handle error through parent's handle_error method
