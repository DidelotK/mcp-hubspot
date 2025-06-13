"""Tests for HubSpot MCP tools."""

import asyncio
from typing import Any, Dict, List, Optional, Union
from unittest.mock import patch

import mcp.types as types
import pytest
from httpx import HTTPStatusError
from mcp.types import TextContent

from hubspot_mcp.client import HubSpotClient
from hubspot_mcp.tools import (
    CompaniesTool,
    CompanyPropertiesTool,
    ContactPropertiesTool,
    ContactsTool,
    CreateDealTool,
    DealByNameTool,
    DealPropertiesTool,
    DealsTool,
    UpdateDealTool,
)
from hubspot_mcp.tools.base import BaseTool


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
                response_data: Optional response data. Defaults to empty results.
                raise_error: Whether to raise an error. Defaults to False.
        """
        self.response_data = kwargs.get("response_data", {"results": []})
        self.raise_error = kwargs.get("raise_error", False)

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

        Raises:
            HTTPStatusError: If raise_error is True.
        """
        if self.raise_error:
            from httpx import HTTPStatusError, Request, Response

            response = Response(200, text="")
            request = Request("GET", url)
            raise HTTPStatusError("Test error", request=request, response=response)
        return DummyResponse(self.response_data)

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> DummyResponse:
        """Mock POST request.

        Args:
            url: The request URL.
            headers: Optional request headers.
            json: Optional JSON body.

        Returns:
            A mock response.

        Raises:
            HTTPStatusError: If raise_error is True.
        """
        if self.raise_error:
            from httpx import HTTPStatusError, Request, Response

            response = Response(200, text="")
            request = Request("POST", url)
            raise HTTPStatusError("Test error", request=request, response=response)
        return DummyResponse(self.response_data)

    async def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> DummyResponse:
        """Mock PATCH request.

        Args:
            url: The request URL.
            headers: Optional request headers.
            json: Optional JSON body.

        Returns:
            A mock response.

        Raises:
            HTTPStatusError: If raise_error is True.
        """
        if self.raise_error:
            from httpx import HTTPStatusError, Request, Response

            response = Response(400, text="API error")
            request = Request("PATCH", url)
            raise HTTPStatusError(
                "HubSpot API Error", request=request, response=response
            )
        return DummyResponse(self.response_data)


