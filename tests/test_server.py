import asyncio
import sys

import httpx
import pytest
from mcp.types import TextContent, Tool

from main import parse_arguments
from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.server import MCPHandlers


def test_parse_arguments_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    args = parse_arguments()
    assert args.mode == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8080


def test_parse_arguments_sse(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--mode", "sse", "--host", "0.0.0.0", "--port", "9090"],
    )
    args = parse_arguments()
    assert args.mode == "sse"
    assert args.host == "0.0.0.0"
    assert args.port == 9090


def test_handle_list_tools():
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools = asyncio.run(handlers.handle_list_tools())
    names = [tool.name for tool in tools]
    assert "list_hubspot_contacts" in names
    assert "list_hubspot_companies" in names
    assert "list_hubspot_deals" in names
    assert "get_deal_by_name" in names
    assert "get_hubspot_company_properties" in names


def test_handle_call_tool_no_client():
    # Test with None client
    handlers = MCPHandlers(None)
    result = asyncio.run(handlers.handle_call_tool("list_hubspot_contacts", {}))
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "Error: HubSpot client not initialized" in result[0].text


class DummyResponse:
    def __init__(self, data=None):
        self._data = data or {"results": []}
        self.status_code = 200
        self.text = ""

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class DummyAsyncClient:
    def __init__(self, *args, **kwargs):
        self.last_url = None
        self.last_headers = None
        self.last_params = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, url, headers=None, params=None):
        self.last_url = url
        self.last_headers = headers
        self.last_params = params
        return DummyResponse({"results": [{"id": "1", "properties": {"foo": "bar"}}]})


def test_get_contacts_and_companies(monkeypatch):
    # Patch AsyncClient to prevent real HTTP calls
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    contacts = asyncio.run(client.get_contacts(limit=2, filters={"search": "test"}))
    assert contacts == [{"id": "1", "properties": {"foo": "bar"}}]
    companies = asyncio.run(client.get_companies(limit=3, filters={"search": "alpha"}))
    assert companies == [{"id": "1", "properties": {"foo": "bar"}}]


def test_get_deals(monkeypatch):
    # Specific test for deals
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    deals = asyncio.run(client.get_deals(limit=5, filters={"search": "deal"}))
    assert deals == [{"id": "1", "properties": {"foo": "bar"}}]


def test_handle_call_tool_deals(monkeypatch):
    # Test calling the list_hubspot_deals tool
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    handlers = MCPHandlers(client)
    result = asyncio.run(handlers.handle_call_tool("list_hubspot_deals", {"limit": 10}))
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "HubSpot Deals" in result[0].text


def test_handle_list_tools_includes_properties():
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools = asyncio.run(handlers.handle_list_tools())
    names = [tool.name for tool in tools]
    assert "get_hubspot_contact_properties" in names
    assert "get_hubspot_deal_properties" in names


def test_get_deal_properties(monkeypatch):
    # Test deal properties retrieval
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    properties = asyncio.run(client.get_deal_properties())
    assert properties == [{"id": "1", "properties": {"foo": "bar"}}]


def test_handle_call_tool_deal_properties(monkeypatch):
    # Test calling the get_hubspot_deal_properties tool
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = HubSpotClient("testkey")
    handlers = MCPHandlers(client)
    result = asyncio.run(handlers.handle_call_tool("get_hubspot_deal_properties", {}))
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "HubSpot Deal Properties" in result[0].text


def test_handle_call_tool_unknown_tool():
    """Test calling an unknown tool."""
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    result = asyncio.run(handlers.handle_call_tool("unknown_tool", {}))
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert "Unknown tool: unknown_tool" in result[0].text


def test_handle_call_tool_with_arguments():
    """Test calling tools with various arguments."""
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)

    # Test with limit argument
    result = asyncio.run(
        handlers.handle_call_tool("list_hubspot_contacts", {"limit": 50})
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)

    # Test with filters
    result = asyncio.run(
        handlers.handle_call_tool(
            "list_hubspot_deals", {"limit": 25, "filters": {"search": "important"}}
        )
    )
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)


def test_handle_list_tools_count():
    """Test that all expected tools are listed."""
    client = HubSpotClient("test-key")
    handlers = MCPHandlers(client)
    tools = asyncio.run(handlers.handle_list_tools())

    # Should have exactly 8 tools
    assert len(tools) == 8

    expected_tools = [
        "list_hubspot_contacts",
        "list_hubspot_companies",
        "list_hubspot_deals",
        "create_deal",
        "get_deal_by_name",
        "get_hubspot_contact_properties",
        "get_hubspot_company_properties",
        "get_hubspot_deal_properties",
    ]

    tool_names = [tool.name for tool in tools]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names
