"""Test data fixtures for HubSpot entities."""

from datetime import datetime
from typing import Any, Dict, List


def get_sample_contacts() -> List[Dict[str, Any]]:
    """Generate sample contact data for testing."""
    return [
        {
            "id": "1",
            "properties": {
                "email": "john.doe@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "phone": "+1-555-0123",
                "company": "Example Corp",
                "jobtitle": "Software Engineer",
                "city": "New York",
                "state": "NY",
                "country": "United States",
                "createdate": "2024-01-01T10:00:00.000Z",
                "lastmodifieddate": "2024-01-15T14:30:00.000Z",
                "hs_lead_status": "NEW",
                "lifecyclestage": "lead",
            },
        },
        {
            "id": "2",
            "properties": {
                "email": "jane.smith@techcorp.com",
                "firstname": "Jane",
                "lastname": "Smith",
                "phone": "+1-555-0456",
                "company": "Tech Corp",
                "jobtitle": "Product Manager",
                "city": "San Francisco",
                "state": "CA",
                "country": "United States",
                "createdate": "2024-01-02T11:00:00.000Z",
                "lastmodifieddate": "2024-01-16T15:45:00.000Z",
                "hs_lead_status": "OPEN",
                "lifecyclestage": "marketingqualifiedlead",
            },
        },
    ]


def get_sample_companies() -> List[Dict[str, Any]]:
    """Generate sample company data for testing."""
    return [
        {
            "id": "1",
            "properties": {
                "name": "Example Corp",
                "domain": "example.com",
                "industry": "Technology",
                "description": "A leading technology company",
                "founded_year": "2010",
                "num_employees": "500",
                "annualrevenue": "10000000",
                "city": "New York",
                "state": "NY",
                "country": "United States",
                "phone": "+1-555-0100",
                "website": "https://example.com",
                "createdate": "2024-01-01T09:00:00.000Z",
                "lastmodifieddate": "2024-01-15T16:00:00.000Z",
                "type": "PROSPECT",
            },
        },
        {
            "id": "2",
            "properties": {
                "name": "Tech Corp",
                "domain": "techcorp.com",
                "industry": "Software",
                "description": "Innovative software solutions",
                "founded_year": "2015",
                "num_employees": "250",
                "annualrevenue": "5000000",
                "city": "San Francisco",
                "state": "CA",
                "country": "United States",
                "phone": "+1-555-0200",
                "website": "https://techcorp.com",
                "createdate": "2024-01-02T10:00:00.000Z",
                "lastmodifieddate": "2024-01-16T17:00:00.000Z",
                "type": "CUSTOMER",
            },
        },
    ]


def get_sample_deals() -> List[Dict[str, Any]]:
    """Generate sample deal data for testing."""
    return [
        {
            "id": "1",
            "properties": {
                "dealname": "Example Corp - Enterprise License",
                "amount": "50000",
                "dealstage": "negotiation",
                "closedate": "2024-03-31",
                "pipeline": "default",
                "hubspot_owner_id": "12345",
                "deal_currency_code": "USD",
                "description": "Enterprise software license deal",
                "createdate": "2024-01-01T12:00:00.000Z",
                "lastmodifieddate": "2024-01-20T14:00:00.000Z",
                "hs_deal_stage_probability": "0.5",
                "dealtype": "newbusiness",
            },
        },
        {
            "id": "2",
            "properties": {
                "dealname": "Tech Corp - Professional Services",
                "amount": "25000",
                "dealstage": "appointmentscheduled",
                "closedate": "2024-02-28",
                "pipeline": "default",
                "hubspot_owner_id": "67890",
                "deal_currency_code": "USD",
                "description": "Professional services engagement",
                "createdate": "2024-01-05T13:00:00.000Z",
                "lastmodifieddate": "2024-01-18T15:30:00.000Z",
                "hs_deal_stage_probability": "0.3",
                "dealtype": "existingbusiness",
            },
        },
    ]


def get_sample_properties() -> Dict[str, List[Dict[str, Any]]]:
    """Generate sample property definitions for testing."""
    return {
        "contacts": [
            {
                "name": "email",
                "label": "Email",
                "type": "string",
                "fieldType": "text",
                "description": "Contact's email address",
            },
            {
                "name": "firstname",
                "label": "First Name",
                "type": "string",
                "fieldType": "text",
                "description": "Contact's first name",
            },
            {
                "name": "lastname",
                "label": "Last Name",
                "type": "string",
                "fieldType": "text",
                "description": "Contact's last name",
            },
        ],
        "companies": [
            {
                "name": "name",
                "label": "Company Name",
                "type": "string",
                "fieldType": "text",
                "description": "Company name",
            },
            {
                "name": "domain",
                "label": "Domain",
                "type": "string",
                "fieldType": "text",
                "description": "Company domain",
            },
        ],
        "deals": [
            {
                "name": "dealname",
                "label": "Deal Name",
                "type": "string",
                "fieldType": "text",
                "description": "Deal name",
            },
            {
                "name": "amount",
                "label": "Amount",
                "type": "number",
                "fieldType": "number",
                "description": "Deal amount",
            },
        ],
    }


def get_api_error_responses() -> Dict[str, Dict[str, Any]]:
    """Generate sample API error responses for testing."""
    return {
        "unauthorized": {
            "status": "error",
            "message": "This request is not authorized",
            "correlationId": "test-correlation-id",
            "category": "UNAUTHORIZED",
        },
        "rate_limit": {
            "status": "error",
            "message": "Request rate limit exceeded",
            "correlationId": "test-correlation-id",
            "category": "RATE_LIMIT",
        },
        "not_found": {
            "status": "error",
            "message": "Resource not found",
            "correlationId": "test-correlation-id",
            "category": "OBJECT_NOT_FOUND",
        },
        "bad_request": {
            "status": "error",
            "message": "Invalid request parameters",
            "correlationId": "test-correlation-id",
            "category": "VALIDATION_ERROR",
            "errors": [
                {"message": "Property 'invalid_field' does not exist", "in": "body"}
            ],
        },
    }


def get_empty_api_response() -> Dict[str, Any]:
    """Generate empty API response for testing."""
    return {"results": [], "paging": {"next": None}}


def get_paginated_api_response() -> Dict[str, Any]:
    """Generate paginated API response for testing."""
    return {
        "results": get_sample_contacts()[:1],
        "paging": {
            "next": {"after": "next_cursor_token", "link": "?after=next_cursor_token"}
        },
    }
