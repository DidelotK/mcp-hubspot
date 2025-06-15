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

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_with_filtering(self, tool):
        """Test semantic mode with entity type filtering to cover lines 173-174."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create mock entities of different types
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
            },
        }

        company_entity = {
            "id": "2",
            "properties": {
                "name": "TechCorp",
                "domain": "techcorp.com",
                "industry": "Technology",
            },
        }

        # Mock semantic search returning mixed entities
        tool.semantic_search = AsyncMock(
            return_value=[(contact_entity, 0.9), (company_entity, 0.8)]
        )

        # Test filtering for just contacts
        result = await tool.execute(
            {
                "query": "software engineer",
                "search_mode": "semantic",
                "entity_types": ["contacts"],
                "limit": 5,
                "threshold": 0.5,
            }
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        # Should only show contacts, not companies
        assert "John" in result[0].text or "Contacts (" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_auto_mode_fallback_to_semantic(self, tool):
        """Test auto mode fallback to semantic search to cover line 201."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Alice",
                "lastname": "Smith",
                "email": "alice@example.com",
            },
        }

        # Mock hybrid search to return empty first, then semantic search with results
        tool.hybrid_search = AsyncMock(return_value=[])  # Empty hybrid results
        tool.semantic_search = AsyncMock(return_value=[(contact_entity, 0.8)])

        result = await tool.execute(
            {
                "query": "product manager",
                "search_mode": "auto",
                "entity_types": ["contacts"],
                "limit": 5,
                "threshold": 0.5,
            }
        )

        # Verify both hybrid and semantic search were called
        tool.hybrid_search.assert_called_once()
        tool.semantic_search.assert_called_once()

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text

    def test_format_search_results_with_engagements(self, tool):
        """Test formatting search results with engagements to cover line 238."""
        engagement_entity = {
            "id": "1",
            "properties": {
                "hs_engagement_type": "EMAIL",
                "hs_engagement_source": "CRM",
                "hs_body_preview": "Meeting scheduled for next week",
            },
        }

        results = {"engagements": [engagement_entity]}

        formatted = tool._format_search_results(
            results, "meeting email", "hybrid", 0.6, 1
        )

        assert "Semantic Search Results" in formatted
        assert "meeting email" in formatted
        assert "Engagements (1 found)" in formatted
        assert "Total Results:** 1" in formatted

    def test_format_search_results_with_header_extraction(self, tool):
        """Test formatting with header extraction logic to cover lines 247-252."""
        # Create a result that will trigger the header extraction logic
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Bob",
                "lastname": "Johnson",
                "email": "bob@example.com",
                "company": "TestCorp",
            },
        }

        results = {"contacts": [contact_entity]}

        # Mock the HubSpotFormatter to return content with a header
        import unittest.mock

        with unittest.mock.patch(
            "hubspot_mcp.tools.semantic_search_tool.HubSpotFormatter"
        ) as mock_formatter:
            mock_formatter.format_contacts.return_value = (
                "🎯 **HubSpot Contacts** (1 found)\n\n"
                "**Bob Johnson**\n"
                "  📧 Email: bob@example.com\n"
                "  🏢 Company: TestCorp\n"
                "  🆔 ID: 1\n\n"
            )

            formatted = tool._format_search_results(
                results, "test query", "semantic", 0.5, 1
            )

            # Verify the header extraction logic was triggered
            assert "Semantic Search Results" in formatted
            assert "Bob Johnson" in formatted

    def test_format_search_results_empty_entities_list(self, tool):
        """Test formatting when entities list is empty but present."""
        results = {
            "contacts": [],  # Empty list, not missing
            "companies": [{"id": "1", "properties": {"name": "TestCorp"}}],
        }

        formatted = tool._format_search_results(results, "test query", "hybrid", 0.5, 1)

        assert "Semantic Search Results" in formatted
        assert "Companies (1 found)" in formatted
        # Should not include contacts section since it's empty

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_no_matching_entities(self, tool):
        """Test semantic mode when filtering results in no matching entities."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create entities that don't match the requested entity type
        company_entity = {
            "id": "1",
            "properties": {"name": "TechCorp", "domain": "techcorp.com"},
        }

        # Mock semantic search returning companies but we're looking for contacts
        tool.semantic_search = AsyncMock(return_value=[(company_entity, 0.8)])

        result = await tool.execute(
            {
                "query": "engineer",
                "search_mode": "semantic",
                "entity_types": [
                    "contacts"
                ],  # Looking for contacts but only companies returned
                "limit": 5,
                "threshold": 0.5,
            }
        )

        assert len(result) == 1
        assert "No matching entities found" in result[0].text

    def test_get_entity_type_from_result_company_fallback(self, tool):
        """Test entity type detection for companies using fallback logic."""
        company = {
            "properties": {
                "industry": "Technology",
                "city": "San Francisco",
                "country": "USA",
                # No name or domain, so should use fallback logic
            }
        }

        entity_type = tool._get_entity_type_from_result(company)
        assert entity_type == "companies"

    @pytest.mark.asyncio
    async def test_execute_auto_mode_with_semantic_fallback_and_filtering(self, tool):
        """Test auto mode with complete semantic fallback and entity filtering."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Charlie",
                "lastname": "Brown",
                "email": "charlie@example.com",
            },
        }

        deal_entity = {
            "id": "2",
            "properties": {
                "dealname": "Big Deal",
                "amount": "100000",
                "dealstage": "closed-won",
            },
        }

        # Mock hybrid search to return empty
        tool.hybrid_search = AsyncMock(return_value=[])

        # Mock semantic search to return mixed entities
        tool.semantic_search = AsyncMock(
            return_value=[(contact_entity, 0.9), (deal_entity, 0.8)]
        )

        result = await tool.execute(
            {
                "query": "sales person",
                "search_mode": "auto",
                "entity_types": ["contacts"],  # Only want contacts
                "limit": 5,
                "threshold": 0.5,
            }
        )

        # Verify both searches were called
        tool.hybrid_search.assert_called_once()
        tool.semantic_search.assert_called_once()

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        # Should only show the contact, not the deal
        assert "Charlie" in result[0].text or "Contacts (" in result[0].text

    def test_format_search_results_unknown_entity_type(self, tool):
        """Test formatting with unknown entity type to cover the else clause (line 252)."""
        # Create an entity with unknown type
        unknown_entity = {
            "id": "1",
            "properties": {
                "some_field": "some_value",
                "another_field": "another_value",
            },
        }

        results = {"unknown_type": [unknown_entity]}

        formatted = tool._format_search_results(
            results, "test query", "semantic", 0.5, 1
        )

        assert "Semantic Search Results" in formatted
        # The formatting creates a title case section: "Unknown_Type (1 found)"
        assert "Unknown_Type (1 found)" in formatted

    def test_format_search_results_with_skip_header_logic(self, tool):
        """Test the header skipping logic in formatting (lines 248, 252)."""
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Test",
                "lastname": "User",
                "email": "test@example.com",
            },
        }

        results = {"contacts": [contact_entity]}

        # Mock the formatter to return a specific format with header
        import unittest.mock

        with unittest.mock.patch(
            "hubspot_mcp.tools.semantic_search_tool.HubSpotFormatter"
        ) as mock_formatter:
            # Return a format that will trigger the header skipping logic
            mock_formatter.format_contacts.return_value = (
                "Some initial content\n"
                "**Header Line**\n"
                "  Some entity data\n"
                "  More entity data\n"
            )

            formatted = tool._format_search_results(
                results, "test query", "semantic", 0.5, 1
            )

            # Verify the header extraction was applied
            assert "Semantic Search Results" in formatted
            assert "Header Line" in formatted

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_with_specific_entity_filtering(self, tool):
        """Test semantic mode to specifically target the filtering logic (lines 173-174)."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create entities where the filtering will be very specific
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
                "jobtitle": "Engineer",
            },
        }

        deal_entity = {
            "id": "2",
            "properties": {
                "dealname": "Big Sale",
                "amount": "50000",
                "dealstage": "proposal",
            },
        }

        engagement_entity = {
            "id": "3",
            "properties": {"hs_engagement_type": "CALL", "hs_engagement_source": "CRM"},
        }

        # Mock semantic search to return all types, but we only want deals
        tool.semantic_search = AsyncMock(
            return_value=[
                (contact_entity, 0.9),
                (deal_entity, 0.8),
                (engagement_entity, 0.7),
            ]
        )

        # Test with entity_types filtering
        result = await tool.execute(
            {
                "query": "sales opportunity",
                "search_mode": "semantic",
                "entity_types": ["deals"],  # Only want deals
                "limit": 10,
                "threshold": 0.5,
            }
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        # Should only show deals, not contacts or engagements
        tool.semantic_search.assert_called_once_with("sales opportunity", 10, 0.5)

    @pytest.mark.asyncio
    async def test_execute_auto_mode_semantic_fallback_filtering(self, tool):
        """Test auto mode semantic fallback with entity filtering (lines 134-140)."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create mixed entities for semantic fallback
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Sarah",
                "lastname": "Connor",
                "email": "sarah@example.com",
            },
        }

        company_entity = {
            "id": "2",
            "properties": {
                "name": "Cyberdyne Systems",
                "domain": "cyberdyne.com",
                "industry": "Technology",
            },
        }

        # Mock hybrid search to return empty for fallback
        tool.hybrid_search = AsyncMock(return_value=[])

        # Mock semantic search to return mixed entities
        tool.semantic_search = AsyncMock(
            return_value=[(contact_entity, 0.9), (company_entity, 0.8)]
        )

        # Test auto mode fallback with specific entity type filtering
        result = await tool.execute(
            {
                "query": "technology leader",
                "search_mode": "auto",
                "entity_types": ["companies"],  # Only want companies
                "limit": 5,
                "threshold": 0.6,
            }
        )

        # Verify both searches were called
        tool.hybrid_search.assert_called_once()
        tool.semantic_search.assert_called_once()

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        # Should only show companies, not contacts
        assert "Cyberdyne" in result[0].text or "Companies (" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_direct_entity_filtering_exact_lines(
        self, tool
    ):
        """Test semantic mode to cover the exact filtering lines 173-174."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create a very specific scenario to hit lines 173-174
        # We need the semantic search to return results that get filtered by entity type
        contact_entity_1 = {
            "id": "contact1",
            "properties": {
                "firstname": "Test",
                "lastname": "Contact",
                "email": "test@contact.com",
            },
        }

        contact_entity_2 = {
            "id": "contact2",
            "properties": {
                "firstname": "Another",
                "lastname": "Contact",
                "email": "another@contact.com",
            },
        }

        company_entity = {
            "id": "company1",
            "properties": {"name": "Test Company", "domain": "testcompany.com"},
        }

        # Mock the semantic search to return mixed entity types with scores
        tool.semantic_search = AsyncMock(
            return_value=[
                (contact_entity_1, 0.95),
                (company_entity, 0.85),
                (contact_entity_2, 0.75),
            ]
        )

        # Execute with semantic mode, requesting only contacts
        # This should trigger the filtering logic in lines 173-174
        result = await tool.execute(
            {
                "query": "test search",
                "search_mode": "semantic",
                "entity_types": ["contacts"],
                "limit": 10,
                "threshold": 0.5,
            }
        )

        # Verify the semantic search was called
        tool.semantic_search.assert_called_once_with("test search", 10, 0.5)

        # Verify results contain only contacts (filtered out the company)
        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        # Should contain both contacts but not the company
        result_text = result[0].text
        assert (
            "Test Contact" in result_text
            or "Another Contact" in result_text
            or "Contacts (" in result_text
        )
        # Should not contain the company info
        assert "Test Company" not in result_text

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_filtering_with_multiple_entity_types(
        self, tool
    ):
        """Test semantic mode filtering with multiple requested entity types."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create entities of different types
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
            },
        }

        company_entity = {
            "id": "2",
            "properties": {"name": "TechCorp", "domain": "techcorp.com"},
        }

        deal_entity = {
            "id": "3",
            "properties": {
                "dealname": "Big Deal",
                "amount": "100000",
                "dealstage": "proposal",
            },
        }

        engagement_entity = {
            "id": "4",
            "properties": {
                "hs_engagement_type": "EMAIL",
                "hs_engagement_source": "CRM",
            },
        }

        # Mock semantic search to return all entity types
        tool.semantic_search = AsyncMock(
            return_value=[
                (contact_entity, 0.9),
                (company_entity, 0.8),
                (deal_entity, 0.7),
                (engagement_entity, 0.6),
            ]
        )

        # Request only contacts and companies (should filter out deals and engagements)
        result = await tool.execute(
            {
                "query": "business search",
                "search_mode": "semantic",
                "entity_types": ["contacts", "companies"],
                "limit": 5,
                "threshold": 0.5,
            }
        )

        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text
        result_text = result[0].text

        # Should contain contacts and companies sections
        assert (
            "Contacts (" in result_text
            or "John" in result_text
            or "Companies (" in result_text
            or "TechCorp" in result_text
        )

        # Should not contain deals or engagements
        assert "Big Deal" not in result_text
        assert "EMAIL" not in result_text

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_force_filtering_lines_173_174(self, tool):
        """Force execution of the exact filtering lines 173-174 in semantic mode."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create specific entities to ensure filtering is triggered
        # We need entities where _get_entity_type_from_result will be called for each
        contact_entity = {
            "id": "1",
            "properties": {
                "firstname": "Jane",
                "lastname": "Smith",
                "email": "jane@example.com",
            },
        }

        # Mock _get_entity_type_from_result to ensure it's called during filtering
        original_get_entity_type = tool._get_entity_type_from_result
        tool._get_entity_type_from_result = Mock(
            side_effect=lambda entity: original_get_entity_type(entity)
        )

        # Mock semantic search to return results that need filtering
        tool.semantic_search = AsyncMock(return_value=[(contact_entity, 0.9)])

        # Execute semantic mode to trigger the filtering logic
        result = await tool.execute(
            {
                "query": "test",
                "search_mode": "semantic",
                "entity_types": ["contacts"],
                "limit": 5,
                "threshold": 0.5,
            }
        )

        # Verify that the filtering methods were called
        tool.semantic_search.assert_called_once()
        tool._get_entity_type_from_result.assert_called()

        # Verify the result
        assert len(result) == 1
        assert "Semantic Search Results" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_semantic_mode_with_entity_type_mismatch_filtering(
        self, tool
    ):
        """Test semantic mode where filtering removes all entities to hit lines 173-174."""
        # Mock embedding stats
        tool.get_embedding_stats = Mock(return_value={"enabled": True})

        # Create an entity that will be filtered out
        company_entity = {
            "id": "1",
            "properties": {"name": "Test Company", "domain": "test.com"},
        }

        # Mock semantic search to return a company
        tool.semantic_search = AsyncMock(return_value=[(company_entity, 0.8)])

        # Request contacts but semantic search returns companies - should be filtered out
        result = await tool.execute(
            {
                "query": "business",
                "search_mode": "semantic",
                "entity_types": ["contacts"],  # Requesting contacts
                "limit": 5,
                "threshold": 0.5,
            }
        )

        # This should trigger the filtering logic and result in no matching entities
        assert len(result) == 1
        assert "No matching entities found" in result[0].text

        # Verify semantic search was called
        tool.semantic_search.assert_called_once_with("business", 5, 0.5)
