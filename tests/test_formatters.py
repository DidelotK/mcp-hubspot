"""Tests for HubSpot formatters."""

import pytest

from src.hubspot_mcp.formatters import HubSpotFormatter


def test_format_contacts():
    """Test contact formatting."""
    contacts_data = [
        {
            "id": "1",
            "properties": {
                "firstname": "Jean",
                "lastname": "Dupont",
                "email": "jean.dupont@example.com",
                "company": "Acme Corp",
                "phone": "+33123456789",
                "createdate": "2024-01-01T00:00:00Z",
            },
        },
        {
            "id": "2",
            "properties": {
                "firstname": "Marie",
                "lastname": "Martin",
                "email": "marie.martin@example.com",
            },
        },
    ]

    result = HubSpotFormatter.format_contacts(contacts_data)

    assert "📋 **HubSpot Contacts** (2 found)" in result
    assert "**Jean Dupont**" in result
    assert "jean.dupont@example.com" in result
    assert "Acme Corp" in result
    assert "**Marie Martin**" in result
    assert "marie.martin@example.com" in result
    assert "🆔 ID: 1" in result
    assert "🆔 ID: 2" in result


def test_format_companies():
    """Test company formatting."""
    companies_data = [
        {
            "id": "100",
            "properties": {
                "name": "Tech Solutions",
                "domain": "techsolutions.com",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
                "industry": "Technology",
                "createdate": "2024-01-15T00:00:00Z",
            },
        },
        {"id": "101", "properties": {"name": "Startup Inc"}},
    ]

    result = HubSpotFormatter.format_companies(companies_data)

    assert "🏢 **HubSpot Companies** (2 found)" in result
    assert "**Tech Solutions**" in result
    assert "techsolutions.com" in result
    assert "Paris, Île-de-France, France" in result
    assert "Technology" in result
    assert "**Startup Inc**" in result
    assert "🆔 ID: 100" in result
    assert "🆔 ID: 101" in result


def test_format_deals():
    """Test deal formatting."""
    deals_data = [
        {
            "id": "200",
            "properties": {
                "dealname": "Gros contrat",
                "amount": "50000.00",
                "dealstage": "negotiation",
                "pipeline": "sales",
                "closedate": "2024-06-30",
                "createdate": "2024-01-01T00:00:00Z",
                "hubspot_owner_id": "12345",
            },
        },
        {"id": "201", "properties": {"dealname": "Petit deal", "amount": "0"}},
        {"id": "202", "properties": {"dealname": "Deal sans montant"}},
    ]

    result = HubSpotFormatter.format_deals(deals_data)

    assert "💰 **HubSpot Deals** (3 found)" in result
    assert "**Gros contrat**" in result
    assert "$50,000.00" in result
    assert "negotiation" in result
    assert "sales" in result
    assert "**Petit deal**" in result
    assert "**Deal sans montant**" in result
    assert "🆔 ID: 200" in result
    assert "🆔 ID: 201" in result
    assert "🆔 ID: 202" in result


def test_format_deals_with_invalid_amount():
    """Test deal formatting with invalid amount."""
    deals_data = [
        {
            "id": "300",
            "properties": {
                "dealname": "Deal avec montant invalide",
                "amount": "invalid_amount",
            },
        }
    ]

    result = HubSpotFormatter.format_deals(deals_data)

    assert "**Deal avec montant invalide**" in result
    assert "$invalid_amount" in result


def test_format_empty_lists():
    """Test formatting with empty lists."""
    assert "📋 **HubSpot Contacts** (0 found)" in HubSpotFormatter.format_contacts([])
    assert "🏢 **HubSpot Companies** (0 found)" in HubSpotFormatter.format_companies([])
    assert "💰 **HubSpot Deals** (0 found)" in HubSpotFormatter.format_deals([])


