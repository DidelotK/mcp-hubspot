"""Unit tests for BulkCacheLoaderTool."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from hubspot_mcp.client.hubspot_client import HubSpotClient
from hubspot_mcp.tools.bulk_cache_loader import BulkCacheLoaderTool


class TestBulkCacheLoaderTool:
    """Test cases for BulkCacheLoaderTool."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock(spec=HubSpotClient)
        client.api_key = "test-api-key"
        return client

    @pytest.fixture
    def tool(self, mock_client):
        """Create a BulkCacheLoaderTool instance."""
        return BulkCacheLoaderTool(client=mock_client)

    @pytest.fixture
    def sample_properties(self):
        """Sample property definitions."""
        return [
            {
                "name": "firstname",
                "label": "First Name",
                "type": "string",
                "fieldType": "text",
                "calculated": False,
            },
            {
                "name": "lastname",
                "label": "Last Name",
                "type": "string",
                "fieldType": "text",
                "calculated": False,
            },
            {
                "name": "email",
                "label": "Email",
                "type": "string",
                "fieldType": "text",
                "calculated": False,
            },
            {
                "name": "hs_calculated_field",
                "label": "Calculated Field",
                "type": "string",
                "fieldType": "text",
                "calculated": True,  # Should be filtered out
            },
            {
                "name": "id",  # System property - should be filtered out
                "label": "ID",
                "type": "string",
                "fieldType": "text",
                "calculated": False,
            },
        ]

    @pytest.fixture
    def sample_contacts(self):
        """Sample contact data."""
        return [
            {
                "id": "1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john@example.com",
                    "createdate": "2024-01-01T00:00:00.000Z",
                },
            },
            {
                "id": "2",
                "properties": {
                    "firstname": "Jane",
                    "lastname": "Smith",
                    "email": "jane@example.com",
                    "createdate": "2024-01-02T00:00:00.000Z",
                },
            },
        ]

    @pytest.fixture
    def sample_companies(self):
        """Sample company data."""
        return [
            {
                "id": "1",
                "properties": {
                    "name": "TechCorp",
                    "domain": "techcorp.com",
                    "industry": "Technology",
                    "createdate": "2024-01-01T00:00:00.000Z",
                },
            },
            {
                "id": "2",
                "properties": {
                    "name": "HealthCorp",
                    "domain": "healthcorp.com",
                    "industry": "Healthcare",
                    "createdate": "2024-01-02T00:00:00.000Z",
                },
            },
        ]

    def test_tool_definition(self, tool):
        """Test tool definition."""
        definition = tool.get_tool_definition()

        assert definition.name == "load_hubspot_entities_to_cache"
        assert "bulk load" in definition.description.lower()

        # Check schema
        schema = definition.inputSchema
        assert schema["type"] == "object"
        assert "entity_type" in schema["properties"]
        assert "build_embeddings" in schema["properties"]
        assert "max_entities" in schema["properties"]
        assert schema["required"] == ["entity_type"]

        # Check entity_type enum
        entity_type_schema = schema["properties"]["entity_type"]
        assert entity_type_schema["enum"] == ["contacts", "companies"]

    @pytest.mark.asyncio
    async def test_execute_invalid_entity_type(self, tool):
        """Test execution with invalid entity type."""
        result = await tool.execute({"entity_type": "invalid"})

        assert len(result) == 1
        assert "❌ **Error**" in result[0].text
        assert "entity_type must be 'contacts' or 'companies'" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_contacts_success(
        self, tool, sample_properties, sample_contacts
    ):
        """Test successful execution for contacts."""
        # Mock the cached client calls
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,  # get_contact_properties
            sample_contacts,  # get_all_contacts_with_pagination
        ]

        # Mock embedding functionality
        tool.enable_embeddings = True
        tool._embedding_manager = Mock()
        tool._build_embedding_index_from_entities = AsyncMock(
            return_value={
                "success": True,
                "entities_indexed": len(sample_contacts),
                "index_stats": {
                    "total_entities": len(sample_contacts),
                    "dimension": 384,
                    "index_type": "flat",
                },
            }
        )

        result = await tool.execute(
            {
                "entity_type": "contacts",
                "build_embeddings": True,
                "max_entities": 10000,
            }
        )

        assert len(result) == 1
        result_text = result[0].text

        # Check main sections
        assert "🚀 **Bulk Loading Contacts to Cache**" in result_text
        assert "📋 **Step 1**: Retrieving all contacts properties" in result_text
        assert (
            "📥 **Step 2**: Loading all contacts with complete property data"
            in result_text
        )
        assert (
            "🧠 **Step 3**: Building FAISS embeddings for semantic search"
            in result_text
        )
        assert "🎉 **Cache Loading Complete**" in result_text

        # Check data counts
        assert f"Loaded {len(sample_contacts)} contacts" in result_text
        assert "Built embeddings for 2 contacts" in result_text

        # Verify calls
        tool._cached_client_call.assert_any_call("get_contact_properties")
        tool._cached_client_call.assert_any_call(
            "get_all_contacts_with_pagination",
            extra_properties=["firstname", "lastname", "email"],  # Filtered properties
            max_entities=10000,
        )

    @pytest.mark.asyncio
    async def test_execute_companies_success(
        self, tool, sample_properties, sample_companies
    ):
        """Test successful execution for companies."""
        # Mock the cached client calls
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,  # get_company_properties
            sample_companies,  # get_all_companies_with_pagination
        ]

        # Disable embeddings for this test
        tool.enable_embeddings = False

        result = await tool.execute(
            {
                "entity_type": "companies",
                "build_embeddings": False,
                "max_entities": 5000,
            }
        )

        assert len(result) == 1
        result_text = result[0].text

        # Check main sections
        assert "🚀 **Bulk Loading Companies to Cache**" in result_text
        assert (
            "ℹ️ **Step 3**: Skipped embedding generation (build_embeddings=false)"
            in result_text
        )
        assert "🎉 **Cache Loading Complete**" in result_text

        # Check data counts
        assert f"Loaded {len(sample_companies)} companies" in result_text
        assert "Embeddings: ❌ Not built" in result_text

        # Verify calls
        tool._cached_client_call.assert_any_call("get_company_properties")
        tool._cached_client_call.assert_any_call(
            "get_all_companies_with_pagination",
            extra_properties=["firstname", "lastname", "email"],  # Filtered properties
            max_entities=5000,
        )

    @pytest.mark.asyncio
    async def test_execute_no_properties_found(self, tool):
        """Test execution when no properties are found."""
        tool._cached_client_call = AsyncMock(return_value=[])

        result = await tool.execute({"entity_type": "contacts"})

        assert len(result) == 1
        assert "❌ **Error**: Could not retrieve contacts properties" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_no_entities_found(self, tool, sample_properties):
        """Test execution when no entities are found."""
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,  # get_contact_properties
            [],  # get_all_contacts_with_pagination (empty)
        ]

        result = await tool.execute({"entity_type": "contacts"})

        assert len(result) == 1
        assert "❌ **Error**: No contacts found to load" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_embedding_failure(
        self, tool, sample_properties, sample_contacts
    ):
        """Test execution when embedding building fails."""
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,
            sample_contacts,
        ]

        # Mock embedding failure
        tool.enable_embeddings = True
        tool._build_embedding_index_from_entities = AsyncMock(
            return_value={
                "success": False,
                "error": "Embedding model failed to load",
            }
        )

        result = await tool.execute(
            {
                "entity_type": "contacts",
                "build_embeddings": True,
            }
        )

        assert len(result) == 1
        result_text = result[0].text

        assert (
            "⚠️ Failed to build embeddings: Embedding model failed to load"
            in result_text
        )
        assert "🎉 **Cache Loading Complete**" in result_text  # Should still complete

    @pytest.mark.asyncio
    async def test_execute_with_exception(self, tool):
        """Test execution when an exception occurs."""
        tool._cached_client_call = AsyncMock(side_effect=Exception("API Error"))

        with patch.object(tool, "handle_error") as mock_handle_error:
            mock_handle_error.return_value = [Mock(text="Error handled")]

            result = await tool.execute({"entity_type": "contacts"})

            mock_handle_error.assert_called_once()
            assert len(result) == 1

    def test_property_filtering(self, tool, sample_properties):
        """Test that properties are correctly filtered."""
        # Test the property filtering logic directly
        property_names = []
        system_properties = {
            "id",
            "createddate",
            "lastmodifieddate",
            "createdate",
            "hs_lastmodifieddate",
            "hs_object_id",
            "hs_created_by",
            "hs_updated_by",
            "archived",
            "archivedAt",
        }

        for prop in sample_properties:
            prop_name = prop.get("name", "")
            if prop_name and prop_name not in system_properties:
                if not prop.get("calculated", False):
                    property_names.append(prop_name)

        # Should include: firstname, lastname, email
        # Should exclude: hs_calculated_field (calculated), id (system property)
        assert "firstname" in property_names
        assert "lastname" in property_names
        assert "email" in property_names
        assert "hs_calculated_field" not in property_names
        assert "id" not in property_names
        assert len(property_names) == 3

    @pytest.mark.asyncio
    async def test_load_all_entities_with_properties(self, tool, sample_contacts):
        """Test the _load_all_entities_with_properties method."""
        tool._cached_client_call = AsyncMock(return_value=sample_contacts)

        result = await tool._load_all_entities_with_properties(
            "contacts", ["firstname", "lastname", "email"], 10000
        )

        assert result == sample_contacts
        tool._cached_client_call.assert_called_once_with(
            "get_all_contacts_with_pagination",
            extra_properties=["firstname", "lastname", "email"],
            max_entities=10000,
        )

    @pytest.mark.asyncio
    async def test_build_embedding_index_from_entities_success(
        self, tool, sample_contacts
    ):
        """Test successful embedding index building."""
        # Mock embedding manager
        tool.enable_embeddings = True
        tool._embedding_manager = Mock()
        tool._embedding_manager.build_index = Mock()
        tool._embedding_manager.get_index_stats = Mock(
            return_value={
                "status": "ready",
                "total_entities": 2,
                "dimension": 384,
                "index_type": "flat",
            }
        )

        result = await tool._build_embedding_index_from_entities(
            "contacts", sample_contacts
        )

        assert result["success"] is True
        assert result["entity_type"] == "contacts"
        assert result["entities_indexed"] == 2
        assert result["index_stats"]["total_entities"] == 2

        tool._embedding_manager.build_index.assert_called_once_with(
            sample_contacts, "contacts"
        )

    @pytest.mark.asyncio
    async def test_build_embedding_index_from_entities_disabled(
        self, tool, sample_contacts
    ):
        """Test embedding index building when embeddings are disabled."""
        tool.enable_embeddings = False

        result = await tool._build_embedding_index_from_entities(
            "contacts", sample_contacts
        )

        assert result["success"] is False
        assert result["error"] == "Embeddings not enabled"

    @pytest.mark.asyncio
    async def test_build_embedding_index_from_entities_no_manager(
        self, tool, sample_contacts
    ):
        """Test embedding index building when embedding manager is None."""
        tool.enable_embeddings = True
        tool._embedding_manager = None

        result = await tool._build_embedding_index_from_entities(
            "contacts", sample_contacts
        )

        assert result["success"] is False
        assert result["error"] == "Embeddings not enabled"

    @pytest.mark.asyncio
    async def test_build_embedding_index_from_entities_exception(
        self, tool, sample_contacts
    ):
        """Test embedding index building when an exception occurs."""
        tool.enable_embeddings = True
        tool._embedding_manager = Mock()
        tool._embedding_manager.build_index = Mock(
            side_effect=Exception("Build failed")
        )

        result = await tool._build_embedding_index_from_entities(
            "contacts", sample_contacts
        )

        assert result["success"] is False
        assert result["error"] == "Build failed"

    @pytest.mark.asyncio
    async def test_embeddings_not_available_warning(
        self, tool, sample_properties, sample_contacts
    ):
        """Test warning when embeddings are enabled but not available."""
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,
            sample_contacts,
        ]

        # Enable embeddings but set manager to None
        tool.enable_embeddings = True
        tool._embedding_manager = None

        result = await tool.execute(
            {
                "entity_type": "contacts",
                "build_embeddings": True,  # Requested but not available
            }
        )

        assert len(result) == 1
        result_text = result[0].text

        assert "⚠️ Failed to build embeddings: Embeddings not enabled" in result_text

    def test_inheritance_from_enhanced_base_tool(self, tool):
        """Test that BulkCacheLoaderTool inherits from EnhancedBaseTool."""
        from hubspot_mcp.tools.enhanced_base import EnhancedBaseTool

        assert isinstance(tool, EnhancedBaseTool)

    @pytest.mark.asyncio
    async def test_max_entities_zero_means_no_limit(
        self, tool, sample_properties, sample_contacts
    ):
        """Test that max_entities=0 means no limit."""
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,
            sample_contacts,
        ]
        tool.enable_embeddings = False

        result = await tool.execute(
            {
                "entity_type": "contacts",
                "max_entities": 0,  # No limit
                "build_embeddings": False,
            }
        )

        assert len(result) == 1

        # Verify that max_entities=0 is passed through
        tool._cached_client_call.assert_any_call(
            "get_all_contacts_with_pagination",
            extra_properties=["firstname", "lastname", "email"],
            max_entities=0,
        )

    @pytest.mark.asyncio
    async def test_default_parameters(self, tool, sample_properties, sample_contacts):
        """Test execution with default parameters."""
        tool._cached_client_call = AsyncMock()
        tool._cached_client_call.side_effect = [
            sample_properties,
            sample_contacts,
        ]
        tool.enable_embeddings = True
        tool._build_embedding_index_from_entities = AsyncMock(
            return_value={
                "success": True,
                "entities_indexed": 2,
                "index_stats": {},
            }
        )

        # Call with only required parameter
        result = await tool.execute({"entity_type": "contacts"})

        assert len(result) == 1

        # Verify defaults: build_embeddings=True, max_entities=10000
        tool._cached_client_call.assert_any_call(
            "get_all_contacts_with_pagination",
            extra_properties=["firstname", "lastname", "email"],
            max_entities=10000,  # Default value
        )

        # Should attempt to build embeddings by default
        tool._build_embedding_index_from_entities.assert_called_once()
