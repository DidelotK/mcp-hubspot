"""Tests for HubSpot MCP server."""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from mcp.types import TextContent, Tool

# Add src to path for imports before importing local modules
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Local imports after path modification
from hubspot_mcp.__main__ import parse_arguments  # noqa: E402
from hubspot_mcp.client import HubSpotClient  # noqa: E402
from hubspot_mcp.server import MCPHandlers  # noqa: E402


def test_parse_arguments_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test argument parsing with default values.

    Tests that the argument parser correctly sets default values
    when no arguments are provided.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(sys, "argv", ["hubspot-mcp-server"])
    args = parse_arguments()
    assert args.mode == "stdio"
    assert args.host == "localhost"
    assert args.port == 8080


def test_parse_arguments_sse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test argument parsing with SSE mode.

    Tests that the argument parser correctly handles SSE mode
    and custom host/port values.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["hubspot-mcp-server", "--mode", "sse", "--host", "0.0.0.0", "--port", "9090"],
    )
    args = parse_arguments()
    assert args.mode == "sse"
    assert args.host == "0.0.0.0"
    assert args.port == 9090


def test_handle_list_tools() -> None:
    """Test listing available tools.

    Tests that the handler correctly lists all available HubSpot tools
    with their expected names.
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools: List[Tool] = asyncio.run(handlers.handle_list_tools())
    names: List[str] = [tool.name for tool in tools]
    assert "list_hubspot_contacts" in names
    assert "list_hubspot_companies" in names
    assert "list_hubspot_deals" in names
    assert "get_deal_by_name" in names
    assert "get_hubspot_company_properties" in names


def test_handle_call_tool_no_client() -> None:
    """Test tool execution without client.

    Tests that the handler correctly handles the case when no client
    is initialized.
    """
    handlers = MCPHandlers(None)
    result: List[TextContent] = asyncio.run(
        handlers.handle_call_tool("list_hubspot_contacts", {})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "Error: HubSpot client not initialized" in result[0].text


class DummyResponse:
    """Mock response class for testing."""

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the mock response.

        Args:
            data: Optional response data. Defaults to empty results.
        """
        self._data = data or {"results": []}
        self.status_code = 200
        self.text = ""

    def json(self) -> Dict[str, Any]:
        """Return the mock response data.

        Returns:
            The mock response data as a dictionary.
        """
        return self._data

    def raise_for_status(self) -> None:
        """Mock method that does nothing."""
        pass


class DummyAsyncClient:
    """Mock async client for testing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the mock async client.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.last_url: Optional[str] = None
        self.last_headers: Optional[Dict[str, str]] = None
        self.last_params: Optional[Dict[str, Any]] = None

    async def __aenter__(self) -> "DummyAsyncClient":
        """Enter the async context.

        Returns:
            The mock client instance.
        """
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Exit the async context.

        Args:
            exc_type: The exception type.
            exc: The exception instance.
            tb: The traceback.
        """
        pass

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> DummyResponse:
        """Mock GET request.

        Args:
            url: The request URL.
            headers: Optional request headers.
            params: Optional query parameters.

        Returns:
            A mock response.
        """
        self.last_url = url
        self.last_headers = headers
        self.last_params = params
        return DummyResponse({"results": [{"id": "1", "properties": {"foo": "bar"}}]})


