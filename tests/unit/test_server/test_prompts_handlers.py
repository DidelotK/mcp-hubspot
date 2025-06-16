"""Tests for MCP server prompt handlers."""

from unittest.mock import AsyncMock, MagicMock, Mock

import mcp.types as types
import pytest

from hubspot_mcp.client import HubSpotClient
from hubspot_mcp.server.handlers import HubSpotHandlers


class TestHubSpotHandlersPrompts:
    """Test cases for MCP handlers prompt functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HubSpot client."""
        return Mock(spec=HubSpotClient)

    @pytest.fixture
    def handlers(self, mock_client):
        """Create MCP handlers instance."""
        return HubSpotHandlers(mock_client)

    @pytest.mark.asyncio
    async def test_handle_list_prompts(self, handlers):
        """Test listing all available prompts."""
        prompts = await handlers.handle_list_prompts()

        assert isinstance(prompts, list)
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

        # Verify all prompts are proper Prompt objects
        for prompt in prompts:
            assert isinstance(prompt, types.Prompt)
            assert prompt.name
            assert prompt.description
            assert isinstance(prompt.arguments, list)

    @pytest.mark.asyncio
    async def test_handle_get_prompt_basics_guide(self, handlers):
        """Test getting the basics guide prompt."""
        result = await handlers.handle_get_prompt("hubspot_basics_guide", {})

        assert isinstance(result, types.GetPromptResult)
        assert "Generated guidance for hubspot_basics_guide" in result.description
        assert len(result.messages) == 1

        message = result.messages[0]
        assert isinstance(message, types.PromptMessage)
        assert message.role == "user"
        assert isinstance(message.content, types.TextContent)

        content = message.content.text
        assert "HubSpot MCP Server - Getting Started Guide" in content
        assert "18 tools" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_with_arguments(self, handlers):
        """Test getting a prompt with arguments."""
        arguments = {"entity_type": "contacts"}
        result = await handlers.handle_get_prompt("hubspot_basics_guide", arguments)

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        # Should contain entity-specific content
        assert "Focused Guide: Contacts" in content
        assert "list_hubspot_contacts" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_search_guide(self, handlers):
        """Test getting the search guide prompt."""
        arguments = {"search_type": "api_params"}
        result = await handlers.handle_get_prompt("hubspot_search_guide", arguments)

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "HubSpot Search & Filtering Guide" in content
        assert "Advanced API Parameters" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_ai_search_guide(self, handlers):
        """Test getting the AI search guide prompt."""
        arguments = {"use_case": "setup"}
        result = await handlers.handle_get_prompt("hubspot_ai_search_guide", arguments)

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "HubSpot AI-Powered Search Guide" in content
        assert "Initial Setup Guide" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_performance_guide(self, handlers):
        """Test getting the performance guide prompt."""
        arguments = {"optimization_focus": "caching"}
        result = await handlers.handle_get_prompt(
            "hubspot_performance_guide", arguments
        )

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "HubSpot Performance Optimization Guide" in content
        assert "Cache Optimization Deep Dive" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_api_compatibility(self, handlers):
        """Test getting the API compatibility prompt."""
        arguments = {"parameter_type": "filters"}
        result = await handlers.handle_get_prompt(
            "hubspot_api_compatibility", arguments
        )

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "HubSpot API Compatibility Guide" in content
        assert "Filter Parameter Deep Dive" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_no_arguments(self, handlers):
        """Test getting a prompt with no arguments provided."""
        result = await handlers.handle_get_prompt("hubspot_basics_guide", {})

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        # Should work with default empty arguments
        assert "HubSpot MCP Server - Getting Started Guide" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_with_none_arguments(self, handlers):
        """Test getting a prompt with None arguments to cover line 106."""
        result = await handlers.handle_get_prompt("hubspot_basics_guide", None)

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        # Should work with None arguments converted to empty dict
        assert "HubSpot MCP Server - Getting Started Guide" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_empty_arguments(self, handlers):
        """Test getting a prompt with empty arguments dict."""
        result = await handlers.handle_get_prompt("hubspot_basics_guide", {})

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "HubSpot MCP Server - Getting Started Guide" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_unknown_prompt(self, handlers):
        """Test handling unknown prompt name."""
        result = await handlers.handle_get_prompt("unknown_prompt", {})

        assert isinstance(result, types.GetPromptResult)
        content = result.messages[0].content.text

        assert "Unknown prompt: unknown_prompt" in content

    @pytest.mark.asyncio
    async def test_handle_get_prompt_error_handling(self, handlers):
        """Test error handling in prompt generation."""
        # Mock the prompts object to raise an exception
        handlers.prompts.generate_prompt_content = Mock(
            side_effect=Exception("Test error")
        )

        result = await handlers.handle_get_prompt("hubspot_basics_guide", {})

        assert isinstance(result, types.GetPromptResult)
        assert "Error generating prompt hubspot_basics_guide" in result.description
        content = result.messages[0].content.text
        assert "Error generating prompt hubspot_basics_guide: Test error" in content

    @pytest.mark.asyncio
    async def test_prompts_initialization(self, mock_client):
        """Test that prompts are properly initialized in handlers."""
        handlers = HubSpotHandlers(mock_client)

        assert handlers.prompts is not None
        assert hasattr(handlers.prompts, "get_prompt_definitions")
        assert hasattr(handlers.prompts, "generate_prompt_content")

    @pytest.mark.asyncio
    async def test_all_prompts_generate_content(self, handlers):
        """Test that all defined prompts can generate content."""
        prompts = await handlers.handle_list_prompts()

        for prompt in prompts:
            result = await handlers.handle_get_prompt(prompt.name, {})

            assert isinstance(result, types.GetPromptResult)
            assert len(result.messages) == 1
            content = result.messages[0].content.text
            assert len(content) > 100  # Ensure meaningful content

    @pytest.mark.asyncio
    async def test_prompt_arguments_are_optional(self, handlers):
        """Test that all prompt arguments are optional."""
        prompts = await handlers.handle_list_prompts()

        for prompt in prompts:
            # Should work without any arguments
            result = await handlers.handle_get_prompt(prompt.name, {})
            assert isinstance(result, types.GetPromptResult)

            # Verify all arguments are optional
            for arg in prompt.arguments:
                assert not arg.required

    @pytest.mark.asyncio
    async def test_prompt_content_consistency(self, handlers):
        """Test that prompt content is consistent across calls."""
        # Same prompt with same arguments should return same content
        args = {"entity_type": "contacts"}

        result1 = await handlers.handle_get_prompt("hubspot_basics_guide", args)
        result2 = await handlers.handle_get_prompt("hubspot_basics_guide", args)

        content1 = result1.messages[0].content.text
        content2 = result2.messages[0].content.text

        assert content1 == content2

    def test_prompts_class_integration(self, handlers):
        """Test that HubSpotPrompts class is properly integrated."""
        from hubspot_mcp.prompts import HubSpotPrompts

        assert isinstance(handlers.prompts, HubSpotPrompts)

        # Test that we can call the class methods directly
        definitions = handlers.prompts.get_prompt_definitions()
        assert len(definitions) == 5

        content = handlers.prompts.generate_prompt_content("hubspot_basics_guide", {})
        assert "HubSpot MCP Server" in content

    @pytest.mark.asyncio
    async def test_handle_list_prompts_exception_handling(self, handlers):
        """Test exception handling in handle_list_prompts method.

        Tests that the handler correctly handles exceptions raised during
        prompt listing by logging the error and returning an empty list
        to achieve 100% coverage of lines 87-89.
        """
        from unittest.mock import patch

        # Mock the prompts object to raise an exception
        handlers.prompts.get_prompt_definitions = Mock(
            side_effect=Exception("Test error during prompt listing")
        )

        # Patch the logger to verify it's called
        with patch("src.hubspot_mcp.server.handlers.logger") as mock_logger:
            result = await handlers.handle_list_prompts()

            # Verify the error response (should return empty list)
            assert isinstance(result, list)
            assert len(result) == 0

            # Verify the logger was called with the error
            mock_logger.error.assert_called_once_with(
                "Error listing prompts: Test error during prompt listing"
            )
