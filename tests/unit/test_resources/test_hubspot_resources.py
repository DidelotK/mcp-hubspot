"""Tests for HubSpot MCP resources functionality."""

import json
from unittest.mock import patch

import mcp.types as types
import pytest

from hubspot_mcp.resources.hubspot_resources import HubSpotResources


class TestHubSpotResources:
    """Test suite for HubSpot resources functionality."""

    def test_get_resource_definitions(self):
        """Test getting all resource definitions."""
        resources = HubSpotResources.get_resource_definitions()

        assert isinstance(resources, list)
        assert len(resources) == 6

        # Check resource types
        resource_names = [resource.name for resource in resources]
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

    def test_tool_examples_resource_definition(self):
        """Test tool examples resource definition."""
        resource = HubSpotResources._get_tool_examples_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://examples/tools"
        assert resource.name == "HubSpot Tool Usage Examples"
        assert "JSON examples" in resource.description
        assert resource.mimeType == "application/json"

    def test_field_mappings_resource_definition(self):
        """Test field mappings resource definition."""
        resource = HubSpotResources._get_field_mappings_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://schemas/fields"
        assert resource.name == "HubSpot Field Mappings"
        assert "field mappings" in resource.description
        assert resource.mimeType == "application/json"

    def test_configuration_template_resource_definition(self):
        """Test configuration template resource definition."""
        resource = HubSpotResources._get_configuration_template_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://config/template"
        assert resource.name == "Server Configuration Template"
        assert "configuration template" in resource.description
        assert resource.mimeType == "application/json"

    def test_best_practices_resource_definition(self):
        """Test best practices resource definition."""
        resource = HubSpotResources._get_best_practices_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://guides/best-practices"
        assert resource.name == "HubSpot MCP Best Practices"
        assert "best practices" in resource.description
        assert resource.mimeType == "text/markdown"

    def test_troubleshooting_resource_definition(self):
        """Test troubleshooting resource definition."""
        resource = HubSpotResources._get_troubleshooting_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://guides/troubleshooting"
        assert resource.name == "Troubleshooting Guide"
        assert "issues" in resource.description
        assert resource.mimeType == "text/markdown"

    def test_api_reference_resource_definition(self):
        """Test API reference resource definition."""
        resource = HubSpotResources._get_api_reference_resource()

        assert isinstance(resource, types.Resource)
        assert str(resource.uri) == "hubspot://docs/api-reference"
        assert resource.name == "HubSpot API Quick Reference"
        assert "API" in resource.description
        assert resource.mimeType == "text/markdown"

    def test_read_resource_tool_examples(self):
        """Test reading tool examples resource."""
        content = HubSpotResources.read_resource("hubspot://examples/tools")

        assert isinstance(content, str)
        # Parse JSON to verify it's valid
        data = json.loads(content)
        assert "hubspot_mcp_tool_examples" in data
        assert "tools" in data["hubspot_mcp_tool_examples"]

        # Check for expected tool categories
        tools = data["hubspot_mcp_tool_examples"]["tools"]
        expected_categories = [
            "entity_listing",
            "properties",
            "search_and_filtering",
            "deal_management",
            "ai_powered_search",
            "cache_and_performance",
        ]
        for category in expected_categories:
            assert category in tools

    def test_read_resource_field_mappings(self):
        """Test reading field mappings resource."""
        content = HubSpotResources.read_resource("hubspot://schemas/fields")

        assert isinstance(content, str)
        # Parse JSON to verify it's valid
        data = json.loads(content)
        assert "hubspot_field_mappings" in data
        assert "entities" in data["hubspot_field_mappings"]

        # Check for expected entities
        entities = data["hubspot_field_mappings"]["entities"]
        expected_entities = ["contacts", "companies", "deals", "engagements"]
        for entity in expected_entities:
            assert entity in entities
            assert "standard_properties" in entities[entity]
            assert "search_filters" in entities[entity]

    def test_read_resource_configuration_template(self):
        """Test reading configuration template resource."""
        content = HubSpotResources.read_resource("hubspot://config/template")

        assert isinstance(content, str)
        # Parse JSON to verify it's valid
        data = json.loads(content)
        assert "hubspot_mcp_configuration" in data
        config = data["hubspot_mcp_configuration"]

        # Check for expected configuration sections
        expected_sections = [
            "environment_variables",
            "deployment_modes",
            "hubspot_setup",
            "performance_tuning",
        ]
        for section in expected_sections:
            assert section in config

        # Check environment variables
        env_vars = config["environment_variables"]
        assert "required" in env_vars
        assert "optional" in env_vars
        assert "HUBSPOT_API_KEY" in env_vars["required"]

    def test_read_resource_best_practices(self):
        """Test reading best practices resource."""
        content = HubSpotResources.read_resource("hubspot://guides/best-practices")

        assert isinstance(content, str)
        assert "# HubSpot MCP Best Practices" in content
        assert "Performance Optimization" in content
        assert "Caching Strategy" in content
        assert "Search Best Practices" in content
        assert "Security Best Practices" in content

    def test_read_resource_troubleshooting(self):
        """Test reading troubleshooting resource."""
        content = HubSpotResources.read_resource("hubspot://guides/troubleshooting")

        assert isinstance(content, str)
        assert "# HubSpot MCP Troubleshooting Guide" in content
        assert "Authentication Errors" in content
        assert "Performance Issues" in content
        assert "Search & Filtering Issues" in content
        assert "Deal Management Issues" in content

    def test_read_resource_api_reference(self):
        """Test reading API reference resource."""
        content = HubSpotResources.read_resource("hubspot://docs/api-reference")

        assert isinstance(content, str)
        assert "# HubSpot API Quick Reference" in content
        assert "API Endpoints" in content
        assert "/crm/v3/objects/" in content
        assert "Standard Properties" in content
        assert "Filter Operators" in content
        assert "Required Scopes" in content

    def test_read_resource_invalid_uri(self):
        """Test reading resource with invalid URI."""
        with pytest.raises(ValueError, match="Resource not found"):
            HubSpotResources.read_resource("hubspot://invalid/resource")

    def test_tool_examples_contain_all_categories(self):
        """Test that tool examples contain all major tool categories."""
        content = HubSpotResources._generate_tool_examples()
        data = json.loads(content)
        tools = data["hubspot_mcp_tool_examples"]["tools"]

        # Verify entity listing tools are present
        entity_listing = tools["entity_listing"]
        assert "list_hubspot_contacts" in entity_listing
        assert "list_hubspot_companies" in entity_listing
        assert "list_hubspot_deals" in entity_listing
        assert "list_hubspot_engagements" in entity_listing

        # Verify each tool has proper structure
        contact_examples = entity_listing["list_hubspot_contacts"]
        assert isinstance(contact_examples, list)
        for example in contact_examples:
            assert "name" in example
            assert "arguments" in example
            assert "description" in example

    def test_field_mappings_contain_all_entities(self):
        """Test that field mappings contain all entity types."""
        content = HubSpotResources._generate_field_mappings()
        data = json.loads(content)
        entities = data["hubspot_field_mappings"]["entities"]

        # Test contacts mapping
        contacts = entities["contacts"]
        assert "standard_properties" in contacts
        assert "search_filters" in contacts

        # Verify property structure
        for prop in contacts["standard_properties"]:
            assert "name" in prop
            assert "type" in prop
            assert "description" in prop

        # Verify filter structure
        for field, operator in contacts["search_filters"].items():
            assert isinstance(field, str)
            assert operator in ["CONTAINS_TOKEN", "EQ", "GT", "LT"]

    def test_configuration_template_completeness(self):
        """Test that configuration template is comprehensive."""
        content = HubSpotResources._generate_configuration_template()
        data = json.loads(content)
        config = data["hubspot_mcp_configuration"]

        # Test required environment variables
        required_vars = config["environment_variables"]["required"]
        assert "HUBSPOT_API_KEY" in required_vars
        assert "description" in required_vars["HUBSPOT_API_KEY"]
        assert "example" in required_vars["HUBSPOT_API_KEY"]

        # Test deployment modes
        deployment_modes = config["deployment_modes"]
        assert "claude_desktop" in deployment_modes
        assert "web_server" in deployment_modes

        # Test HubSpot setup
        hubspot_setup = config["hubspot_setup"]
        assert "steps" in hubspot_setup
        assert "required_scopes" in hubspot_setup
        assert isinstance(hubspot_setup["steps"], list)
        assert len(hubspot_setup["steps"]) > 0

    def test_markdown_guides_formatting(self):
        """Test that markdown guides are properly formatted."""
        # Test best practices guide
        best_practices = HubSpotResources._generate_best_practices()
        assert best_practices.startswith("# HubSpot MCP Best Practices")
        assert "## " in best_practices  # Has section headers
        assert "```json" in best_practices  # Has code blocks
        assert "- " in best_practices  # Has bullet points

        # Test troubleshooting guide
        troubleshooting = HubSpotResources._generate_troubleshooting()
        assert troubleshooting.startswith("# HubSpot MCP Troubleshooting Guide")
        assert "**Symptoms:**" in troubleshooting
        assert "**Solutions:**" in troubleshooting

        # Test API reference guide
        api_reference = HubSpotResources._generate_api_reference()
        assert api_reference.startswith("# HubSpot API Quick Reference")
        assert "```" in api_reference  # Has code blocks
        assert "GET /crm/v3/objects/" in api_reference

    def test_json_resource_validity(self):
        """Test that all JSON resources are valid JSON."""
        json_resources = [
            "hubspot://examples/tools",
            "hubspot://schemas/fields",
            "hubspot://config/template",
        ]

        for uri in json_resources:
            content = HubSpotResources.read_resource(uri)
            # Should not raise exception
            data = json.loads(content)
            assert isinstance(data, dict)

    def test_markdown_resource_content(self):
        """Test that markdown resources contain expected content."""
        markdown_resources = [
            "hubspot://guides/best-practices",
            "hubspot://guides/troubleshooting",
            "hubspot://docs/api-reference",
        ]

        for uri in markdown_resources:
            content = HubSpotResources.read_resource(uri)
            assert isinstance(content, str)
            assert len(content) > 1000  # Substantial content
            assert content.startswith("#")  # Markdown header

    def test_all_tools_documented(self):
        """Test that all 18 tools are documented in examples."""
        content = HubSpotResources._generate_tool_examples()
        examples_text = json.dumps(json.loads(content))

        # List of all expected tools
        expected_tools = [
            "list_hubspot_contacts",
            "list_hubspot_companies",
            "list_hubspot_deals",
            "list_hubspot_engagements",
            "get_hubspot_contact_properties",
            "get_hubspot_company_properties",
            "get_hubspot_deal_properties",
            "search_hubspot_contacts",
            "search_hubspot_companies",
            "search_hubspot_deals",
            "get_deal_by_name",
            "create_deal",
            "update_deal",
            "semantic_search_hubspot",
            "manage_hubspot_embeddings",
            "browse_hubspot_indexed_data",
            "load_hubspot_entities_to_cache",
            "manage_hubspot_cache",
        ]

        for tool in expected_tools:
            assert tool in examples_text, f"Tool {tool} not found in examples"

    def test_resource_content_consistency(self):
        """Test that resource content is consistent across resources."""
        # Get field mappings
        field_content = HubSpotResources.read_resource("hubspot://schemas/fields")
        field_data = json.loads(field_content)
        entities = list(field_data["hubspot_field_mappings"]["entities"].keys())

        # Get tool examples
        tool_content = HubSpotResources.read_resource("hubspot://examples/tools")
        tool_data = json.loads(tool_content)

        # Verify entities are mentioned in tools
        for entity in entities:
            if entity != "engagements":  # engagements tools use different naming
                assert entity in json.dumps(
                    tool_data
                ), f"Entity {entity} not found in tool examples"

    def test_error_handling_coverage(self):
        """Test that error scenarios are covered in troubleshooting guide."""
        content = HubSpotResources._generate_troubleshooting()

        # Check that common error scenarios are covered
        error_scenarios = [
            "Invalid API key",
            "Insufficient permissions",
            "Slow response times",
            "No results found",
            "Deal creation failed",
        ]

        for scenario in error_scenarios:
            assert scenario in content, f"Error scenario '{scenario}' not covered"

    def test_api_reference_completeness(self):
        """Test that API reference covers all essential information."""
        content = HubSpotResources._generate_api_reference()

        # Check for essential API information
        api_elements = [
            "https://api.hubapi.com",
            "Authorization: Bearer",
            "/crm/v3/objects/contacts",
            "/crm/v3/objects/companies",
            "/crm/v3/objects/deals",
            "CONTAINS_TOKEN",
            "crm.objects.contacts.read",
            "401 Unauthorized",
            "429 Too Many Requests",
        ]

        for element in api_elements:
            assert element in content, f"API element '{element}' missing from reference"
