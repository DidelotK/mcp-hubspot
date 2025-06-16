"""Integration tests for MCP server resources functionality."""

import json
from unittest.mock import Mock, patch

import mcp.types as types
import pytest

from hubspot_mcp.client import HubSpotClient
from hubspot_mcp.server.handlers import HubSpotHandlers


class TestResourcesIntegration:
    """Integration tests for full MCP resources workflow."""

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
    async def test_full_resources_workflow(self, handlers):
        """Test complete resource workflow from list to read."""
        # Step 1: List all resources
        resources = await handlers.handle_list_resources()
        assert len(resources) == 6

        # Step 2: Read each resource and verify content
        for resource in resources:
            result = await handlers.handle_read_resource(resource.uri)
            assert isinstance(result, types.ReadResourceResult)
            assert len(result.contents) == 1

            content = result.contents[0]
            assert content.uri == resource.uri
            assert len(content.text) > 0

            # Verify JSON resources are valid JSON
            if content.mimeType == "application/json":
                data = json.loads(content.text)
                assert isinstance(data, dict)

            # Verify Markdown resources have proper headers
            elif content.mimeType == "text/markdown":
                assert content.text.startswith("#")

            # Error responses should be plain text
            elif content.mimeType == "text/plain":
                # Should contain error information
                assert "Error:" in content.text

    @pytest.mark.asyncio
    async def test_resource_uri_patterns(self, handlers):
        """Test that resource URIs follow expected patterns."""
        resources = await handlers.handle_list_resources()

        expected_uri_patterns = [
            "hubspot://examples/",
            "hubspot://schemas/",
            "hubspot://config/",
            "hubspot://guides/",
            "hubspot://docs/",
        ]

        found_patterns = set()
        for resource in resources:
            for pattern in expected_uri_patterns:
                if str(resource.uri).startswith(pattern):
                    found_patterns.add(pattern)
                    break

        # All patterns should be represented
        assert len(found_patterns) >= 4  # At least 4 different patterns

    @pytest.mark.asyncio
    async def test_json_resources_structure(self, handlers):
        """Test that JSON resources have expected structure."""
        json_resources = [
            "hubspot://examples/tools",
            "hubspot://schemas/fields",
            "hubspot://config/template",
        ]

        for uri in json_resources:
            result = await handlers.handle_read_resource(uri)
            content = result.contents[0]

            data = json.loads(content.text)

            # Each JSON resource should have a top-level key with metadata
            assert len(data.keys()) == 1  # Single top-level object

            top_level_key = list(data.keys())[0]
            top_level_data = data[top_level_key]

            # Should have version and description
            assert "version" in top_level_data
            assert "description" in top_level_data

    @pytest.mark.asyncio
    async def test_markdown_resources_content_quality(self, handlers):
        """Test that Markdown resources have quality content."""
        markdown_resources = [
            "hubspot://guides/best-practices",
            "hubspot://guides/troubleshooting",
            "hubspot://docs/api-reference",
        ]

        for uri in markdown_resources:
            result = await handlers.handle_read_resource(uri)
            content = result.contents[0]

            # Should have substantial content
            assert len(content.text) > 2000

            # Should have multiple sections
            assert content.text.count("##") >= 3

            # Should have code blocks
            assert "```" in content.text

            # Should have lists
            assert "- " in content.text or "* " in content.text

    @pytest.mark.asyncio
    async def test_cross_resource_consistency(self, handlers):
        """Test consistency across different resources."""
        # Get tool examples
        tools_result = await handlers.handle_read_resource("hubspot://examples/tools")
        tools_content = tools_result.contents[0].text

        # Get field mappings
        fields_result = await handlers.handle_read_resource("hubspot://schemas/fields")
        fields_content = fields_result.contents[0].text

        # Get best practices
        practices_result = await handlers.handle_read_resource(
            "hubspot://guides/best-practices"
        )
        practices_content = practices_result.contents[0].text

        tools_data = json.loads(tools_content)
        fields_data = json.loads(fields_content)

        # Tools and fields should reference same entities
        tools_entities = set()
        for category in tools_data["hubspot_mcp_tool_examples"]["tools"].values():
            for tool_list in category.values():
                if isinstance(tool_list, list):
                    for tool in tool_list:
                        tool_name = tool.get("name", "")
                        if "contacts" in tool_name:
                            tools_entities.add("contacts")
                        if "companies" in tool_name:
                            tools_entities.add("companies")
                        if "deals" in tool_name:
                            tools_entities.add("deals")

        fields_entities = set(fields_data["hubspot_field_mappings"]["entities"].keys())

        # Both should reference core entities
        core_entities = {"contacts", "companies", "deals"}
        assert core_entities.issubset(tools_entities)
        assert core_entities.issubset(fields_entities)

        # Best practices should mention key concepts
        key_concepts = ["caching", "search", "API", "performance"]
        for concept in key_concepts:
            assert concept.lower() in practices_content.lower()

    @pytest.mark.asyncio
    async def test_error_resilience(self, handlers):
        """Test that resource system handles errors gracefully."""
        # Test with completely invalid URI
        result = await handlers.handle_read_resource("invalid://test")
        assert isinstance(result, types.ReadResourceResult)
        assert "Error:" in result.contents[0].text

        # Test with valid scheme but invalid path
        result = await handlers.handle_read_resource("hubspot://nonexistent/resource")
        assert isinstance(result, types.ReadResourceResult)
        assert "Error:" in result.contents[0].text

    @pytest.mark.asyncio
    async def test_resource_metadata_completeness(self, handlers):
        """Test that all resources have complete metadata."""
        resources = await handlers.handle_list_resources()

        for resource in resources:
            # All fields should be non-empty
            assert resource.uri and str(resource.uri).strip()
            assert resource.name and resource.name.strip()
            assert resource.description and resource.description.strip()
            assert resource.mimeType and resource.mimeType.strip()

            # URI should follow expected pattern
            assert str(resource.uri).startswith("hubspot://")

            # MIME type should be valid
            assert resource.mimeType in ["application/json", "text/markdown"]

            # Name should be descriptive
            assert len(resource.name) > 10

            # Description should be substantial
            assert len(resource.description) > 20

    @pytest.mark.asyncio
    async def test_performance_characteristics(self, handlers):
        """Test performance characteristics of resource operations."""
        import time

        # List resources should be fast
        start_time = time.time()
        resources = await handlers.handle_list_resources()
        list_time = time.time() - start_time

        assert list_time < 1.0  # Should complete in under 1 second
        assert len(resources) > 0

        # Reading each resource should be reasonably fast
        for resource in resources[:3]:  # Test first 3 resources
            start_time = time.time()
            result = await handlers.handle_read_resource(resource.uri)
            read_time = time.time() - start_time

            assert read_time < 2.0  # Should complete in under 2 seconds
            assert len(result.contents[0].text) > 0

    @pytest.mark.asyncio
    async def test_resource_content_uniqueness(self, handlers):
        """Test that each resource provides unique content."""
        resources = await handlers.handle_list_resources()
        contents = {}

        # Read all resource contents
        for resource in resources:
            result = await handlers.handle_read_resource(resource.uri)
            contents[resource.uri] = result.contents[0].text

        # Each resource should have unique content
        content_values = list(contents.values())
        unique_contents = set(content_values)

        assert len(unique_contents) == len(content_values)  # All unique

        # Each should have substantial unique content (not just minor variations)
        for i, content1 in enumerate(content_values):
            for j, content2 in enumerate(content_values):
                if i != j:
                    # Calculate basic similarity (shared words)
                    words1 = set(content1.lower().split())
                    words2 = set(content2.lower().split())
                    shared_words = words1.intersection(words2)
                    similarity = len(shared_words) / max(len(words1), len(words2))

                    # Should not be too similar (allowing for some common terms)
                    assert similarity < 0.8  # Less than 80% word overlap

    @pytest.mark.asyncio
    async def test_practical_usage_scenarios(self, handlers):
        """Test practical usage scenarios for resources."""
        # Scenario 1: Developer wants to see all available tools
        tools_result = await handlers.handle_read_resource("hubspot://examples/tools")
        tools_data = json.loads(tools_result.contents[0].text)

        # Should have comprehensive tool examples
        tools = tools_data["hubspot_mcp_tool_examples"]["tools"]
        assert "entity_listing" in tools
        assert "search_and_filtering" in tools
        assert "ai_powered_search" in tools

        # Scenario 2: Developer needs field mappings for integration
        fields_result = await handlers.handle_read_resource("hubspot://schemas/fields")
        fields_data = json.loads(fields_result.contents[0].text)

        # Should have detailed field information
        entities = fields_data["hubspot_field_mappings"]["entities"]
        for entity in ["contacts", "companies", "deals"]:
            assert entity in entities
            assert "standard_properties" in entities[entity]
            assert len(entities[entity]["standard_properties"]) > 5

        # Scenario 3: Developer needs configuration help
        config_result = await handlers.handle_read_resource("hubspot://config/template")
        config_data = json.loads(config_result.contents[0].text)

        # Should have complete configuration guidance
        config = config_data["hubspot_mcp_configuration"]
        assert "environment_variables" in config
        assert "deployment_modes" in config
        assert "HUBSPOT_API_KEY" in config["environment_variables"]["required"]

        # Scenario 4: Developer encounters issues and needs troubleshooting
        trouble_result = await handlers.handle_read_resource(
            "hubspot://guides/troubleshooting"
        )
        trouble_content = trouble_result.contents[0].text

        # Should have practical troubleshooting guidance
        assert "Authentication Errors" in trouble_content
        assert "Performance Issues" in trouble_content
        assert "Solutions:" in trouble_content