@pytest.mark.asyncio
async def test_contacts_tool_execute() -> None:
    """Test contacts tool execution.

    Tests the execution of the contacts tool with mock data.
    Verifies that the tool correctly formats and returns contact information.
    """
    test_data: Dict[str, Any] = {
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

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactsTool(client)

        result: List[TextContent] = await tool.execute({"limit": 10})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "John Doe" in result[0].text


@pytest.mark.asyncio
async def test_companies_tool_execute() -> None:
    """Test companies tool execution.

    Tests the execution of the companies tool with mock data.
    Verifies that the tool correctly formats and returns company information.
    """
    test_data: Dict[str, Any] = {
        "results": [
            {"id": "100", "properties": {"name": "Test Company", "domain": "test.com"}}
        ]
    }

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompaniesTool(client)

        result: List[TextContent] = await tool.execute({"limit": 15})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Test Company" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_execute() -> None:
    """Test deals tool execution.

    Tests the execution of the deals tool with mock data.
    Verifies that the tool correctly formats and returns deal information.
    """
    test_data: Dict[str, Any] = {
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

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)

        result: List[TextContent] = await tool.execute({"limit": 20})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test Deal" in result[0].text
        assert "$1,000.00" in result[0].text


@pytest.mark.asyncio
async def test_deals_tool_with_filters() -> None:
    """Test deals tool with filters.

    Tests the execution of the deals tool with search filters.
    Verifies that the tool correctly handles and applies filters.
    """
    test_data: Dict[str, Any] = {
        "results": [
            {
                "id": "300",
                "properties": {"dealname": "Filtered Deal", "amount": "2500.50"},
            }
        ]
    }

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)

        result: List[TextContent] = await tool.execute(
            {"limit": 10, "filters": {"search": "important"}}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Filtered Deal" in result[0].text


@pytest.mark.asyncio
async def test_tool_error_handling() -> None:
    """Test tool error handling.

    Tests the error handling of tools when API errors occur.
    Verifies that errors are properly caught and formatted.
    """

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealsTool(client)

        result: List[TextContent] = await tool.execute({"limit": 10})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "HubSpot API Error" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_execute() -> None:
    """Test deal by name tool execution.

    Tests the execution of the deal by name tool with mock data.
    Verifies that the tool correctly formats and returns deal information.
    """
    test_data: Dict[str, Any] = {
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

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result: List[TextContent] = await tool.execute({"deal_name": "Specific Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Specific Deal" in result[0].text
        assert "$15,000.00" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_not_found() -> None:
    """Test deal by name tool when no deal is found.

    Tests the behavior of the deal by name tool when no matching deal is found.
    Verifies that the tool returns an appropriate "not found" message.
    """
    test_data: Dict[str, Any] = {"results": []}

    def mock_client(*args: Any, **kwargs: Any) -> DummyAsyncClient:
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result: List[TextContent] = await tool.execute(
            {"deal_name": "Nonexistent Deal"}
        )

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


@pytest.mark.asyncio
async def test_base_tool_handle_httpx_error():
    """Test base tool error handling for HTTPStatusError."""
    from httpx import HTTPStatusError, Request, Response

    # Create a concrete implementation for testing
    class TestTool(BaseTool):
        def get_tool_definition(self):
            return None

        async def execute(self, arguments):
            return []

    client = HubSpotClient("test-key")
    tool = TestTool(client)

    # Create a mock HTTPStatusError
    response = Response(404, text="Not Found")
    request = Request("GET", "https://api.hubapi.com/test")
    error = HTTPStatusError("Not Found", request=request, response=response)
    result = tool.handle_error(error)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "HubSpot API Error (404)" in result[0].text
    assert "Not Found" in result[0].text


@pytest.mark.asyncio
async def test_base_tool_handle_generic_error():
    """Test base tool error handling for generic exceptions."""

    class TestTool(BaseTool):
        def get_tool_definition(self):
            return None

        async def execute(self, arguments):
            return []

    client = HubSpotClient("test-key")
    tool = TestTool(client)

    # Create a generic error
    error = ValueError("Something went wrong")
    result = tool.handle_error(error)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "Unexpected error: Something went wrong" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_missing_dealname():
    """Test create deal tool with missing dealname."""
    client = HubSpotClient("test-key")
    tool = CreateDealTool(client)

    result = await tool.execute({})

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "Deal name (dealname) is required" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_empty_dealname():
    """Test create deal tool with empty dealname."""
    client = HubSpotClient("test-key")
    tool = CreateDealTool(client)

    result = await tool.execute({"dealname": ""})

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "Deal name (dealname) is required" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_with_all_fields():
    """Test create deal tool with all optional fields."""
    test_data = {
        "id": "1000",
        "properties": {
            "dealname": "Complete Deal",
            "amount": "10000.00",
            "dealstage": "closedwon",
            "pipeline": "sales",
            "closedate": "2024-12-31",
            "hubspot_owner_id": "12345",
            "description": "A complete deal with all fields",
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
                "dealname": "Complete Deal",
                "amount": "10000.00",
                "dealstage": "closedwon",
                "pipeline": "sales",
                "closedate": "2024-12-31",
                "hubspot_owner_id": "12345",
                "description": "A complete deal with all fields",
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ **Deal created successfully" in result[0].text
        assert "Complete Deal" in result[0].text
        assert "$10,000.00" in result[0].text
        assert "closedwon" in result[0].text
        assert "sales" in result[0].text


@pytest.mark.asyncio
async def test_deal_properties_tool_error():
    """Test deal properties tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealPropertiesTool(client)

        result = await tool.execute({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


def test_deal_properties_tool_definition():
    """Test deal properties tool definition."""
    client = HubSpotClient("test-key")
    tool = DealPropertiesTool(client)

    definition = tool.get_tool_definition()

    assert definition.name == "get_hubspot_deal_properties"
    assert (
        "Retrieves the list of available properties for HubSpot deals"
        in definition.description
    )
    assert len(definition.inputSchema["properties"]) == 0  # No required parameters


@pytest.mark.asyncio
async def test_contacts_tool_error_handling():
    """Test contacts tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = ContactsTool(client)

        result = await tool.execute({"limit": 10})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


@pytest.mark.asyncio
async def test_companies_tool_error_handling():
    """Test companies tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = CompaniesTool(client)

        result = await tool.execute({"limit": 10})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


@pytest.mark.asyncio
async def test_deal_by_name_tool_error_handling():
    """Test deal by name tool error handling."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = DealByNameTool(client)

        result = await tool.execute({"deal_name": "Test Deal"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


def test_all_tools_have_proper_definitions():
    """Test that all tools have proper definitions."""
    client = HubSpotClient("test-key")

    tools = [
        ContactsTool(client),
        CompaniesTool(client),
        DealsTool(client),
        CreateDealTool(client),
        DealByNameTool(client),
        ContactPropertiesTool(client),
        CompanyPropertiesTool(client),
        DealPropertiesTool(client),
    ]

    for tool in tools:
        definition = tool.get_tool_definition()

        # Check that all tools have required fields
        assert hasattr(definition, "name")
        assert hasattr(definition, "description")
        assert hasattr(definition, "inputSchema")
        assert isinstance(definition.name, str)
        assert isinstance(definition.description, str)
        assert isinstance(definition.inputSchema, dict)

        # Check that inputSchema has required structure
        assert "type" in definition.inputSchema
        assert "properties" in definition.inputSchema
        assert "additionalProperties" in definition.inputSchema


@pytest.mark.asyncio
async def test_create_deal_tool_with_invalid_amount_format():
    """Test create deal tool with invalid amount that can't be formatted."""
    test_data = {
        "id": "1100",
        "properties": {
            "dealname": "Deal with Invalid Amount Format",
            "amount": "not_a_number",
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
                "dealname": "Deal with Invalid Amount Format",
                "amount": "not_a_number",
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ **Deal created successfully" in result[0].text
        assert "Deal with Invalid Amount Format" in result[0].text
        # Should handle invalid amount gracefully without crashing
        assert "$not_a_number" in result[0].text


@pytest.mark.asyncio
async def test_create_deal_tool_with_no_amount():
    """Test create deal tool with no amount property in response."""
    test_data = {
        "id": "1200",
        "properties": {
            "dealname": "Deal without Amount",
            "dealstage": "proposal",
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
                "dealname": "Deal without Amount",
                "dealstage": "proposal",
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ **Deal created successfully" in result[0].text
        assert "Deal without Amount" in result[0].text
        # Should not include amount line when no amount is present
        assert "💰 Amount:" not in result[0].text


@pytest.mark.asyncio
async def test_update_deal_tool_success():
    """Test successful deal update."""
    test_data = {
        "id": "12345",
        "properties": {
            "dealname": "Updated Enterprise Contract",
            "amount": "85000",
            "dealstage": "contractsent",
            "pipeline": "enterprise",
            "closedate": "2024-12-31",
            "description": "Updated enterprise deal for Q4",
        },
    }

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(response_data=test_data)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = UpdateDealTool(client)

        result = await tool.execute(
            {
                "deal_id": "12345",
                "properties": {
                    "dealname": "Updated Enterprise Contract",
                    "amount": "85000",
                    "dealstage": "contractsent",
                    "pipeline": "enterprise",
                    "closedate": "2024-12-31",
                    "description": "Updated enterprise deal for Q4",
                },
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Updated Enterprise Contract" in result[0].text
        assert "$85,000.00" in result[0].text
        assert "contractsent" in result[0].text
        assert "enterprise" in result[0].text
        assert "2024-12-31" in result[0].text


@pytest.mark.asyncio
async def test_update_deal_tool_missing_deal_id():
    """Test deal update without deal_id."""
    client = HubSpotClient("test-key")
    tool = UpdateDealTool(client)

    result = await tool.execute(
        {"properties": {"dealname": "Updated Enterprise Contract"}}
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert "deal_id is required" in result[0].text


@pytest.mark.asyncio
async def test_update_deal_tool_missing_properties():
    """Test deal update without properties."""
    client = HubSpotClient("test-key")
    tool = UpdateDealTool(client)

    result = await tool.execute({"deal_id": "12345"})

    assert isinstance(result, list)
    assert len(result) == 1
    assert "properties object is required" in result[0].text


@pytest.mark.asyncio
async def test_update_deal_tool_api_error():
    """Test deal update with API error."""

    def mock_client(*args, **kwargs):
        return DummyAsyncClient(raise_error=True)

    with patch("httpx.AsyncClient", mock_client):
        client = HubSpotClient("test-key")
        tool = UpdateDealTool(client)

        result = await tool.execute(
            {
                "deal_id": "12345",
                "properties": {"dealname": "Updated Enterprise Contract"},
            }
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "HubSpot API Error" in result[0].text


def test_update_deal_tool_definition():
    """Test update deal tool definition."""
    client = HubSpotClient("test-key")
    tool = UpdateDealTool(client)

    definition = tool.get_tool_definition()

    assert definition.name == "update_deal"
    assert "Updates an existing deal in HubSpot" in definition.description
    assert "deal_id" in definition.inputSchema["properties"]
    assert "properties" in definition.inputSchema["properties"]
    assert "deal_id" in definition.inputSchema["required"]
    assert "properties" in definition.inputSchema["required"]
    assert (
        definition.inputSchema["properties"]["properties"]["additionalProperties"]
        is True
    )


def test_base_tool_abstract_class():
    """Test that BaseTool cannot be instantiated directly."""
    client = HubSpotClient("test-key")

    # Attempting to instantiate BaseTool directly should raise TypeError
    with pytest.raises(TypeError, match="Can't instantiate abstract class BaseTool"):
        BaseTool(client)


def test_base_tool_initialization():
    """Test BaseTool initialization with concrete implementation."""

    class TestTool(BaseTool):
        def get_tool_definition(self):
            return types.Tool(
                name="test_tool",
                description="Test tool",
                inputSchema={"type": "object", "properties": {}},
            )

        async def execute(self, arguments):
            return [types.TextContent(type="text", text="test")]

    client = HubSpotClient("test-key")
    tool = TestTool(client)

    # Test that the client is properly assigned
    assert tool.client == client
    assert isinstance(tool.client, HubSpotClient)


@pytest.mark.asyncio
async def test_base_tool_concrete_implementation():
    """Test that concrete implementation works correctly."""

    class TestTool(BaseTool):
        def get_tool_definition(self):
            # Call the parent's abstract method first to cover line 37
            try:
                super().get_tool_definition()
            except TypeError:
                # Expected since it's abstract
                pass

            return types.Tool(
                name="test_tool",
                description="Test tool for coverage",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            )

        async def execute(self, arguments):
            # Call the parent's abstract method first to cover line 49
            try:
                await super().execute(arguments)
            except TypeError:
                # Expected since it's abstract
                pass

            return [types.TextContent(type="text", text="test execution")]

    client = HubSpotClient("test-key")
    tool = TestTool(client)

    # Test get_tool_definition
    definition = tool.get_tool_definition()
    assert definition.name == "test_tool"
    assert definition.description == "Test tool for coverage"

    # Test execute
    result = await tool.execute({})
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].text == "test execution"
