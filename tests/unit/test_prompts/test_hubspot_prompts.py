"""Tests for HubSpot MCP prompts."""

import mcp.types as types
import pytest

from src.hubspot_mcp.prompts.hubspot_prompts import HubSpotPrompts


class TestHubSpotPrompts:
    """Test cases for HubSpot prompts functionality."""

    def test_get_prompt_definitions(self):
        """Test that get_prompt_definitions returns all expected prompts."""
        prompts = HubSpotPrompts.get_prompt_definitions()

        assert len(prompts) == 5
        prompt_names = [prompt.name for prompt in prompts]

        expected_prompts = [
            "hubspot_basics_guide",
            "hubspot_search_guide",
            "hubspot_ai_search_guide",
            "hubspot_performance_guide",
            "hubspot_api_compatibility",
        ]

        for expected_prompt in expected_prompts:
            assert expected_prompt in prompt_names

    def test_prompt_definitions_structure(self):
        """Test that prompt definitions have correct structure."""
        prompts = HubSpotPrompts.get_prompt_definitions()

        for prompt in prompts:
            assert isinstance(prompt, types.Prompt)
            assert prompt.name
            assert prompt.description
            assert isinstance(prompt.arguments, list)

    def test_basics_prompt_definition(self):
        """Test the basics prompt definition."""
        prompt = HubSpotPrompts._get_hubspot_basics_prompt()

        assert prompt.name == "hubspot_basics_guide"
        assert "getting started" in prompt.description.lower()
        assert len(prompt.arguments) == 1
        assert prompt.arguments[0].name == "entity_type"
        assert not prompt.arguments[0].required

    def test_search_guide_prompt_definition(self):
        """Test the search guide prompt definition."""
        prompt = HubSpotPrompts._get_hubspot_search_guide_prompt()

        assert prompt.name == "hubspot_search_guide"
        assert "search" in prompt.description.lower()
        assert len(prompt.arguments) == 2

        arg_names = [arg.name for arg in prompt.arguments]
        assert "search_type" in arg_names
        assert "entity_type" in arg_names

    def test_ai_search_prompt_definition(self):
        """Test the AI search prompt definition."""
        prompt = HubSpotPrompts._get_hubspot_ai_search_prompt()

        assert prompt.name == "hubspot_ai_search_guide"
        assert (
            "ai" in prompt.description.lower()
            or "semantic" in prompt.description.lower()
        )
        assert len(prompt.arguments) == 1
        assert prompt.arguments[0].name == "use_case"

    def test_performance_prompt_definition(self):
        """Test the performance prompt definition."""
        prompt = HubSpotPrompts._get_hubspot_performance_prompt()

        assert prompt.name == "hubspot_performance_guide"
        assert "performance" in prompt.description.lower()
        assert len(prompt.arguments) == 1
        assert prompt.arguments[0].name == "optimization_focus"

    def test_api_compatibility_prompt_definition(self):
        """Test the API compatibility prompt definition."""
        prompt = HubSpotPrompts._get_hubspot_api_compatibility_prompt()

        assert prompt.name == "hubspot_api_compatibility"
        assert "api" in prompt.description.lower()
        assert len(prompt.arguments) == 2

        arg_names = [arg.name for arg in prompt.arguments]
        assert "api_endpoint" in arg_names
        assert "parameter_type" in arg_names

    def test_generate_prompt_content_basics_default(self):
        """Test generating basics content with default arguments."""
        content = HubSpotPrompts.generate_prompt_content("hubspot_basics_guide", {})

        assert "HubSpot MCP Server - Getting Started Guide" in content
        assert "18 tools" in content
        assert "📋 Entity Listing" in content
        assert "🔧 Properties" in content
        assert "🔍 Search & Filtering" in content
        assert "💼 Deal Management" in content
        assert "🤖 AI-Powered Search" in content
        assert "⚡ Cache & Performance" in content
        assert "API Compatibility" in content
        assert "https://developers.hubspot.com/docs/api/overview" in content

    def test_generate_prompt_content_basics_with_entity_type(self):
        """Test generating basics content with entity type specified."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_basics_guide", {"entity_type": "contacts"}
        )

        assert "Focused Guide: Contacts" in content
        assert "list_hubspot_contacts" in content
        assert "get_hubspot_contact_properties" in content
        assert "search_hubspot_contacts" in content
        assert "https://developers.hubspot.com/docs/api/contacts" in content

    def test_generate_prompt_content_search_guide_basic(self):
        """Test generating search guide content with basic search type."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide", {"search_type": "basic"}
        )

        assert "HubSpot Search & Filtering Guide" in content
        assert "CRITICAL: HubSpot API Compatibility" in content
        assert "search tools use identical parameters" in content
        assert "list_hubspot_contacts" in content
        assert "search_hubspot_deals" in content
        assert "Common Filter Patterns" in content

    def test_generate_prompt_content_search_guide_api_params(self):
        """Test generating search guide content with API parameters focus."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide", {"search_type": "api_params"}
        )

        assert "Advanced API Parameters" in content
        assert "POST /crm/v3/objects/{objectType}/search" in content
        assert "filterGroups" in content
        assert "CONTAINS_TOKEN" in content
        assert "search_hubspot_contacts" in content

    def test_generate_prompt_content_search_guide_with_entity_type(self):
        """Test generating search guide content with entity type specified."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide", {"entity_type": "deals"}
        )

        assert "Deals-Specific Search" in content
        assert "search_hubspot_deals" in content
        assert "https://developers.hubspot.com/docs/api/crm/deals" in content

    def test_generate_prompt_content_ai_search_setup(self):
        """Test generating AI search content for setup use case."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_ai_search_guide", {"use_case": "setup"}
        )

        assert "Initial Setup Guide" in content
        assert "load_hubspot_entities_to_cache" in content
        assert "manage_hubspot_embeddings" in content
        assert "semantic_search_hubspot" in content
        assert "build_embeddings: true" in content

    def test_generate_prompt_content_ai_search_search(self):
        """Test generating AI search content for search use case."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_ai_search_guide", {"use_case": "search"}
        )

        assert "Advanced Search Techniques" in content
        assert "Natural Language Queries" in content
        assert "software engineers" in content
        assert "Search Modes" in content
        assert "semantic_weight" in content

    def test_generate_prompt_content_ai_search_troubleshooting(self):
        """Test generating AI search content for troubleshooting use case."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_ai_search_guide", {"use_case": "troubleshooting"}
        )

        assert "Troubleshooting AI Search" in content
        assert "No embedding manager available" in content
        assert "Index not ready" in content
        assert "Poor search results" in content
        assert "browse_hubspot_indexed_data" in content

    def test_generate_prompt_content_ai_search_default(self):
        """Test generating AI search content with default use case."""
        content = HubSpotPrompts.generate_prompt_content("hubspot_ai_search_guide", {})

        assert "HubSpot AI-Powered Search Guide" in content
        assert "FAISS vector search" in content
        assert "semantic_search_hubspot" in content
        assert "Quick Setup Workflow" in content

    def test_generate_prompt_content_performance_default(self):
        """Test generating performance content with default focus."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_performance_guide", {}
        )

        assert "HubSpot Performance Optimization Guide" in content
        assert "Performance Tools" in content
        assert "load_hubspot_entities_to_cache" in content
        assert "manage_hubspot_cache" in content
        assert "Optimization Strategies" in content

    def test_generate_prompt_content_performance_caching_focus(self):
        """Test generating performance content with caching focus."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_performance_guide", {"optimization_focus": "caching"}
        )

        assert "Cache Optimization Deep Dive" in content
        assert "3600 seconds" in content
        assert "Hit rate > 70%" in content
        assert "manage_hubspot_cache" in content

    def test_generate_prompt_content_performance_bulk_loading_focus(self):
        """Test generating performance content with bulk loading focus."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_performance_guide", {"optimization_focus": "bulk_loading"}
        )

        assert "Bulk Loading Best Practices" in content
        assert "load_hubspot_entities_to_cache" in content
        assert "< 1,000 entities" in content
        assert "500-1000 entities/minute" in content

    def test_generate_prompt_content_performance_embeddings_focus(self):
        """Test generating performance content with embeddings focus."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_performance_guide", {"optimization_focus": "embeddings"}
        )

        assert "Embedding Performance Optimization" in content
        assert "Index Type Selection" in content
        assert "Flat" in content
        assert "IVF" in content
        assert "manage_hubspot_embeddings" in content

    def test_generate_prompt_content_api_compatibility_default(self):
        """Test generating API compatibility content with default arguments."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {}
        )

        assert "HubSpot API Compatibility Guide" in content
        assert "100% compatible with the HubSpot REST API" in content
        assert "https://developers.hubspot.com/docs/api/overview" in content
        assert "Direct API Mapping" in content
        assert "Parameter Compatibility Examples" in content

    def test_generate_prompt_content_api_compatibility_with_endpoint(self):
        """Test generating API compatibility content with API endpoint specified."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {"api_endpoint": "contacts"}
        )

        assert "Focused Guide: contacts" in content
        assert "list_hubspot_contacts" in content
        assert "get_hubspot_contact_properties" in content
        assert "https://developers.hubspot.com/docs/api/crm/contacts" in content

    def test_generate_prompt_content_api_compatibility_filters_params(self):
        """Test generating API compatibility content with filters parameter type."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {"parameter_type": "filters"}
        )

        assert "Filter Parameter Deep Dive" in content
        assert "filterGroups" in content
        assert "propertyName" in content
        assert "CONTAINS_TOKEN" in content
        assert "Automatic Operator Selection" in content

    def test_generate_prompt_content_api_compatibility_properties_params(self):
        """Test generating API compatibility content with properties parameter type."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {"parameter_type": "properties"}
        )

        assert "Properties Parameter Guide" in content
        assert "Default Properties" in content
        assert "get_hubspot_contact_properties" in content
        assert "extra_properties" in content

    def test_generate_prompt_content_api_compatibility_pagination_params(self):
        """Test generating API compatibility content with pagination parameter type."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {"parameter_type": "pagination"}
        )

        assert "Pagination Parameter Guide" in content
        assert "limit" in content
        assert "after" in content
        assert "cursor" in content
        assert "Pagination Workflow" in content

    def test_generate_prompt_content_unknown_prompt(self):
        """Test generating content for unknown prompt name."""
        content = HubSpotPrompts.generate_prompt_content("unknown_prompt", {})

        assert content == "Unknown prompt: unknown_prompt"

    def test_all_prompt_methods_exist(self):
        """Test that all prompt generation methods exist and can be called."""
        methods_to_test = [
            ("_generate_basics_content", {}),
            ("_generate_search_guide_content", {}),
            ("_generate_ai_search_content", {}),
            ("_generate_performance_content", {}),
            ("_generate_api_compatibility_content", {}),
        ]

        for method_name, args in methods_to_test:
            method = getattr(HubSpotPrompts, method_name)
            result = method(args)
            assert isinstance(result, str)
            assert len(result) > 100  # Ensure meaningful content

    def test_prompt_arguments_validation(self):
        """Test that prompt arguments are properly defined."""
        prompts = HubSpotPrompts.get_prompt_definitions()

        for prompt in prompts:
            for arg in prompt.arguments:
                assert isinstance(arg, types.PromptArgument)
                assert arg.name
                assert arg.description
                assert isinstance(arg.required, bool)

    def test_content_contains_critical_information(self):
        """Test that all prompts contain critical HubSpot API information."""
        # Test that API compatibility information is present in relevant prompts
        search_content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide", {}
        )
        api_content = HubSpotPrompts.generate_prompt_content(
            "hubspot_api_compatibility", {}
        )

        # Both should mention HubSpot API documentation
        assert "developers.hubspot.com" in search_content
        assert "developers.hubspot.com" in api_content

        # Both should emphasize API compatibility
        assert "API" in search_content
        assert "API" in api_content

    def test_prompt_content_formatting(self):
        """Test that prompt content is properly formatted with markdown."""
        # Test with a prompt that contains code blocks
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide", {"search_type": "api_params"}
        )

        # Check for markdown headers
        assert content.count("#") >= 5  # Multiple headers
        assert "```" in content  # Code blocks
        assert "**" in content  # Bold text
        assert "*" in content  # Italic or list items
        assert "- " in content  # List items

    def test_entity_type_coverage(self):
        """Test that all major entity types are covered in prompts."""
        basics_content = HubSpotPrompts.generate_prompt_content(
            "hubspot_basics_guide", {}
        )

        entity_types = ["contacts", "companies", "deals", "engagements"]
        for entity_type in entity_types:
            assert entity_type in basics_content

    def test_tool_coverage_in_prompts(self):
        """Test that prompts mention the key tools."""
        basics_content = HubSpotPrompts.generate_prompt_content(
            "hubspot_basics_guide", {}
        )

        key_tools = [
            "list_hubspot_contacts",
            "search_hubspot_deals",
            "semantic_search_hubspot",
            "manage_hubspot_embeddings",
            "load_hubspot_entities_to_cache",
        ]

        for tool in key_tools:
            assert tool in basics_content

    def test_generate_prompt_content_with_complex_arguments(self):
        """Test generating content with multiple arguments."""
        content = HubSpotPrompts.generate_prompt_content(
            "hubspot_search_guide",
            {"search_type": "api_params", "entity_type": "companies"},
        )

        # Should contain both API params and companies-specific content
        assert "Advanced API Parameters" in content
        assert "Companies-Specific Search" in content
        assert "search_hubspot_companies" in content
