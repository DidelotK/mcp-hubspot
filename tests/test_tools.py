"""Tests pour les outils MCP HubSpot."""

import asyncio
from unittest.mock import patch

import httpx
import pytest
from mcp.types import TextContent

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.tools import (
    CompaniesTool,
    CompanyPropertiesTool,
    ContactPropertiesTool,
    ContactsTool,
<<<<<<< HEAD
    CreateDealTool,
=======
    DealPropertiesTool,
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
    DealsTool,
    DealByNameTool,
)


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
                "API Error", request=None, response=DummyResponse()
            )
        return DummyResponse(self.response_data)

    async def post(self, url, headers=None, json=None):
        if self.raise_error:
            raise httpx.HTTPStatusError(
                "API Error", request=None, response=DummyResponse()
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
                    "email": "test@example.com",
                },
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
            {"id": "100", "properties": {"name": "Test Company", "domain": "test.com"}}
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
                    "dealstage": "proposal",
                },
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
        assert "$1,000.00" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_with_filters():
    """Test deals tool with filters."""
    test_data = {
        "results": [
            {
                "id": "300",
                "properties": {"dealname": "Filtered Deal", "amount": "2500.50"},
            }
        ]
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)

        result = await tool.execute({"limit": 10, "filters": {"search": "important"}})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Filtered Deal" in result[0].text


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)

        result = await tool.execute({"limit": 10})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "HubSpot API Error" in result[0].text


@pytest.mark.asyncio
<<<<<<< HEAD
async def test_deal_by_name_tool_execute():
    """Test d'exécution du tool deal par nom."""
