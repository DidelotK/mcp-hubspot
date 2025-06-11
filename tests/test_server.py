import sys
import httpx
import pytest

import server
from server import parse_arguments, HubSpotClient, handle_list_tools, handle_call_tool
from mcp.types import TextContent, Tool


def test_parse_arguments_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['server.py'])
    args = parse_arguments()
    assert args.mode == 'stdio'
    assert args.host == '127.0.0.1'
    assert args.port == 8080


def test_parse_arguments_sse(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        ['server.py', '--mode', 'sse', '--host', '0.0.0.0', '--port', '9090'],
    )
    args = parse_arguments()
    assert args.mode == 'sse'
    assert args.host == '0.0.0.0'
    assert args.port == 9090


@pytest.mark.asyncio
async def test_handle_list_tools():
    tools = await handle_list_tools()
    names = [tool.name for tool in tools]
    assert 'list_hubspot_contacts' in names
    assert 'list_hubspot_companies' in names


@pytest.mark.asyncio
async def test_handle_call_tool_no_client():
    # Ensure hubspot_client is None
    server.hubspot_client = None
    result = await handle_call_tool('list_hubspot_contacts', {})
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
    assert 'Erreur: Client HubSpot non initialisé' in result[0].text


class DummyResponse:
    def __init__(self, data=None):
        self._data = data or {'results': []}
        self.status_code = 200
        self.text = ''

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class DummyAsyncClient:
    def __init__(self, *args, **kwargs):
        self.last_url = None
        self.last_headers = None
        self.last_params = None

    async def get(self, url, headers=None, params=None):
        self.last_url = url
        self.last_headers = headers
        self.last_params = params
        return DummyResponse({'results': [{'id': '1', 'properties': {'foo': 'bar'}}]})


@pytest.mark.asyncio
async def test_get_contacts_and_companies(monkeypatch):
    # Patch AsyncClient to prevent real HTTP calls
    monkeypatch.setattr(httpx, 'AsyncClient', DummyAsyncClient)
    client = HubSpotClient('testkey')
    contacts = await client.get_contacts(limit=2, filters={'search': 'test'})
    assert contacts == [{'id': '1', 'properties': {'foo': 'bar'}}]
    companies = await client.get_companies(limit=3, filters={'search': 'alpha'})
    assert companies == [{'id': '1', 'properties': {'foo': 'bar'}}]