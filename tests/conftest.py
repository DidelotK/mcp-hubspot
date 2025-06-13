"""Shared pytest configuration and fixtures for HubSpot MCP Server tests."""

import os
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest


@pytest.fixture
def mock_hubspot_client():
    """Mock HubSpot API client for testing."""
    mock_client = Mock()

    # Mock common API responses
    mock_client.get_contacts = AsyncMock(
        return_value=[
            {
                "id": "1",
                "properties": {
                    "email": "test@example.com",
                    "firstname": "Test",
                    "lastname": "User",
                    "createdate": "2024-01-01T00:00:00.000Z",
                    "lastmodifieddate": "2024-01-01T00:00:00.000Z",
                },
            }
        ]
    )

    mock_client.get_companies = AsyncMock(
        return_value=[
            {
                "id": "1",
                "properties": {
                    "name": "Test Company",
                    "domain": "test.com",
                    "createdate": "2024-01-01T00:00:00.000Z",
                    "lastmodifieddate": "2024-01-01T00:00:00.000Z",
                },
            }
        ]
    )

    mock_client.get_deals = AsyncMock(
        return_value=[
            {
                "id": "1",
                "properties": {
                    "dealname": "Test Deal",
                    "amount": "1000",
                    "dealstage": "appointmentscheduled",
                    "createdate": "2024-01-01T00:00:00.000Z",
                    "lastmodifieddate": "2024-01-01T00:00:00.000Z",
                },
            }
        ]
    )

    return mock_client


@pytest.fixture
def sample_contact():
    """Create a sample contact for testing."""
    return {
        "id": "1",
        "properties": {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User",
            "phone": "+1234567890",
            "company": "Test Company",
            "createdate": "2024-01-01T00:00:00.000Z",
            "lastmodifieddate": "2024-01-01T00:00:00.000Z",
        },
    }


@pytest.fixture
def sample_contacts():
    """Create multiple contacts for bulk testing."""
    return [
        {
            "id": str(i),
            "properties": {
                "email": f"user{i}@example.com",
                "firstname": f"User{i}",
                "lastname": "Test",
                "createdate": "2024-01-01T00:00:00.000Z",
                "lastmodifieddate": "2024-01-01T00:00:00.000Z",
            },
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def sample_company():
    """Create a sample company for testing."""
    return {
        "id": "1",
        "properties": {
            "name": "Test Company",
            "domain": "test.com",
            "industry": "Technology",
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "createdate": "2024-01-01T00:00:00.000Z",
            "lastmodifieddate": "2024-01-01T00:00:00.000Z",
        },
    }


@pytest.fixture
def sample_deal():
    """Create a sample deal for testing."""
    return {
        "id": "1",
        "properties": {
            "dealname": "Test Deal",
            "amount": "1000",
            "dealstage": "appointmentscheduled",
            "closedate": "2024-12-31",
            "pipeline": "default",
            "createdate": "2024-01-01T00:00:00.000Z",
            "lastmodifieddate": "2024-01-01T00:00:00.000Z",
        },
    }


@pytest.fixture
def sample_deals():
    """Create multiple deals for bulk testing."""
    return [
        {
            "id": str(i),
            "properties": {
                "dealname": f"Deal {i}",
                "amount": str(i * 1000),
                "dealstage": "appointmentscheduled",
                "createdate": "2024-01-01T00:00:00.000Z",
                "lastmodifieddate": "2024-01-01T00:00:00.000Z",
            },
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    mock_server = Mock()
    mock_server.list_tools.return_value = []
    mock_server.list_resources.return_value = []
    mock_server.list_prompts.return_value = []
    return mock_server


@pytest.fixture
def test_environment():
    """Set up test environment variables."""
    test_env = {
        "HUBSPOT_ACCESS_TOKEN": "test_token_123",
        "HUBSPOT_API_URL": "https://api.hubapi.com",
    }

    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_env

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_api_response():
    """Mock API response structure."""
    return {"results": [], "paging": {"next": {"after": "next_cursor"}}}


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test."""
    yield
    # Clean up any global state if needed