=======
async def test_transaction_by_name_tool_execute():
    """Test transaction by name tool execution."""
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
    test_data = {
        "results": [
            {
                "id": "400",
                "properties": {
                    "dealname": "Contrat Spécifique",
                    "amount": "15000.00",
                    "dealstage": "closedwon",
                    "pipeline": "sales",
                },
            }
        ]
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result = await tool.execute({"deal_name": "Contrat Spécifique"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Contrat Spécifique" in result[0].text
        assert "$15,000.00" in result[0].text


@pytest.mark.asyncio
<<<<<<< HEAD
async def test_deal_by_name_tool_not_found():
    """Test du tool deal par nom quand aucun deal n'est trouvé."""
=======
async def test_transaction_by_name_tool_not_found():
    """Test transaction by name tool when no transaction is found."""
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result = await tool.execute({"deal_name": "Deal Inexistant"})

        assert isinstance(result, list)
        assert len(result) == 1
<<<<<<< HEAD
        assert "Deal non trouvé" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_missing_name():
    """Test du tool deal par nom sans nom fourni."""
=======
        assert "Transaction not found" in result[0].text


@pytest.mark.asyncio
async def test_transaction_by_name_tool_missing_name():
    """Test transaction by name tool without provided name."""
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
    client = HubSpotClient("test-key")
    tool = DealByNameTool(client)

    result = await tool.execute({})

    assert isinstance(result, list)
    assert len(result) == 1
<<<<<<< HEAD
    assert "Le nom du deal est obligatoire" in result[0].text
=======
    assert "Transaction name is required" in result[0].text
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage


@pytest.mark.asyncio
async def test_contact_properties_tool_execute():
    """Test contact properties tool execution."""
    test_data = {
        "results": [
            {
                "name": "firstname",
                "label": "Prénom",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "Le prénom du contact",
            },
            {
                "name": "email",
                "label": "Adresse e-mail",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "L'adresse e-mail du contact",
            },
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
        assert "HubSpot Contact Properties" in result[0].text
        assert "Prénom" in result[0].text
        assert "Adresse e-mail" in result[0].text
        assert "contactinformation" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_empty():
    """Test contact properties tool with empty response."""
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "No properties found" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_error():
    """Test contact properties tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


@pytest.mark.asyncio
async def test_deal_properties_tool_execute():
    """Test deal properties tool execution."""
    test_data = {
        "results": [
            {
                "name": "dealname",
                "label": "Deal Name",
                "type": "string",
                "fieldType": "text",
                "groupName": "dealinformation",
                "description": "The name of the deal",
            },
            {
                "name": "amount",
                "label": "Amount",
                "type": "number",
                "fieldType": "number",
                "groupName": "dealinformation",
                "description": "The deal amount",
            },
        ]
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "HubSpot Deal Properties" in result[0].text
        assert "Deal Name" in result[0].text
        assert "Amount" in result[0].text
        assert "dealinformation" in result[0].text


@pytest.mark.asyncio
async def test_deal_properties_tool_empty():
    """Test deal properties tool with empty response."""
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "No properties found" in result[0].text


def test_tools_definitions():
    """Test des définitions des outils."""
    client = HubSpotClient("test-key")

    contacts_tool = ContactsTool(client)
    companies_tool = CompaniesTool(client)
    deals_tool = DealsTool(client)
    deal_by_name_tool = DealByNameTool(client)
    contact_properties_tool = ContactPropertiesTool(client)
    company_properties_tool = CompanyPropertiesTool(client)

    # Test des définitions
    contacts_def = contacts_tool.get_tool_definition()
    companies_def = companies_tool.get_tool_definition()
    deals_def = deals_tool.get_tool_definition()
    deal_def = deal_by_name_tool.get_tool_definition()
    contact_properties_def = contact_properties_tool.get_tool_definition()
    company_properties_def = company_properties_tool.get_tool_definition()

    assert contacts_def.name == "list_hubspot_contacts"
    assert companies_def.name == "list_hubspot_companies"
    assert deals_def.name == "list_hubspot_deals"
    assert deal_def.name == "get_deal_by_name"
    assert contact_properties_def.name == "get_hubspot_contact_properties"
    assert company_properties_def.name == "get_hubspot_company_properties"

    # Vérifier les schémas d'entrée
    assert "limit" in contacts_def.inputSchema["properties"]
    assert "filters" in contacts_def.inputSchema["properties"]
    assert "limit" in companies_def.inputSchema["properties"]
    assert "filters" in companies_def.inputSchema["properties"]
    assert "limit" in deals_def.inputSchema["properties"]
    assert "filters" in deals_def.inputSchema["properties"]
    assert "deal_name" in deal_def.inputSchema["properties"]
    assert deal_def.inputSchema["required"] == ["deal_name"]
    assert (
        len(contact_properties_def.inputSchema["properties"]) == 0
    )  # Pas de paramètres requis
    assert (
        len(company_properties_def.inputSchema["properties"]) == 0
    )  # Pas de paramètres requis


@pytest.mark.asyncio
async def test_create_deal_tool_execute():
    """Test d'exécution du tool de création de deal."""
    test_data = {
        "id": "400",
        "properties": {
            "dealname": "New Test Deal",
            "amount": "5000.00",
            "dealstage": "appointmentscheduled",
            "createdate": "2024-01-15T10:30:00Z",
        },
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CreateDealTool(client)

        result = await tool.execute(
            {
                "dealname": "New Test Deal",
                "amount": "5000.00",
                "dealstage": "appointmentscheduled",
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ **Deal créé avec succès" in result[0].text
        assert "New Test Deal" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_minimal():
    """Test de création de deal avec uniquement les champs obligatoires."""
    test_data = {
        "id": "500",
        "properties": {
            "dealname": "Minimal Deal",
            "createdate": "2024-01-15T10:30:00Z",
        },
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CreateDealTool(client)

        result = await tool.execute({"dealname": "Minimal Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "✅ **Deal créé avec succès" in result[0].text
        assert "Minimal Deal" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_error():
    """Test de gestion d'erreur pour la création de deal."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CreateDealTool(client)

        result = await tool.execute({"dealname": "Error Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Erreur API HubSpot" in result[0].text


def test_create_deal_tool_definition():
    """Test de la définition du tool de création de deal."""
    client = HubSpotClient("test-key")
    tool = CreateDealTool(client)

    definition = tool.get_tool_definition()

    assert definition.name == "create_deal"
    assert "dealname" in definition.inputSchema["properties"]
    assert "amount" in definition.inputSchema["properties"]
    assert "dealstage" in definition.inputSchema["properties"]
    assert "dealname" in definition.inputSchema["required"]
    assert definition.inputSchema["properties"]["dealname"]["type"] == "string"


@pytest.mark.asyncio
async def test_company_properties_tool_execute():
    """Test d'exécution du tool propriétés d'entreprises."""
    test_data = {
        "results": [
            {
                "name": "name",
                "label": "Nom de l'entreprise",
                "type": "string",
                "fieldType": "text",
                "groupName": "companyinformation",
                "description": "Le nom de l'entreprise",
            },
            {
                "name": "domain",
                "label": "Domaine web",
                "type": "string",
                "fieldType": "text",
                "groupName": "companyinformation",
                "description": "Le domaine web de l'entreprise",
            },
        ]
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompanyPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Propriétés des Entreprises HubSpot" in result[0].text
        assert "Nom de l'entreprise" in result[0].text
        assert "Domaine web" in result[0].text
        assert "companyinformation" in result[0].text


@pytest.mark.asyncio
async def test_company_properties_tool_empty():
    """Test du tool propriétés d'entreprises avec réponse vide."""
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompanyPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Aucune propriété trouvée" in result[0].text


@pytest.mark.asyncio
async def test_company_properties_tool_error():
    """Test de la gestion d'erreur du tool propriétés d'entreprises."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompanyPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Erreur API HubSpot" in result[0].text


def test_company_properties_tool_definition():
    """Test de la définition du tool propriétés d'entreprises."""
    client = HubSpotClient("test-key")
    tool = CompanyPropertiesTool(client)

    definition = tool.get_tool_definition()

    assert definition.name == "get_hubspot_company_properties"
    assert (
        "Récupère la liste des propriétés disponibles pour les entreprises HubSpot"
        in definition.description
    )
    assert len(definition.inputSchema["properties"]) == 0  # Pas de paramètres requis
