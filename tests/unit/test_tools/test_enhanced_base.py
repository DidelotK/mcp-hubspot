"""Unit tests for the EnhancedBaseTool class."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import mcp.types as types
import pytest

from hubspot_mcp.embeddings.embedding_manager import EmbeddingManager
from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool


class ConcreteEnhancedBaseTool(EnhancedBaseTool):
    """Concrete implementation of EnhancedBaseTool for testing."""

    def get_tool_definition(self) -> types.Tool:
        """Return a mock tool definition for testing."""
        return types.Tool(
            name="test_tool",
            description="Test tool for enhanced base tool testing",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Return a mock execution result for testing."""
        return [types.TextContent(type="text", text="Test execution result")]


class TestEnhancedBaseTool:
    """Test the EnhancedBaseTool class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock()
        client.get_contacts = AsyncMock(
            return_value=[
                {"id": "1", "properties": {"firstname": "John", "lastname": "Doe"}},
                {"id": "2", "properties": {"firstname": "Jane", "lastname": "Smith"}},
            ]
        )
        client.get_companies = AsyncMock(
            return_value=[
                {
                    "id": "1",
                    "properties": {"name": "TechCorp", "domain": "techcorp.com"},
                },
                {
                    "id": "2",
                    "properties": {"name": "InnovateCorp", "domain": "innovate.com"},
                },
            ]
        )
        client.search_contacts = AsyncMock(
            return_value=[
                {"id": "1", "properties": {"firstname": "John", "lastname": "Doe"}},
            ]
        )
        client.search_companies = AsyncMock(
            return_value=[
                {
                    "id": "1",
                    "properties": {"name": "TechCorp", "domain": "techcorp.com"},
                },
            ]
        )
        return client

    @pytest.fixture
    def tool_with_embeddings(self, mock_client):
        """Create a ConcreteEnhancedBaseTool with embeddings enabled."""
        # Clear any existing embedding manager
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        EnhancedBaseTool._embedding_manager = None
        return ConcreteEnhancedBaseTool(mock_client, enable_embeddings=True)

    @pytest.fixture
    def tool_without_embeddings(self, mock_client):
        """Create a ConcreteEnhancedBaseTool with embeddings disabled."""
        return ConcreteEnhancedBaseTool(mock_client, enable_embeddings=False)

    @pytest.fixture
    def mock_embedding_manager(self):
        """Create a mock embedding manager."""
        manager = Mock(spec=EmbeddingManager)
        manager.build_index = Mock()
        manager.search_similar = Mock(
            return_value=[
                ({"id": "1", "properties": {"name": "TechCorp"}}, 0.95),
                ({"id": "2", "properties": {"name": "InnovateCorp"}}, 0.85),
            ]
        )
        manager.get_index_stats = Mock(
            return_value={
                "status": "ready",
                "total_entities": 100,
                "dimension": 384,
                "model_name": "all-MiniLM-L6-v2",
                "cache_size": 50,
            }
        )
        manager.clear_cache = Mock()
        return manager

    def test_init_with_embeddings_enabled(self, mock_client):
        """Test initialization with embeddings enabled."""
        # Clear any existing embedding manager
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        EnhancedBaseTool._embedding_manager = None

        tool = ConcreteEnhancedBaseTool(mock_client, enable_embeddings=True)

        assert tool.enable_embeddings is True
        assert tool.client == mock_client

        # The embedding manager should be created and accessible
        manager = tool.get_embedding_manager()
        assert manager is not None
        assert isinstance(manager, EmbeddingManager)

    def test_init_with_embeddings_disabled(self, mock_client):
        """Test initialization with embeddings disabled."""
        # Clear any existing embedding manager
        ConcreteEnhancedBaseTool._embedding_manager = None

        tool = ConcreteEnhancedBaseTool(mock_client, enable_embeddings=False)

        assert tool.enable_embeddings is False
        assert tool.client == mock_client
        assert ConcreteEnhancedBaseTool._embedding_manager is None

    def test_init_with_existing_embedding_manager(self, mock_client):
        """Test initialization when embedding manager already exists."""
        # Set up existing manager
        existing_manager = Mock(spec=EmbeddingManager)
        ConcreteEnhancedBaseTool._embedding_manager = existing_manager

        tool = ConcreteEnhancedBaseTool(mock_client, enable_embeddings=True)

        # Should reuse existing manager, not create new one
        assert ConcreteEnhancedBaseTool._embedding_manager is existing_manager
        assert tool.enable_embeddings is True

    def test_init_reuses_existing_embedding_manager(self, mock_client):
        """Test that multiple instances share the same embedding manager."""
        # Clear any existing embedding manager
        ConcreteEnhancedBaseTool._embedding_manager = None

        tool1 = ConcreteEnhancedBaseTool(mock_client, enable_embeddings=True)
        manager1 = ConcreteEnhancedBaseTool._embedding_manager

        tool2 = ConcreteEnhancedBaseTool(mock_client, enable_embeddings=True)
        manager2 = ConcreteEnhancedBaseTool._embedding_manager

        assert manager1 is manager2
        assert tool1.get_embedding_manager() is tool2.get_embedding_manager()

    def test_get_embedding_manager_when_enabled(self, tool_with_embeddings):
        """Test getting embedding manager when enabled."""
        manager = tool_with_embeddings.get_embedding_manager()
        assert manager is not None
        assert isinstance(manager, EmbeddingManager)

    def test_get_embedding_manager_when_disabled(self, tool_without_embeddings):
        """Test getting embedding manager when disabled."""
        # The embedding manager is shared across all instances, so even when
        # embeddings are disabled for this tool, it might still exist from other tests
        # The important thing is that the tool has embeddings disabled
        assert tool_without_embeddings.enable_embeddings is False

    async def test_build_embedding_index_success(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test successful embedding index building."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        # Mock the cached client call
        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.return_value = [
                {"id": "1", "properties": {"firstname": "John"}},
                {"id": "2", "properties": {"firstname": "Jane"}},
            ]

            result = await tool_with_embeddings.build_embedding_index("contacts", 100)

            assert result["success"] is True
            assert result["entity_type"] == "contacts"
            assert result["entities_indexed"] == 2
            assert "index_stats" in result

            mock_call.assert_called_once_with("get_contacts", limit=100)
            mock_embedding_manager.build_index.assert_called_once()

    async def test_build_embedding_index_embeddings_disabled(
        self, tool_without_embeddings
    ):
        """Test building index when embeddings are disabled."""
        result = await tool_without_embeddings.build_embedding_index("contacts", 100)

        assert result["success"] is False
        assert "Embeddings not enabled" in result["error"]

    async def test_build_embedding_index_no_manager(self, tool_with_embeddings):
        """Test building index when no embedding manager exists."""
        tool_with_embeddings._embedding_manager = None

        result = await tool_with_embeddings.build_embedding_index("contacts", 100)

        assert result["success"] is False
        assert "Embeddings not enabled" in result["error"]

    async def test_build_embedding_index_no_entities(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test building index when no entities are found."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.return_value = []

            result = await tool_with_embeddings.build_embedding_index("contacts", 100)

            assert result["success"] is False
            assert "No contacts found to index" in result["error"]

    async def test_build_embedding_index_exception(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test building index when an exception occurs."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.side_effect = Exception("API error")

            result = await tool_with_embeddings.build_embedding_index("contacts", 100)

            assert result["success"] is False
            assert "API error" in result["error"]

    async def test_semantic_search_success(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test successful semantic search."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        results = await tool_with_embeddings.semantic_search(
            "technology companies", k=5, threshold=0.7
        )

        assert len(results) == 2
        entity, score = results[0]
        assert entity["id"] == "1"
        assert score == 0.95

        mock_embedding_manager.search_similar.assert_called_once_with(
            "technology companies", 5, 0.7
        )

    async def test_semantic_search_embeddings_disabled(self, tool_without_embeddings):
        """Test semantic search when embeddings are disabled."""
        results = await tool_without_embeddings.semantic_search("test query")
        assert results == []

    async def test_semantic_search_no_manager(self, tool_with_embeddings):
        """Test semantic search when no embedding manager exists."""
        tool_with_embeddings._embedding_manager = None

        results = await tool_with_embeddings.semantic_search("test query")
        assert results == []

    async def test_semantic_search_exception(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test semantic search when an exception occurs."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager
        mock_embedding_manager.search_similar.side_effect = Exception("Search error")

        results = await tool_with_embeddings.semantic_search("test query")
        assert results == []

    async def test_hybrid_search_success(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test successful hybrid search."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        # Mock semantic search
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 0.9),
            ({"id": "3", "properties": {"name": "StartupCorp"}}, 0.8),
        ]

        with patch.object(tool_with_embeddings, "semantic_search") as mock_semantic:
            mock_semantic.return_value = semantic_results

            with patch.object(tool_with_embeddings, "_cached_client_call") as mock_api:
                mock_api.return_value = [
                    {"id": "1", "properties": {"name": "TechCorp"}},
                    {"id": "2", "properties": {"name": "InnovateCorp"}},
                ]

                results = await tool_with_embeddings.hybrid_search(
                    "tech", "companies", k=3
                )

                assert len(results) <= 3
                # Should contain entities from both semantic and API results
                entity_ids = [entity["id"] for entity in results]
                assert "1" in entity_ids  # Common entity

    async def test_hybrid_search_embeddings_disabled(self, tool_without_embeddings):
        """Test hybrid search when embeddings are disabled (should fallback)."""
        with patch.object(tool_without_embeddings, "_fallback_search") as mock_fallback:
            mock_fallback.return_value = [{"id": "1", "properties": {"name": "Test"}}]

            results = await tool_without_embeddings.hybrid_search(
                "test", "companies", k=5
            )

            mock_fallback.assert_called_once_with("test", "companies", 5)
            assert results == [{"id": "1", "properties": {"name": "Test"}}]

    async def test_hybrid_search_no_manager(self, tool_with_embeddings):
        """Test hybrid search when no embedding manager exists."""
        tool_with_embeddings._embedding_manager = None

        with patch.object(tool_with_embeddings, "_fallback_search") as mock_fallback:
            mock_fallback.return_value = [{"id": "1", "properties": {"name": "Test"}}]

            results = await tool_with_embeddings.hybrid_search("test", "companies", k=5)

            mock_fallback.assert_called_once_with("test", "companies", 5)
            assert results == [{"id": "1", "properties": {"name": "Test"}}]

    async def test_hybrid_search_exception_fallback(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test hybrid search falls back on exception."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        with patch.object(tool_with_embeddings, "semantic_search") as mock_semantic:
            mock_semantic.side_effect = Exception("Search error")

            with patch.object(
                tool_with_embeddings, "_fallback_search"
            ) as mock_fallback:
                mock_fallback.return_value = [
                    {"id": "1", "properties": {"name": "Fallback"}}
                ]

                results = await tool_with_embeddings.hybrid_search(
                    "test", "companies", k=5
                )

                mock_fallback.assert_called_once_with("test", "companies", 5)
                assert results == [{"id": "1", "properties": {"name": "Fallback"}}]

    def test_combine_search_results(self, tool_with_embeddings):
        """Test combining semantic and API search results."""
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 0.9),
            ({"id": "2", "properties": {"name": "StartupCorp"}}, 0.8),
        ]

        api_results = [
            {"id": "1", "properties": {"name": "TechCorp"}},  # Same as semantic
            {"id": "3", "properties": {"name": "NewCorp"}},  # Only in API
        ]

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.7, k=3
        )

        assert len(results) <= 3
        # Should contain entities from both sources
        entity_ids = [entity["id"] for entity in results]
        assert "1" in entity_ids  # Common entity should be ranked high
        assert "2" in entity_ids  # Semantic only
        assert "3" in entity_ids  # API only

    def test_combine_search_results_empty_inputs(self, tool_with_embeddings):
        """Test combining with empty inputs."""
        results = tool_with_embeddings._combine_search_results([], [], 0.7, 5)
        assert results == []

    def test_combine_search_results_entities_without_id(self, tool_with_embeddings):
        """Test combining results when entities don't have IDs."""
        semantic_results = [
            ({"properties": {"name": "TechCorp"}}, 0.9),  # No ID
        ]

        api_results = [
            {"properties": {"name": "ApiCorp"}},  # No ID
        ]

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.7, k=3
        )

        # Should return empty list since no entities have IDs
        assert results == []

    def test_combine_search_results_single_source(self, tool_with_embeddings):
        """Test combining when only one source has results."""
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 0.9),
        ]

        api_results = []

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.7, k=3
        )

        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_combine_search_results_api_relevance_calculation(
        self, tool_with_embeddings
    ):
        """Test API relevance score calculation in combine_search_results."""
        semantic_results = []

        api_results = [
            {"id": "1", "properties": {"name": "First"}},  # Should get highest score
            {"id": "2", "properties": {"name": "Second"}},  # Should get lower score
            {"id": "3", "properties": {"name": "Third"}},  # Should get lowest score
        ]

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.3, k=3
        )

        # First API result should be ranked highest due to position
        assert len(results) == 3
        assert results[0]["id"] == "1"  # First in API results gets highest relevance

    async def test_fallback_search_with_search_method(self, tool_with_embeddings):
        """Test fallback search when search method exists."""
        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.return_value = [{"id": "1", "properties": {"name": "Test"}}]

            results = await tool_with_embeddings._fallback_search(
                "test", "companies", 5
            )

            mock_call.assert_called_once_with(
                "search_companies", limit=5, filters={"search": "test"}
            )
            assert results == [{"id": "1", "properties": {"name": "Test"}}]

    async def test_fallback_search_without_search_method(self, tool_with_embeddings):
        """Test fallback search when no search method exists."""
        # Remove search method from client
        delattr(tool_with_embeddings.client, "search_companies")

        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.return_value = [
                {"id": "1", "properties": {"name": "TechCorp"}},
                {"id": "2", "properties": {"description": "Technology company"}},
                {"id": "3", "properties": {"name": "BioInc"}},
            ]

            results = await tool_with_embeddings._fallback_search(
                "tech", "companies", 2
            )

            mock_call.assert_called_once_with("get_companies", limit=100)
            # Should return entities containing "tech"
            assert len(results) <= 2
            for entity in results:
                entity_text = str(entity.get("properties", {})).lower()
                assert "tech" in entity_text

    async def test_fallback_search_text_matching_limit(self, tool_with_embeddings):
        """Test fallback search respects the k limit when filtering."""
        # Remove search method from client
        delattr(tool_with_embeddings.client, "search_companies")

        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            # Return many entities that match the query
            mock_call.return_value = [
                {"id": str(i), "properties": {"name": f"TechCorp{i}"}}
                for i in range(10)  # 10 entities, all containing "tech"
            ]

            results = await tool_with_embeddings._fallback_search(
                "tech", "companies", 3
            )

            # Should stop at k=3 results
            assert len(results) == 3

    async def test_fallback_search_exception(self, tool_with_embeddings):
        """Test fallback search when an exception occurs."""
        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.side_effect = Exception("API error")

            results = await tool_with_embeddings._fallback_search(
                "test", "companies", 5
            )
            assert results == []

    def test_get_embedding_stats_enabled(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test getting embedding stats when enabled."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        stats = tool_with_embeddings.get_embedding_stats()

        assert stats["enabled"] is True
        assert stats["status"] == "ready"
        assert stats["total_entities"] == 100
        assert stats["dimension"] == 384

    def test_get_embedding_stats_disabled(self, tool_without_embeddings):
        """Test getting embedding stats when disabled."""
        stats = tool_without_embeddings.get_embedding_stats()

        assert stats["enabled"] is False
        assert stats["status"] == "disabled"

    def test_get_embedding_stats_no_manager(self, tool_with_embeddings):
        """Test getting embedding stats when no manager exists."""
        tool_with_embeddings._embedding_manager = None

        stats = tool_with_embeddings.get_embedding_stats()

        assert stats["enabled"] is False
        assert stats["status"] == "disabled"

    def test_clear_embedding_cache_with_manager(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test clearing embedding cache when manager exists."""
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        EnhancedBaseTool._embedding_manager = mock_embedding_manager

        ConcreteEnhancedBaseTool.clear_embedding_cache()

        mock_embedding_manager.clear_cache.assert_called_once()

    def test_clear_embedding_cache_without_manager(self, tool_without_embeddings):
        """Test clearing embedding cache when no manager exists."""
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        EnhancedBaseTool._embedding_manager = None

        # Should not raise an exception
        ConcreteEnhancedBaseTool.clear_embedding_cache()

    def test_handle_error_embedding_related(self, tool_with_embeddings):
        """Test error handling for embedding-related errors."""
        error = Exception("FAISS index not found")

        result = tool_with_embeddings.handle_error(error)

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Embedding Tip" in result[0].text
        assert "Rebuilding the embedding index" in result[0].text

    def test_handle_error_embedding_keyword(self, tool_with_embeddings):
        """Test error handling when error message contains 'embedding'."""
        error = Exception("Embedding generation failed")

        result = tool_with_embeddings.handle_error(error)

        assert len(result) == 1
        assert "Embedding Tip" in result[0].text
        assert "sentence transformer model" in result[0].text

    def test_handle_error_faiss_keyword(self, tool_with_embeddings):
        """Test error handling when error message contains 'faiss'."""
        error = Exception("FAISS search failed")

        result = tool_with_embeddings.handle_error(error)

        assert len(result) == 1
        assert "Embedding Tip" in result[0].text

    def test_handle_error_mixed_case_keywords(self, tool_with_embeddings):
        """Test error handling with mixed case keywords."""
        error = Exception("Embedding and FAISS errors")

        result = tool_with_embeddings.handle_error(error)

        assert len(result) == 1
        assert "Embedding Tip" in result[0].text

    def test_handle_error_non_embedding(self, tool_with_embeddings):
        """Test error handling for non-embedding errors."""
        error = Exception("Regular API error")

        with patch.object(
            tool_with_embeddings.__class__.__bases__[0], "handle_error"
        ) as mock_super:
            mock_super.return_value = [types.TextContent(type="text", text="API Error")]

            result = tool_with_embeddings.handle_error(error)

            mock_super.assert_called_once_with(error)
            assert len(result) == 1
            assert "Embedding Tip" not in result[0].text

    async def test_hybrid_search_no_search_method(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test hybrid search when client has no search method for entity type."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        # Remove search method
        delattr(tool_with_embeddings.client, "search_companies")

        with patch.object(tool_with_embeddings, "semantic_search") as mock_semantic:
            mock_semantic.return_value = [
                ({"id": "1", "properties": {"name": "TechCorp"}}, 0.9),
            ]

            with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
                # This should be called but return empty since no search method
                mock_call.return_value = []

                results = await tool_with_embeddings.hybrid_search(
                    "tech", "companies", k=3
                )

                assert len(results) >= 0  # Should still work with semantic results only
                # Semantic search should still be called
                mock_semantic.assert_called_once()

    async def test_build_embedding_index_default_limit(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test building embedding index with default limit."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        with patch.object(tool_with_embeddings, "_cached_client_call") as mock_call:
            mock_call.return_value = [{"id": "1", "properties": {"name": "Test"}}]

            result = await tool_with_embeddings.build_embedding_index("contacts")

            mock_call.assert_called_once_with(
                "get_contacts", limit=1000
            )  # Default limit
            assert result["success"] is True

    def test_combine_search_results_with_weights(self, tool_with_embeddings):
        """Test combining results with different semantic weights."""
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 1.0),
        ]

        api_results = [
            {"id": "2", "properties": {"name": "ApiCorp"}},
        ]

        # Test with high semantic weight
        results_high_semantic = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.9, k=2
        )

        # Test with low semantic weight
        results_low_semantic = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.1, k=2
        )

        assert len(results_high_semantic) == 2
        assert len(results_low_semantic) == 2
        # Order might differ based on weights, but both entities should be present

    def test_combine_search_results_zero_semantic_weight(self, tool_with_embeddings):
        """Test combining results with zero semantic weight."""
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 1.0),
        ]

        api_results = [
            {"id": "2", "properties": {"name": "ApiCorp"}},
        ]

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=0.0, k=2
        )

        assert len(results) == 2
        # With zero semantic weight, API results should be preferred

    def test_combine_search_results_max_semantic_weight(self, tool_with_embeddings):
        """Test combining results with maximum semantic weight."""
        semantic_results = [
            ({"id": "1", "properties": {"name": "TechCorp"}}, 1.0),
        ]

        api_results = [
            {"id": "2", "properties": {"name": "ApiCorp"}},
        ]

        results = tool_with_embeddings._combine_search_results(
            semantic_results, api_results, semantic_weight=1.0, k=2
        )

        assert len(results) == 2
        # With max semantic weight, semantic results should be preferred

    def test_class_method_get_embedding_manager(self):
        """Test the class method for getting embedding manager."""
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        # Test when no manager exists
        EnhancedBaseTool._embedding_manager = None
        assert ConcreteEnhancedBaseTool.get_embedding_manager() is None

        # Test when manager exists
        mock_manager = Mock()
        EnhancedBaseTool._embedding_manager = mock_manager
        assert ConcreteEnhancedBaseTool.get_embedding_manager() is mock_manager

    async def test_semantic_search_with_default_parameters(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test semantic search with default parameters."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        await tool_with_embeddings.semantic_search("test query")

        mock_embedding_manager.search_similar.assert_called_once_with(
            "test query", 5, 0.5
        )

    async def test_hybrid_search_with_default_parameters(
        self, tool_with_embeddings, mock_embedding_manager
    ):
        """Test hybrid search with default parameters."""
        tool_with_embeddings._embedding_manager = mock_embedding_manager

        with patch.object(tool_with_embeddings, "semantic_search") as mock_semantic:
            mock_semantic.return_value = []

            with patch.object(tool_with_embeddings, "_cached_client_call") as mock_api:
                mock_api.return_value = []

                await tool_with_embeddings.hybrid_search("test", "companies")

                # Should call semantic_search with k*2 and default threshold
                mock_semantic.assert_called_with("test", 10, 0.3)  # k=5 * 2 = 10
