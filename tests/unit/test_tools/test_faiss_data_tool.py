"""Tests for FAISS data browsing tool."""

from unittest.mock import MagicMock, patch

import pytest

from hubspot_mcp.tools.faiss_data_tool import FaissDataTool


class TestFaissDataTool:
    """Test the FAISS data browsing tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.tool = FaissDataTool(self.mock_client)

    def test_get_tool_definition(self):
        """Test that the tool definition is correct."""
        definition = self.tool.get_tool_definition()

        assert definition.name == "browse_hubspot_indexed_data"
        assert (
            "Browse and search HubSpot entities indexed in FAISS"
            in definition.description
        )

        # Check input schema
        schema = definition.inputSchema
        assert schema["type"] == "object"

        properties = schema["properties"]
        assert "action" in properties
        assert "entity_type" in properties
        assert "offset" in properties
        assert "limit" in properties
        assert "search_text" in properties
        assert "include_content" in properties

        # Check action enum values
        assert set(properties["action"]["enum"]) == {"list", "stats", "search"}

        # Check entity_type enum values
        assert set(properties["entity_type"]["enum"]) == {
            "contacts",
            "companies",
            "deals",
            "engagements",
        }

        # Check default values
        assert properties["action"]["default"] == "list"
        assert properties["offset"]["default"] == 0
        assert properties["limit"]["default"] == 20
        assert properties["include_content"]["default"] is False

    @pytest.mark.asyncio
    async def test_execute_invalid_action(self):
        """Test executing with invalid action."""
        result = await self.tool.execute({"action": "invalid"})

        assert len(result) == 1
        assert "Invalid Action" in result[0].text
        assert "invalid" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_stats_no_embedding_manager(self):
        """Test stats action when no embedding manager is available."""
        with patch.object(self.tool, "get_embedding_manager", return_value=None):
            result = await self.tool.execute({"action": "stats"})

            assert len(result) == 1
            assert "No embedding manager available" in result[0].text
            assert "Status**: No embedding manager available" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_stats_index_not_ready(self):
        """Test stats action when index is not ready."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "not_ready"}

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "stats"})

            assert len(result) == 1
            assert "Status**: not_ready" in result[0].text
            assert "not ready for querying" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_stats_success(self):
        """Test successful stats action."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {
            "status": "ready",
            "dimension": 768,
            "index_type": "flat",
            "model_name": "test-model",
            "cache_size": 100,
        }
        mock_manager.entity_metadata = {
            0: {"entity_type": "contacts", "entity": {"id": "1"}},
            1: {"entity_type": "contacts", "entity": {"id": "2"}},
            2: {"entity_type": "companies", "entity": {"id": "3"}},
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "stats"})

            assert len(result) == 1
            text = result[0].text
            assert "Status**: ready" in text
            assert "Total indexed entities: 3" in text
            assert "Vector dimension: 768" in text
            assert "Index type: flat" in text
            assert "Model: test-model" in text
            assert "Cache size: 100" in text
            assert "contacts: 2 (66.7%)" in text
            assert "companies: 1 (33.3%)" in text

    @pytest.mark.asyncio
    async def test_execute_list_no_embedding_manager(self):
        """Test list action when no embedding manager is available."""
        with patch.object(self.tool, "get_embedding_manager", return_value=None):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            assert "No embedding manager available" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_list_index_not_ready(self):
        """Test list action when index is not ready."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "building"}

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            assert "FAISS index not ready" in result[0].text
            assert "Current status: building" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_list_success_basic(self):
        """Test successful list action with basic parameters."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {
                        "firstname": "John",
                        "lastname": "Doe",
                        "email": "john@test.com",
                    },
                },
                "text": "John Doe sales representative",
            },
            1: {
                "entity_type": "companies",
                "entity": {"id": "company1", "properties": {"name": "Test Corp"}},
                "text": "Test Corp technology company",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            text = result[0].text
            assert "Indexed Entities**" in text
            assert "Total entities: 2" in text
            assert "Showing: 1-2 of 2" in text
            assert "1. John Doe" in text
            assert "Type: contacts" in text
            assert "ID: contact1" in text
            assert "2. Test Corp" in text
            assert "Type: companies" in text
            assert "ID: company1" in text

    @pytest.mark.asyncio
    async def test_execute_list_with_pagination(self):
        """Test list action with pagination."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            i: {
                "entity_type": "contacts",
                "entity": {
                    "id": f"contact{i}",
                    "properties": {"firstname": f"User{i}", "lastname": "Test"},
                },
                "text": f"User{i} Test contact",
            }
            for i in range(5)
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            # Test first page
            result = await self.tool.execute(
                {"action": "list", "limit": 2, "offset": 0}
            )

            assert len(result) == 1
            text = result[0].text
            assert "Total entities: 5" in text
            assert "Showing: 1-2 of 5" in text
            assert "1. User0 Test" in text
            assert "2. User1 Test" in text
            assert "Next page**: Use offset=2" in text

    @pytest.mark.asyncio
    async def test_execute_list_with_entity_type_filter(self):
        """Test list action with entity type filter."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe",
            },
            1: {
                "entity_type": "companies",
                "entity": {"id": "company1", "properties": {"name": "Test Corp"}},
                "text": "Test Corp",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "list", "entity_type": "contacts"}
            )

            assert len(result) == 1
            text = result[0].text
            assert "(filtered by contacts)" in text
            assert "Total entities: 1" in text
            assert "John Doe" in text
            assert "Test Corp" not in text

    @pytest.mark.asyncio
    async def test_execute_list_with_include_content(self):
        """Test list action with include_content=True."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe sales representative with extensive experience",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "list", "include_content": True}
            )

            assert len(result) == 1
            text = result[0].text
            assert (
                "Content: John Doe sales representative with extensive experience"
                in text
            )

    @pytest.mark.asyncio
    async def test_execute_list_offset_exceeds_total(self):
        """Test list action when offset exceeds total count."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {"id": "contact1", "properties": {}},
                "text": "test",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list", "offset": 10})

            assert len(result) == 1
            text = result[0].text
            assert "Offset exceeds total count" in text
            assert "Maximum valid offset is 0" in text

    @pytest.mark.asyncio
    async def test_execute_search_no_search_text(self):
        """Test search action without search text."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "search"})

            assert len(result) == 1
            assert "No search text provided" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_search_success(self):
        """Test successful search action."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe is a sales representative with experience in technology",
            },
            1: {
                "entity_type": "companies",
                "entity": {"id": "company1", "properties": {"name": "Tech Corp"}},
                "text": "Tech Corp provides software solutions",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "search", "search_text": "technology"}
            )

            assert len(result) == 1
            text = result[0].text
            assert "Search Results for 'technology'" in text
            assert "Total matches: 1" in text
            assert "John Doe" in text
            assert (
                "Match: ... Doe is a sales representative with experience in technology"
                in text
            )

    @pytest.mark.asyncio
    async def test_execute_search_case_insensitive(self):
        """Test search is case insensitive."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe works with TECHNOLOGY companies",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "search", "search_text": "technology"}
            )

            assert len(result) == 1
            text = result[0].text
            assert "Total matches: 1" in text
            assert "John Doe" in text

    @pytest.mark.asyncio
    async def test_execute_search_no_matches(self):
        """Test search with no matches."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {"id": "contact1", "properties": {}},
                "text": "John Doe sales representative",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "search", "search_text": "nonexistent"}
            )

            assert len(result) == 1
            text = result[0].text
            assert "No matches found" in text
            assert "for 'nonexistent'" in text

    @pytest.mark.asyncio
    async def test_execute_search_with_entity_type_filter(self):
        """Test search with entity type filter."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe technology sales",
            },
            1: {
                "entity_type": "companies",
                "entity": {"id": "company1", "properties": {"name": "Tech Corp"}},
                "text": "Tech Corp technology solutions",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {
                    "action": "search",
                    "search_text": "technology",
                    "entity_type": "contacts",
                }
            )

            assert len(result) == 1
            text = result[0].text
            assert "in contacts**" in text
            assert "Total matches: 1" in text
            assert "John Doe" in text
            assert "Tech Corp" not in text

    @pytest.mark.asyncio
    async def test_execute_search_with_pagination(self):
        """Test search with pagination."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            i: {
                "entity_type": "contacts",
                "entity": {
                    "id": f"contact{i}",
                    "properties": {"firstname": f"User{i}"},
                },
                "text": f"User{i} technology specialist",
            }
            for i in range(5)
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {
                    "action": "search",
                    "search_text": "technology",
                    "limit": 2,
                    "offset": 1,
                }
            )

            assert len(result) == 1
            text = result[0].text
            assert "Total matches: 5" in text
            assert "Showing: 2-3 of 5" in text
            assert "Next page**: Use offset=3" in text
            assert "Previous page**: Use offset=0" in text

    @pytest.mark.asyncio
    async def test_execute_search_with_include_content(self):
        """Test search with include_content=True."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": "John Doe is a technology sales representative with extensive experience in enterprise solutions",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {
                    "action": "search",
                    "search_text": "technology",
                    "include_content": True,
                }
            )

            assert len(result) == 1
            text = result[0].text
            assert "Full content: John Doe is a technology sales representative" in text

    @pytest.mark.asyncio
    async def test_execute_with_exception(self):
        """Test execution with exception handling."""
        with patch.object(
            self.tool, "get_embedding_manager", side_effect=Exception("Test error")
        ):
            result = await self.tool.execute({"action": "stats"})

            assert len(result) == 1
            assert "Unexpected error" in result[0].text

    @pytest.mark.asyncio
    async def test_entity_name_extraction_contacts(self):
        """Test entity name extraction for contacts."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {
                        "firstname": "Jane",
                        "lastname": "Smith",
                        "email": "jane@test.com",
                    },
                },
                "text": "Jane Smith contact",
            },
            1: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact2",
                    "properties": {
                        "email": "nofirstname@test.com"
                    },  # No first/last name
                },
                "text": "Contact without name",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            text = result[0].text
            assert "1. Jane Smith" in text
            assert "2. nofirstname@test.com" in text

    @pytest.mark.asyncio
    async def test_entity_name_extraction_deals(self):
        """Test entity name extraction for deals."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "deals",
                "entity": {
                    "id": "deal1",
                    "properties": {"dealname": "Big Enterprise Deal"},
                },
                "text": "Big Enterprise Deal description",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            text = result[0].text
            assert "1. Big Enterprise Deal" in text

    @pytest.mark.asyncio
    async def test_entity_name_fallback_to_unnamed(self):
        """Test entity name fallback when no name properties are available."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {"id": "contact1", "properties": {}},  # No name properties
                "text": "Contact with no name",
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            text = result[0].text
            assert "1. Unnamed" in text

    @pytest.mark.asyncio
    async def test_search_text_context_display(self):
        """Test that search results show proper context around matches."""
        long_text = "This is a very long text that contains the word technology somewhere in the middle of the sentence and continues with more content after that important keyword."

        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {
            0: {
                "entity_type": "contacts",
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "text": long_text,
            },
        }

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute(
                {"action": "search", "search_text": "technology"}
            )

            assert len(result) == 1
            text = result[0].text
            # Should show context around "technology" - check for the actual format
            assert (
                "Match: This is a very long text that contains the word technology somewhere in the middle"
                in text
            )

    @pytest.mark.asyncio
    async def test_list_empty_metadata(self):
        """Test list action with empty metadata."""
        mock_manager = MagicMock()
        mock_manager.get_index_stats.return_value = {"status": "ready"}
        mock_manager.entity_metadata = {}

        with patch.object(
            self.tool, "get_embedding_manager", return_value=mock_manager
        ):
            result = await self.tool.execute({"action": "list"})

            assert len(result) == 1
            text = result[0].text
            assert "Total entities: 0" in text
            assert "No indexed data matches your criteria" in text
