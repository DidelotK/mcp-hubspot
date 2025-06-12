"""Tests pour les outils MCP HubSpot."""

import asyncio
from unittest.mock import patch

import httpx
import pytest
from mcp.types import TextContent

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.tools import CompaniesTool, ContactsTool, ContactPropertiesTool, DealsTool, TransactionByNameTool


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
    
    async def post(self, url, headers=None, json=None):
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


@pytest.mark.asyncio
async def test_transaction_by_name_tool_execute():
    """Test d'exécution du tool transaction par nom."""
    test_data = {
        "results": [
            {
                "id": "400",
                "properties": {
                    "dealname": "Contrat Spécifique",
                    "amount": "15000.00",
                    "dealstage": "closedwon",
                    "pipeline": "sales"
                }
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = TransactionByNameTool(client)
        
        result = await tool.execute({"deal_name": "Contrat Spécifique"})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Contrat Spécifique" in result[0].text
        assert "15,000.00 €" in result[0].text


@pytest.mark.asyncio 
async def test_transaction_by_name_tool_not_found():
    """Test du tool transaction par nom quand aucune transaction n'est trouvée."""
    test_data = {"results": []}
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = TransactionByNameTool(client)
        
        result = await tool.execute({"deal_name": "Transaction Inexistante"})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Transaction non trouvée" in result[0].text


@pytest.mark.asyncio
async def test_transaction_by_name_tool_missing_name():
    """Test du tool transaction par nom sans nom fourni."""
    client = HubSpotClient("test-key")
    tool = TransactionByNameTool(client)
    
    result = await tool.execute({})
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert "Le nom de la transaction est obligatoire" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_execute():
    """Test d'exécution du tool propriétés de contacts."""
    test_data = {
        "results": [
            {
                "name": "firstname",
                "label": "Prénom",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "Le prénom du contact"
            },
            {
                "name": "email",
                "label": "Adresse e-mail",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "L'adresse e-mail du contact"
            }
        ]
    }
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactPropertiesTool(client)
        
        result = await tool.execute({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Propriétés des Contacts HubSpot" in result[0].text
        assert "Prénom" in result[0].text
        assert "Adresse e-mail" in result[0].text
        assert "contactinformation" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_empty():
    """Test du tool propriétés de contacts avec réponse vide."""
    test_data = {"results": []}
    
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactPropertiesTool(client)
        
        result = await tool.execute({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Aucune propriété trouvée" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_error():
    """Test de la gestion d'erreur du tool propriétés de contacts."""
    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)
    
    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactPropertiesTool(client)
        
        result = await tool.execute({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Erreur API HubSpot" in result[0].text


def test_tools_definitions():
    """Test des définitions des outils."""
    client = HubSpotClient("test-key")
    
    contacts_tool = ContactsTool(client)
    companies_tool = CompaniesTool(client)
    deals_tool = DealsTool(client)
    transaction_by_name_tool = TransactionByNameTool(client)
    contact_properties_tool = ContactPropertiesTool(client)
    
    # Test des définitions
    contacts_def = contacts_tool.get_tool_definition()
    companies_def = companies_tool.get_tool_definition()
    deals_def = deals_tool.get_tool_definition()
    transaction_def = transaction_by_name_tool.get_tool_definition()
    properties_def = contact_properties_tool.get_tool_definition()
    
    assert contacts_def.name == "list_hubspot_contacts"
    assert companies_def.name == "list_hubspot_companies"
    assert deals_def.name == "list_hubspot_deals"
    assert transaction_def.name == "get_transaction_by_name"
    assert properties_def.name == "get_hubspot_contact_properties"
    
    # Vérifier les schémas d'entrée
    assert "limit" in contacts_def.inputSchema["properties"]
    assert "filters" in contacts_def.inputSchema["properties"]
    assert "limit" in companies_def.inputSchema["properties"]
    assert "filters" in companies_def.inputSchema["properties"]
    assert "limit" in deals_def.inputSchema["properties"]
    assert "filters" in deals_def.inputSchema["properties"]
    assert "deal_name" in transaction_def.inputSchema["properties"]
    assert transaction_def.inputSchema["required"] == ["deal_name"]
    assert len(properties_def.inputSchema["properties"]) == 0  # Pas de paramètres requis 