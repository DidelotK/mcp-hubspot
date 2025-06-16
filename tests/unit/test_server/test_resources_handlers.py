"""Tests for MCP server resource handlers."""

from unittest.mock import AsyncMock, MagicMock, Mock

import mcp.types as types
import pytest

from hubspot_mcp.client import HubSpotClient
from hubspot_mcp.server.handlers import HubSpotHandlers


class TestResourceHandlers:
    """Test suite for resource handlers functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        client = Mock(spec=HubSpotClient)
        return client

    @pytest.fixture
    def handlers(self, mock_client):
        """Create handlers instance with mock client."""
        return HubSpotHandlers(mock_client)

    @pytest.mark.asyncio
    async def test_handle_list_resources(self, handlers):
        """Test listing all available resources."""
        result = await handlers.handle_list_resources()

        assert isinstance(result, list)
        assert len(result) == 6

        # Check that all expected resources are present
        resource_names = [resource.name for resource in result]
        expected_names = [
            "HubSpot Tool Usage Examples",
            "HubSpot Field Mappings",
            "Server Configuration Template",
            "HubSpot MCP Best Practices",
            "Troubleshooting Guide",
            "HubSpot API Quick Reference",
        ]

        for expected_name in expected_names:
            assert expected_name in resource_names

        # Check resource structure
        for resource in result:
            assert isinstance(resource, types.Resource)
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert hasattr(resource, "description")
            assert hasattr(resource, "mimeType")

    @pytest.mark.asyncio
    async def test_handle_list_resources_error_handling(self, handlers):
        """Test error handling in list resources."""
        # Mock the resources to raise an exception
        handlers.resources.get_resource_definitions = Mock(
            side_effect=Exception("Test error")
        )

        result = await handlers.handle_list_resources()
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_handle_read_resource_tool_examples(self, handlers):
        """Test reading tool examples resource."""
        uri = "hubspot://examples/tools"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        assert isinstance(result.contents, list)
        assert len(result.contents) == 1

        content = result.contents[0]
        assert isinstance(content, types.TextResourceContents)
        assert str(content.uri) == uri
        assert content.mimeType == "application/json"
        assert content.text is not None
        assert len(content.text) > 0

        # Verify it's valid JSON
        import json

        data = json.loads(content.text)
        assert "hubspot_mcp_tool_examples" in data

    @pytest.mark.asyncio
    async def test_handle_read_resource_field_mappings(self, handlers):
        """Test reading field mappings resource."""
        uri = "hubspot://schemas/fields"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "application/json"

        # Verify it's valid JSON
        import json

        data = json.loads(content.text)
        assert "hubspot_field_mappings" in data

    @pytest.mark.asyncio
    async def test_handle_read_resource_configuration_template(self, handlers):
        """Test reading configuration template resource."""
        uri = "hubspot://config/template"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "application/json"

        # Verify it's valid JSON
        import json

        data = json.loads(content.text)
        assert "hubspot_mcp_configuration" in data

    @pytest.mark.asyncio
    async def test_handle_read_resource_best_practices(self, handlers):
        """Test reading best practices resource."""
        uri = "hubspot://guides/best-practices"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "text/markdown"
        assert "# HubSpot MCP Best Practices" in content.text

    @pytest.mark.asyncio
    async def test_handle_read_resource_troubleshooting(self, handlers):
        """Test reading troubleshooting resource."""
        uri = "hubspot://guides/troubleshooting"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "text/markdown"
        assert "# HubSpot MCP Troubleshooting Guide" in content.text

    @pytest.mark.asyncio
    async def test_handle_read_resource_api_reference(self, handlers):
        """Test reading API reference resource."""
        uri = "hubspot://docs/api-reference"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "text/markdown"
        assert "# HubSpot API Quick Reference" in content.text

    @pytest.mark.asyncio
    async def test_handle_read_resource_invalid_uri(self, handlers):
        """Test reading resource with invalid URI."""
        uri = "hubspot://invalid/resource"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "text/plain"
        assert "Error:" in content.text

    @pytest.mark.asyncio
    async def test_handle_read_resource_error_handling(self, handlers):
        """Test error handling in read resource."""
        # Mock the resources object to raise an exception
        handlers.resources.read_resource = Mock(side_effect=Exception("Test error"))

        uri = "hubspot://examples/tools"
        result = await handlers.handle_read_resource(uri)

        assert isinstance(result, types.ReadResourceResult)
        content = result.contents[0]
        assert str(content.uri) == uri
        assert content.mimeType == "text/plain"
        assert "Error:" in content.text
        assert "Test error" in content.text

    @pytest.mark.asyncio
    async def test_mime_type_determination(self, handlers):
        """Test that MIME types are correctly determined."""
        # Test JSON resources
        json_uris = [
            "hubspot://examples/tools",
            "hubspot://schemas/fields",
            "hubspot://config/template",
        ]

        for uri in json_uris:
            result = await handlers.handle_read_resource(uri)
            content = result.contents[0]
            assert content.mimeType == "application/json"

        # Test Markdown resources
        markdown_uris = [
            "hubspot://guides/best-practices",
            "hubspot://guides/troubleshooting",
            "hubspot://docs/api-reference",
        ]

        for uri in markdown_uris:
            result = await handlers.handle_read_resource(uri)
            content = result.contents[0]
            assert content.mimeType == "text/markdown"

    def test_resources_object_initialization(self, handlers):
        """Test that resources object is properly initialized."""
        assert handlers.resources is not None
        assert hasattr(handlers.resources, "get_resource_definitions")
        assert hasattr(handlers.resources, "read_resource")

    @pytest.mark.asyncio
    async def test_resource_content_not_empty(self, handlers):
        """Test that all resources return non-empty content."""
        all_uris = [
            "hubspot://examples/tools",
            "hubspot://schemas/fields",
            "hubspot://config/template",
            "hubspot://guides/best-practices",
            "hubspot://guides/troubleshooting",
            "hubspot://docs/api-reference",
        ]

        for uri in all_uris:
            result = await handlers.handle_read_resource(uri)
            content = result.contents[0]
            assert len(content.text) > 100  # Substantial content
            assert content.text.strip() != ""  # Not just whitespace

    @pytest.mark.asyncio
    async def test_resource_consistency(self, handlers):
        """Test that resource definitions match readable resources."""
        # Get all resource definitions
        resources = await handlers.handle_list_resources()

        # Try to read each resource
        for resource in resources:
            result = await handlers.handle_read_resource(str(resource.uri))
            assert isinstance(result, types.ReadResourceResult)
            assert len(result.contents) == 1

            content = result.contents[0]
            assert str(content.uri) == str(resource.uri)
            # MIME type should match expected type from definition
            if resource.mimeType == "application/json":
                assert content.mimeType == "application/json"
            elif resource.mimeType == "text/markdown":
                assert content.mimeType == "text/markdown"