def test_format_single_deal():
    """Test single deal formatting."""
    deal_data = {
        "id": "500",
        "properties": {
            "dealname": "Premium Contract",
            "amount": "25000.00",
            "dealstage": "proposal",
            "pipeline": "enterprise",
            "closedate": "2024-12-31",
            "createdate": "2024-06-01T00:00:00Z",
            "lastmodifieddate": "2024-06-12T12:00:00Z",
            "hubspot_owner_id": "98765",
        },
    }

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "💰 **HubSpot Deal**" in result
    assert "**Premium Contract**" in result
    assert "$25,000.00" in result
    assert "proposal" in result
    assert "enterprise" in result
    assert "2024-12-31" in result
    assert "🆔 ID: 500" in result


def test_format_single_deal_not_found():
    """Test formatting when no deal is found."""
    result = HubSpotFormatter.format_single_deal(None)

    assert "🔍 **Deal not found**" in result
    assert "No deal matches the specified name" in result


def test_format_single_deal_minimal_data():
    """Test deal formatting with minimal data."""
    deal_data = {"id": "600", "properties": {"dealname": "Simple Deal"}}

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Simple Deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🆔 ID: 600" in result


def test_format_contact_properties():
    """Test contact properties formatting."""
    properties_data = [
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
        {
            "name": "birthdate",
            "label": "Birth Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "demographic_information",
        },
        {
            "name": "industry",
            "label": "Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "company_information",
            "options": [
                {"label": "Technology", "value": "TECHNOLOGY"},
                {"label": "Finance", "value": "FINANCE"},
                {"label": "Healthcare", "value": "HEALTHCARE"},
            ],
        },
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "🔧 **HubSpot Contact Properties** (4 properties)" in result
    assert "## 📁 contactinformation" in result
    assert "**📝 First Name**" in result
    assert "`firstname`" in result
    assert "**📧 Email Address**" in result
    assert "`email`" in result
    assert "## 📁 demographic_information" in result
    assert "**📅 Birth Date**" in result
    assert "## 📁 company_information" in result
    assert "**📋 Industry**" in result
    assert "Technology, Finance, Healthcare" in result


def test_format_contact_properties_empty():
    """Test contact properties formatting with empty list."""
    result = HubSpotFormatter.format_contact_properties([])

    assert "❌ **No properties found**" in result
    assert "Unable to retrieve contact properties" in result


def test_format_contact_properties_minimal():
    """Test properties formatting with minimal data."""
    properties_data = [
        {
            "name": "custom_field",
            "label": "Custom Field",
            "type": "string",
            "fieldType": "text",
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "🔧 **HubSpot Contact Properties** (1 properties)" in result
    assert "## 📁 Other" in result
    assert "**📝 Custom Field**" in result
    assert "`custom_field`" in result


def test_format_company_properties():
    """Test company properties formatting."""
    properties_data = [
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
        {
            "name": "industry",
            "label": "Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "business_information",
            "options": [
                {"label": "Technology", "value": "TECHNOLOGY"},
                {"label": "Finance", "value": "FINANCE"},
                {"label": "Healthcare", "value": "HEALTHCARE"},
            ],
        },
        {
            "name": "annualrevenue",
            "label": "Annual Revenue",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial_information",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "🏢 **HubSpot Company Properties** (4 properties)" in result
    assert "## 📁 companyinformation" in result
    assert "## 📁 business_information" in result
    assert "## 📁 financial_information" in result
    assert "**🏢 Company Name**" in result
    assert "**🌐 Website Domain**" in result
    assert "**📋 Industry**" in result
    assert "**🔢 Annual Revenue**" in result
    assert "`name`" in result
    assert "`domain`" in result
    assert "The company name" in result
    assert "The company website domain" in result
    assert "Technology, Finance, Healthcare" in result


def test_format_company_properties_empty():
    """Test company properties formatting with empty list."""
    result = HubSpotFormatter.format_company_properties([])

    assert "❌ **No properties found**" in result
    assert "Unable to retrieve company properties" in result


def test_format_company_properties_minimal():
    """Test company properties formatting with minimal data."""
    properties_data = [
        {
            "name": "custom_field",
            "label": "Custom Company Field",
            "type": "string",
            "fieldType": "text",
        }
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "🏢 **HubSpot Company Properties** (1 properties)" in result
    assert "## 📁 Other" in result
    assert "**📝 Custom Company Field**" in result
    assert "`custom_field`" in result
