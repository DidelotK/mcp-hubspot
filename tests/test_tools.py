"""Tests pour les outils MCP HubSpot."""

import asyncio
from unittest.mock import patch

import httpx
import pytest
from mcp.types import TextContent

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.tools import CompaniesTool, ContactsTool, DealsTool


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
        self.response_data = kwargs.get("response_data", {"results": []})
        self.raise_error = kwargs.get("raise_error", False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, url, headers=None, params=None):
        if self.raise_error:
            raise httpx.HTTPStatusError(
                "API Error", 
                request=None, 
                response=DummyResponse()
            )
        return DummyResponse(self.response_data)


@pytest.mark.asyncio
async def test_contacts_tool_execute():
    """Test d'exécution du tool contacts."""
    test_data = {
        "results": [
            {
                "id": "1",
                "properties": {
                    "firstname": "Test",
                    "lastname": "User",
                    "email": "test@example.com"
                }
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactsTool(client)
        
        result = await tool.execute({"limit": 10})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test User" in result[0].text


@pytest.mark.asyncio
async def test_companies_tool_execute():
    """Test d'exécution du tool entreprises."""
    test_data = {
        "results": [
            {
                "id": "100",
                "properties": {
                    "name": "Test Company",
                    "domain": "test.com"
                }
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompaniesTool(client)
        
        result = await tool.execute({"limit": 5})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test Company" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_execute():
    """Test d'exécution du tool deals."""
    test_data = {
        "results": [
            {
                "id": "200",
                "properties": {
                    "dealname": "Test Deal",
                    "amount": "1000.00",
                    "dealstage": "proposal"
                }
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)
        
        result = await tool.execute({"limit": 20})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test Deal" in result[0].text
        assert "1,000.00 €" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_with_filters():
    """Test du tool deals avec filtres."""
    test_data = {
        "results": [
            {
                "id": "300",
                "properties": {
                    "dealname": "Filtered Deal",
                    "amount": "2500.50"
                }
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)
        
        result = await tool.execute({
            "limit": 10,
            "filters": {"search": "important"}
        })
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Filtered Deal" in result[0].text


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test de la gestion d'erreur des outils."""
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)
        
        result = await tool.execute({"limit": 10})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Erreur API HubSpot" in result[0].text


def test_tools_definitions():
    """Test des définitions des outils."""
    client = HubSpotClient("test-key")
    
    contacts_tool = ContactsTool(client)
    companies_tool = CompaniesTool(client)
    deals_tool = DealsTool(client)
    
    # Test des définitions
    contacts_def = contacts_tool.get_tool_definition()
    companies_def = companies_tool.get_tool_definition()
    deals_def = deals_tool.get_tool_definition()
    
    assert contacts_def.name == "list_hubspot_contacts"
    assert companies_def.name == "list_hubspot_companies"
    assert deals_def.name == "list_hubspot_deals"
    
    # Vérifier les schémas d'entrée
    assert "limit" in contacts_def.inputSchema["properties"]
    assert "filters" in contacts_def.inputSchema["properties"]
    assert "limit" in companies_def.inputSchema["properties"]
    assert "filters" in companies_def.inputSchema["properties"]
    assert "limit" in deals_def.inputSchema["properties"]
    assert "filters" in deals_def.inputSchema["properties"] 