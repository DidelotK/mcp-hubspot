"""Unit tests for the SemanticSearchTool class."""

from unittest.mock import AsyncMock, Mock

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.semantic_search_tool import SemanticSearchTool


class TestSemanticSearchTool:
    """Test the SemanticSearchTool class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock(spec=HubSpotClient)
        client.api_key = "test-key"
        return client

    @pytest.fixture
    def tool(self, mock_client):
        """Create a SemanticSearchTool instance for testing."""
        return SemanticSearchTool(client=mock_client)

    @pytest.fixture
    def mock_entities(self):
        """Create mock entities for testing."""
        return [
            {
                "id": "1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john@example.com",
                    "jobtitle": "Software Engineer",
                },
            },
            {
                "id": "2",
                "properties": {
                    "name": "TechCorp",
                    "domain": "techcorp.com",
                    "industry": "Technology",
                },
            },
        ]

    def test_get_tool_definition(self, tool):
        """Test tool definition generation."""
        definition = tool.get_tool_definition()

        assert definition.name == "semantic_search_hubspot"
        assert "AI-powered semantic search" in definition.description

        # Check schema structure
        schema = definition.inputSchema
        assert "query" in schema["properties"]
        assert "entity_types" in schema["properties"]
        assert "limit" in schema["properties"]
        assert "threshold" in schema["properties"]
        assert "search_mode" in schema["properties"]

        # Check required fields
        assert schema["required"] == ["query"]

    @pytest.mark.asyncio
    async def test_execute_empty_query(self, tool):
        """Test execution with empty query."""
        result = await tool.execute({"query": ""})

        assert len(result) == 1
        assert "Error" in result[0].text
        assert "cannot be empty" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_embeddings_disabled(self, tool):
        """Test execution when embeddings are disabled."""
        # Mock disabled embeddings
        tool.enable_embeddings = False

        result = await tool.execute({"query": "test query"})

        assert len(result) == 1
        assert "Embeddings Not Available" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_no_embeddings_available(self, tool):
        """Test execution when no embedding stats are available."""
        # Mock get_embedding_stats to return disabled status
        tool.get_embedding_stats = Mock(return_value={"enabled": False})

        result = await tool.execute({"query": "software engineer"})

        assert len(result) == 1
        assert "Embeddings Not Available" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_semantic_search_mode(self, tool, mock_entities):
        """Test execution with semantic search mode."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock semantic search
        tool.semantic_search = AsyncMock(
            return_value=[(mock_entities[0], 0.8), (mock_entities[1], 0.7)]
        )

        result = await tool.execute(
            {
                "query": "software engineer",
                "search_mode": "semantic",
                "entity_types": ["contacts", "companies"],
            }
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        assert "software engineer" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_hybrid_search_mode(self, tool, mock_entities):
        """Test execution with hybrid search mode."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock hybrid search
        tool.hybrid_search = AsyncMock(return_value=mock_entities)

        result = await tool.execute(
            {
                "query": "technology companies",
                "search_mode": "hybrid",
                "entity_types": ["companies"],
            }
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_auto_search_mode(self, tool, mock_entities):
        """Test execution with auto search mode."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock hybrid search with fallback
        tool.hybrid_search = AsyncMock(
            side_effect=[[], mock_entities]
        )  # First empty, then fallback
        tool.semantic_search = AsyncMock(return_value=[(mock_entities[0], 0.8)])

        result = await tool.execute(
            {"query": "engineer", "search_mode": "auto", "entity_types": ["contacts"]}
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_no_results(self, tool):
        """Test execution when no results are found."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock empty search results
        tool.hybrid_search = AsyncMock(return_value=[])
        tool.semantic_search = AsyncMock(return_value=[])

        result = await tool.execute(
            {"query": "nonexistent query", "entity_types": ["contacts"]}
        )

        assert len(result) == 1
        assert "No matching entities found" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_with_search_error(self, tool):
        """Test execution when search throws an error."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock search error
        tool.hybrid_search = AsyncMock(side_effect=Exception("Search failed"))

        result = await tool.execute(
            {"query": "test query", "entity_types": ["contacts"]}
        )

        assert len(result) == 1
        # Should handle error gracefully

    def test_get_entity_type_from_result_contacts(self, tool):
        """Test entity type detection for contacts."""
        contact = {
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
            }
        }

        entity_type = tool._get_entity_type_from_result(contact)
        assert entity_type == "contacts"

    def test_get_entity_type_from_result_companies(self, tool):
        """Test entity type detection for companies."""
        company = {
            "properties": {
                "name": "TechCorp",
                "domain": "techcorp.com",
                "industry": "Technology",
            }
        }

        entity_type = tool._get_entity_type_from_result(company)
        assert entity_type == "companies"

    def test_get_entity_type_from_result_deals(self, tool):
        """Test entity type detection for deals."""
        deal = {
            "properties": {
                "dealname": "Project Alpha",
                "amount": "50000",
                "dealstage": "proposal",
            }
        }

        entity_type = tool._get_entity_type_from_result(deal)
        assert entity_type == "deals"

    def test_get_entity_type_from_result_engagements(self, tool):
        """Test entity type detection for engagements."""
        engagement = {
            "properties": {"hs_engagement_type": "EMAIL", "hs_engagement_source": "CRM"}
        }

        entity_type = tool._get_entity_type_from_result(engagement)
        assert entity_type == "engagements"

    def test_get_entity_type_from_result_fallback(self, tool):
        """Test entity type detection fallback logic."""
        # Entity with contact-like properties but no standard contact fields
        entity = {"properties": {"company": "TechCorp", "jobtitle": "Engineer"}}

        entity_type = tool._get_entity_type_from_result(entity)
        assert entity_type == "contacts"

    def test_get_entity_type_from_result_unknown(self, tool):
        """Test entity type detection for unknown entities."""
        entity = {"properties": {"random_field": "value"}}

        entity_type = tool._get_entity_type_from_result(entity)
        assert entity_type == "unknown"

    def test_format_search_results(self, tool, mock_entities):
        """Test search results formatting."""
        results = {"contacts": [mock_entities[0]], "companies": [mock_entities[1]]}

        formatted = tool._format_search_results(results, "test query", "hybrid", 0.5, 2)

        assert "Semantic Search Results" in formatted
        assert "test query" in formatted
        assert "hybrid" in formatted
        assert "Total Results:** 2" in formatted
        assert "Tips for Better Results" in formatted

    def test_format_search_results_with_errors(self, tool):
        """Test formatting when some entity types have errors."""
        results = {
            "contacts": [{"id": "1", "properties": {"firstname": "John"}}],
            "companies": {"error": "API error occurred"},
        }

        formatted = tool._format_search_results(
            results, "test query", "semantic", 0.5, 1
        )

        assert "Semantic Search Results" in formatted
        assert "Error - API error occurred" in formatted

    @pytest.mark.asyncio
    async def test_execute_with_custom_parameters(self, tool, mock_entities):
        """Test execution with custom parameters."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Mock hybrid search
        tool.hybrid_search = AsyncMock(return_value=mock_entities)

        result = await tool.execute(
            {
                "query": "senior engineer",
                "entity_types": ["contacts"],
                "limit": 10,
                "threshold": 0.7,
                "search_mode": "hybrid",
            }
        )

        # Verify hybrid_search was called with correct parameters
        tool.hybrid_search.assert_called_with(
            "senior engineer", "contacts", 10, semantic_weight=0.7, threshold=0.7
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