def test_get_contacts_and_companies(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test contact and company retrieval.

    Tests that the client correctly retrieves contacts and companies
    with the provided filters.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    contacts: List[Dict[str, Any]] = asyncio.run(
        client.get_contacts(limit=2, after="cursor123")
    )
    assert contacts == [{"id": "1", "properties": {"foo": "bar"}}]
    companies: List[Dict[str, Any]] = asyncio.run(
        client.get_companies(limit=3, after="cursor456")
    )
    assert companies == [{"id": "1", "properties": {"foo": "bar"}}]


def test_get_deals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test deal retrieval.

    Tests that the client correctly retrieves deals with pagination.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    deals: List[Dict[str, Any]] = asyncio.run(
        client.get_deals(limit=5, after="cursor123")
    )
    assert deals == [{"id": "1", "properties": {"foo": "bar"}}]


def test_handle_call_tool_deals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test deal tool execution.

    Tests that the handler correctly executes the list_hubspot_deals tool.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    handlers = MCPHandlers(client)
    result: List[TextContent] = asyncio.run(
        handlers.handle_call_tool("list_hubspot_deals", {"limit": 10})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "HubSpot Deals" in result[0].text


def test_handle_list_tools_includes_properties() -> None:
    """Test that property tools are included in the list.

    Tests that the handler includes all property-related tools
    in the list of available tools.
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools: List[Tool] = asyncio.run(handlers.handle_list_tools())
    names: List[str] = [tool.name for tool in tools]
    assert "get_hubspot_contact_properties" in names
    assert "get_hubspot_deal_properties" in names


def test_get_deal_properties(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test deal properties retrieval.

    Tests that the client correctly retrieves deal properties.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    properties: List[Dict[str, Any]] = asyncio.run(client.get_deal_properties())
    assert properties == [{"id": "1", "properties": {"foo": "bar"}}]


def test_handle_call_tool_deal_properties(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test deal properties tool execution.

    Tests that the handler correctly executes the get_hubspot_deal_properties tool.

    Args:
        monkeypatch: Pytest fixture for patching.
    """
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    handlers = MCPHandlers(client)
    result: List[TextContent] = asyncio.run(
        handlers.handle_call_tool("get_hubspot_deal_properties", {})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "HubSpot Deal Properties" in result[0].text


def test_handle_call_tool_unknown_tool() -> None:
    """Test calling an unknown tool.

    Tests that the handler correctly handles requests for unknown tools
    by returning an appropriate error message.
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    result: List[TextContent] = asyncio.run(
        handlers.handle_call_tool("unknown_tool", {})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "Unknown tool: unknown_tool" in result[0].text


def test_handle_call_tool_with_arguments() -> None:
    """Test calling tools with various arguments.

    Tests that the handler correctly handles tool calls with different
    types of arguments (limit, filters, etc.).
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)

    # Test with limit argument
    result: List[TextContent] = asyncio.run(
        handlers.handle_call_tool("list_hubspot_contacts", {"limit": 50})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)

    # Test with pagination
    result = asyncio.run(
        handlers.handle_call_tool(
            "list_hubspot_deals", {"limit": 25, "after": "cursor456"}
        )
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)


def test_handle_list_tools_count() -> None:
    """Test that all expected tools are listed.

    Tests that the handler lists exactly the expected number of tools
    with their correct names.
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools: List[Tool] = asyncio.run(handlers.handle_list_tools())

    # Should have exactly 17 tools after adding semantic search, embedding management, and bulk cache loader tools
    assert len(tools) == 17

    # Extract tool names
    tool_names = [tool.name for tool in tools]

    # Check that all expected tools are present
    expected_tools = [
        "manage_hubspot_cache",
        "list_hubspot_contacts",
        "list_hubspot_companies",
        "list_hubspot_deals",
        "list_hubspot_engagements",
        "get_deal_by_name",  # Fixed: no hubspot_ prefix
        "get_hubspot_contact_properties",
        "get_hubspot_company_properties",
        "get_hubspot_deal_properties",
        "create_deal",  # Fixed: no hubspot_ prefix
        "update_deal",  # Fixed: no hubspot_ prefix
        "search_hubspot_contacts",
        "search_hubspot_companies",
        "search_hubspot_deals",
        "semantic_search_hubspot",
        "manage_hubspot_embeddings",
    ]

    for tool_name in expected_tools:
        assert tool_name in tool_names, f"Tool {tool_name} not found in tools list"


def test_handle_call_tool_exception_handling() -> None:
    """Test exception handling in tool execution.

    Tests that the handler correctly handles exceptions raised during
    tool execution by logging the error and returning an appropriate
    error message to achieve 100% coverage.
    """
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)

    # Create a mock tool that raises an exception
    mock_tool = AsyncMock()
    mock_tool.execute.side_effect = ValueError("Test exception for coverage")

    # Replace the contacts tool with our mock
    handlers.tools_map["list_hubspot_contacts"] = mock_tool

    # Patch the logger to verify it's called
    with patch("hubspot_mcp.server.handlers.logger") as mock_logger:
        result: List[TextContent] = asyncio.run(
            handlers.handle_call_tool("list_hubspot_contacts", {"limit": 10})
        )

        # Verify the error response
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert (
            "Error executing tool list_hubspot_contacts: Test exception for coverage"
            in result[0].text
        )

        # Verify the logger was called with the error
        mock_logger.error.assert_called_once_with(
            "Error executing tool list_hubspot_contacts: Test exception for coverage"
        )
