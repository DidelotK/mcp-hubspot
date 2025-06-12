"""Tests for HubSpot MCP tools."""

import asyncio
from unittest.mock import patch

import pytest
from mcp.types import TextContent

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.tools import (
    CompaniesTool,
    CompanyPropertiesTool,
    ContactPropertiesTool,
    ContactsTool,
    CreateDealTool,
    DealByNameTool,
    DealPropertiesTool,
    DealsTool,
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
            from httpx import HTTPStatusError, Request, Response

            response = Response(200, text="")
            request = Request("GET", url)
            raise HTTPStatusError("Test error", request=request, response=response)
        return DummyResponse(self.response_data)

    async def post(self, url, headers=None, json=None):
        if self.raise_error:
            from httpx import HTTPStatusError, Request, Response

            response = Response(200, text="")
            request = Request("POST", url)
            raise HTTPStatusError("Test error", request=request, response=response)
        return DummyResponse(self.response_data)


@pytest.mark.asyncio
async def test_contacts_tool_execute():
    """Test contacts tool execution."""
    test_data = {
        "results": [
            {
                "id": "1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john.doe@example.com",
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
        assert "John Doe" in result[0].text


@pytest.mark.asyncio
async def test_companies_tool_execute():
    """Test companies tool execution."""
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

        result = await tool.execute({"limit": 15})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Test Company" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_execute():
    """Test deals tool execution."""
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
async def test_deal_by_name_tool_execute():
    """Test deal by name tool execution."""
    test_data = {
        "results": [
            {
                "id": "400",
                "properties": {
                    "dealname": "Specific Deal",
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

        result = await tool.execute({"deal_name": "Specific Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Specific Deal" in result[0].text
        assert "$15,000.00" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_not_found():
    """Test deal by name tool when no deal is found."""
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result = await tool.execute({"deal_name": "Nonexistent Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Deal not found" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_missing_name():
    """Test deal by name tool without provided name."""
    client = HubSpotClient("test-key")
    tool = DealByNameTool(client)

    result = await tool.execute({})

    assert isinstance(result, list)
    assert len(result) == 1
    assert "Deal name is required" in result[0].text


@pytest.mark.asyncio
async def test_contact_properties_tool_execute():
    """Test contact properties tool execution."""
    test_data = {
        "results": [
            {
                "name": "firstname",
                "label": "First Name",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "The contact's first name",
            },
            {
                "name": "email",
                "label": "Email Address",
                "type": "string",
                "fieldType": "text",
                "groupName": "contactinformation",
                "description": "The contact's email address",
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
        assert "First Name" in result[0].text
        assert "Email Address" in result[0].text
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
    """Test tool definitions."""
    client = HubSpotClient("test-key")

    contacts_tool = ContactsTool(client)
    companies_tool = CompaniesTool(client)
    deals_tool = DealsTool(client)
    deal_by_name_tool = DealByNameTool(client)
    contact_properties_tool = ContactPropertiesTool(client)
    company_properties_tool = CompanyPropertiesTool(client)

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

    # Check input schemas
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
    )  # No required parameters
    assert (
        len(company_properties_def.inputSchema["properties"]) == 0
    )  # No required parameters


@pytest.mark.asyncio
async def test_create_deal_tool_execute():
    """Test create deal tool execution."""
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
        assert "✅ **Deal created successfully" in result[0].text
        assert "New Test Deal" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_minimal():
    """Test deal creation with only required fields."""
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
        assert "✅ **Deal created successfully" in result[0].text
        assert "Minimal Deal" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_error():
    """Test error handling for deal creation."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CreateDealTool(client)

        result = await tool.execute({"dealname": "Error Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


def test_create_deal_tool_definition():
    """Test create deal tool definition."""
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
    """Test company properties tool execution."""
    test_data = {
        "results": [
            {
                "name": "name",
                "label": "Company Name",
                "type": "string",
                "fieldType": "text",
                "groupName": "companyinformation",
                "description": "The company name",
            },
            {
                "name": "domain",
                "label": "Website Domain",
                "type": "string",
                "fieldType": "text",
                "groupName": "companyinformation",
                "description": "The company website domain",
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
        assert "HubSpot Company Properties" in result[0].text
        assert "Company Name" in result[0].text
        assert "Website Domain" in result[0].text
        assert "companyinformation" in result[0].text


@pytest.mark.asyncio
async def test_company_properties_tool_empty():
    """Test company properties tool with empty response."""
    test_data = {"results": []}

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompanyPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "No properties found" in result[0].text


@pytest.mark.asyncio
async def test_company_properties_tool_error():
    """Test company properties tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompanyPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


def test_company_properties_tool_definition():
    """Test company properties tool definition."""
    client = HubSpotClient("test-key")
    tool = CompanyPropertiesTool(client)

    definition = tool.get_tool_definition()

    assert definition.name == "get_hubspot_company_properties"
    assert (
        "Retrieves the list of available properties for HubSpot companies"
        in definition.description
    )
    assert len(definition.inputSchema["properties"]) == 0  # No required parameters
