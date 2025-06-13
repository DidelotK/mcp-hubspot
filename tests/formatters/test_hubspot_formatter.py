"""Tests for HubSpot formatters."""

from typing import Any, Dict, List, Optional

import pytest

from src.hubspot_mcp.formatters import HubSpotFormatter


def test_format_deal_complete():
    deal = {
        "id": "12345",
        "properties": {
            "dealname": "Test Deal",
            "amount": "5000",
            "dealstage": "appointmentscheduled",
            "pipeline": "default",
            "closedate": "2024-12-31",
            "description": "Test description",
        },
    }
    result = HubSpotFormatter.format_single_deal(deal)
    assert "💰 **HubSpot Deal**" in result
    assert "**Test Deal**" in result
    assert "💰 Amount: $5,000.00" in result
    assert "📊 Stage: appointmentscheduled" in result
    assert "🔄 Pipeline: default" in result
    assert "📅 Close date: 2024-12-31" in result
    assert "🆔 ID: 12345" in result


def test_format_deal_partial():
    deal = {
        "id": "99999",
        "properties": {
            "dealname": "Partial Deal",
            "dealstage": "qualifiedtobuy",
        },
    }
    result = HubSpotFormatter.format_single_deal(deal)
    assert "**Partial Deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: qualifiedtobuy" in result
    assert "🔄 Pipeline: N/A" in result
    assert "📅 Close date: N/A" in result
    assert "🆔 ID: 99999" in result


def test_format_deal_empty():
    deal = {}
    result = HubSpotFormatter.format_single_deal(deal)
    assert "🔍 **Deal not found**" in result
    assert "No deal matches the specified name." in result


def test_format_contacts() -> None:
    """Test contact formatting.

    Tests the formatting of a list of contacts with various properties.
    Verifies that the formatted output contains all expected information
    including names, emails, and IDs.
    """
    contacts_data: List[Dict[str, Any]] = [
        {
            "id": "1",
            "properties": {
                "firstname": "Jean",
                "lastname": "Dupont",
                "email": "jean.dupont@example.com",
                "company": "Acme Corp",
                "phone": "+33123456789",
                "createdate": "2024-01-15T10:30:00Z",
                "lastmodifieddate": "2024-01-20T14:45:00Z",
            },
        },
        {
            "id": "2",
            "properties": {
                "firstname": "Marie",
                "lastname": "Martin",
                "email": "marie.martin@example.com",
                "createdate": "2024-01-10T09:15:00Z",
            },
        },
    ]

    result: str = HubSpotFormatter.format_contacts(contacts_data)

    assert "👥 **HubSpot Contacts** (2 found)" in result
    assert "**Jean Dupont**" in result
    assert "jean.dupont@example.com" in result
    assert "Acme Corp" in result
    assert "**Marie Martin**" in result
    assert "marie.martin@example.com" in result
    assert "🆔 ID: 1" in result
    assert "🆔 ID: 2" in result


def test_format_companies() -> None:
    """Test company formatting.

    Tests the formatting of a list of companies with various properties.
    Verifies that the formatted output contains all expected information
    including names, domains, locations, and IDs.
    """
    companies_data: List[Dict[str, Any]] = [
        {
            "id": "100",
            "properties": {
                "name": "Tech Solutions",
                "domain": "techsolutions.com",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
                "industry": "Technology",
                "createdate": "2024-01-01T00:00:00Z",
                "lastmodifieddate": "2024-01-15T12:00:00Z",
            },
        },
        {
            "id": "101",
            "properties": {
                "name": "Global Corp",
                "domain": "globalcorp.com",
            },
        },
    ]

    result: str = HubSpotFormatter.format_companies(companies_data)

    assert "🏢 **HubSpot Companies** (2 found)" in result
    assert "**Tech Solutions**" in result
    assert "techsolutions.com" in result
    assert "Paris" in result
    assert "Île-de-France" in result
    assert "France" in result
    assert "**Global Corp**" in result
    assert "globalcorp.com" in result
    assert "🆔 ID: 100" in result
    assert "🆔 ID: 101" in result


def test_format_deals() -> None:
    """Test deal formatting.

    Tests the formatting of a list of deals with various properties.
    Verifies that the formatted output contains all expected information
    including names, amounts, stages, and IDs.
    """
    deals_data: List[Dict[str, Any]] = [
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
        {"id": "202", "properties": {"dealname": "Deal without amount"}},
    ]

    result: str = HubSpotFormatter.format_deals(deals_data)

    assert "💰 **HubSpot Deals** (3 found)" in result
    assert "**Gros contrat**" in result
    assert "$50,000.00" in result
    assert "negotiation" in result
    assert "sales" in result
    assert "**Petit deal**" in result
    assert "**Deal without amount**" in result
    assert "🆔 ID: 200" in result
    assert "🆔 ID: 201" in result
    assert "🆔 ID: 202" in result


def test_format_deals_with_invalid_amount() -> None:
    """Test deal formatting with invalid amount.

    Tests the formatting of a deal with an invalid amount value.
    Verifies that the invalid amount is displayed as is.
    """
    deals_data: List[Dict[str, Any]] = [
        {
            "id": "300",
            "properties": {
                "dealname": "Deal with invalid amount",
                "amount": "invalid_amount",
            },
        }
    ]

    result: str = HubSpotFormatter.format_deals(deals_data)

    assert "**Deal with invalid amount**" in result
    assert "$invalid_amount" in result


def test_format_empty_lists() -> None:
    """Test formatting with empty lists.

    Tests the formatting of empty lists for contacts, companies, and deals.
    Verifies that appropriate messages are displayed for empty results.
    """
    assert "👥 **HubSpot Contacts** (0 found)" in HubSpotFormatter.format_contacts([])
    assert "🏢 **HubSpot Companies** (0 found)" in HubSpotFormatter.format_companies([])
    assert "💰 **HubSpot Deals** (0 found)" in HubSpotFormatter.format_deals([])


def test_format_single_deal() -> None:
    """Test single deal formatting.

    Tests the formatting of a single deal with complete information.
    Verifies that all deal properties are correctly formatted and displayed.
    """
    deal_data: Dict[str, Any] = {
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

    result: str = HubSpotFormatter.format_single_deal(deal_data)

    assert "💰 **HubSpot Deal**" in result
    assert "**Premium Contract**" in result
    assert "$25,000.00" in result
    assert "proposal" in result
    assert "enterprise" in result
    assert "2024-12-31" in result
    assert "🆔 ID: 500" in result


def test_format_single_deal_not_found() -> None:
    """Test formatting when no deal is found.

    Tests the formatting of a None value for a deal.
    Verifies that an appropriate "not found" message is displayed.
    """
    result: str = HubSpotFormatter.format_single_deal(None)

    assert "🔍 **Deal not found**" in result
    assert "No deal matches the specified name" in result


def test_format_single_deal_minimal_data() -> None:
    """Test deal formatting with minimal data.

    Tests the formatting of a deal with only basic information.
    Verifies that missing properties are handled gracefully.
    """
    deal_data: Dict[str, Any] = {"id": "600", "properties": {"dealname": "Simple Deal"}}

    result: str = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Simple Deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🆔 ID: 600" in result


def test_format_contact_properties() -> None:
    """Test contact properties formatting.

    Tests the formatting of contact properties with various field types.
    Verifies that properties are correctly grouped and formatted.
    """
    properties_data: List[Dict[str, Any]] = [
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

    result: str = HubSpotFormatter.format_contact_properties(properties_data)

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


def test_format_contact_properties_empty() -> None:
    """Test contact properties formatting with empty list.

    Tests the formatting of an empty list of contact properties.
    Verifies that an appropriate "no properties" message is displayed.
    """
    result: str = HubSpotFormatter.format_contact_properties([])

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
    assert "**📝 Company Name**" in result
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


def test_format_single_deal_with_invalid_amount():
    """Test deal formatting with invalid amount."""
    deal_data = {
        "id": "700",
        "properties": {
            "dealname": "Deal with Invalid Amount",
            "amount": "invalid_amount",
            "dealstage": "proposal",
        },
    }

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Deal with Invalid Amount**" in result
    assert "$invalid_amount" in result  # Should handle invalid amount gracefully
    assert "🆔 ID: 700" in result


def test_format_single_deal_with_zero_amount():
    """Test deal formatting with zero amount."""
    deal_data = {
        "id": "800",
        "properties": {
            "dealname": "Zero Amount Deal",
            "amount": "0",
            "dealstage": "proposal",
        },
    }

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Zero Amount Deal**" in result
    assert "💰 Amount: N/A" in result  # Zero amount should show as N/A
    assert "🆔 ID: 800" in result


def test_format_single_deal_with_empty_amount():
    """Test deal formatting with empty amount."""
    deal_data = {
        "id": "900",
        "properties": {
            "dealname": "Empty Amount Deal",
            "amount": "",
            "dealstage": "proposal",
        },
    }

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Empty Amount Deal**" in result
    assert "💰 Amount: N/A" in result  # Empty amount should show as N/A
    assert "🆔 ID: 900" in result


def test_format_contact_properties_with_special_field_types():
    """Test contact properties formatting with special field types to increase coverage."""
    properties_data = [
        {
            "name": "phone",
            "label": "Phone Number",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
        },
        {
            "name": "mobilephone",
            "label": "Mobile Phone",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
        },
        {
            "name": "company",
            "label": "Company",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
        },
        {
            "name": "revenue",
            "label": "Revenue",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial",
        },
        {
            "name": "agreement",
            "label": "Agreement",
            "type": "bool",
            "fieldType": "checkbox",
            "groupName": "legal",
        },
        {
            "name": "notes",
            "label": "Notes",
            "type": "string",
            "fieldType": "textarea",
            "groupName": "notes",
        },
        {
            "name": "attachment",
            "label": "Attachment",
            "type": "string",
            "fieldType": "file",
            "groupName": "documents",
        },
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📞 Phone Number**" in result
    assert "**📞 Mobile Phone**" in result
    assert "**🏢 Company**" in result
    assert "**🔢 Revenue**" in result
    assert "**☑️ Agreement**" in result
    assert "**📄 Notes**" in result
    assert "**📎 Attachment**" in result


def test_format_contact_properties_with_select_options():
    """Test contact properties with select field options."""
    properties_data = [
        {
            "name": "lifecycle_stage",
            "label": "Lifecycle Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "lead_information",
            "options": [
                {"label": "Subscriber", "value": "subscriber"},
                {"label": "Lead", "value": "lead"},
                {
                    "label": "Marketing Qualified Lead",
                    "value": "marketingqualifiedlead",
                },
                {"label": "Sales Qualified Lead", "value": "salesqualifiedlead"},
                {"label": "Opportunity", "value": "opportunity"},
                {"label": "Customer", "value": "customer"},
                {"label": "Evangelist", "value": "evangelist"},
                {"label": "Other", "value": "other"},
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📋 Lifecycle Stage**" in result
    assert (
        "Subscriber, Lead, Marketing Qualified Lead, Sales Qualified Lead, Opportunity"
        in result
    )
    assert "... and 3 more" in result


def test_format_contact_properties_with_few_select_options():
    """Test contact properties with select field having few options."""
    properties_data = [
        {
            "name": "gender",
            "label": "Gender",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "demographic",
            "options": [
                {"label": "Male", "value": "male"},
                {"label": "Female", "value": "female"},
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📋 Gender**" in result
    assert "Male, Female" in result
    assert "... and" not in result  # Should not show "... and more" for 2 options


def test_format_deal_properties_with_special_field_names():
    """Test deal properties with special field names to achieve coverage."""
    properties_data = [
        {
            "name": "amount",
            "label": "Deal Amount",
            "type": "number",
            "fieldType": "number",
            "groupName": "deal_information",
        },
        {
            "name": "hs_deal_amount",
            "label": "HubSpot Deal Amount",
            "type": "number",
            "fieldType": "number",
            "groupName": "deal_information",
        },
        {
            "name": "dealname",
            "label": "Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_information",
        },
        {
            "name": "hs_deal_name",
            "label": "HubSpot Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_information",
        },
        {
            "name": "dealstage",
            "label": "Deal Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "deal_information",
        },
        {
            "name": "hs_deal_stage",
            "label": "HubSpot Deal Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "deal_information",
        },
        {
            "name": "pipeline",
            "label": "Pipeline",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "deal_information",
        },
        {
            "name": "hs_pipeline",
            "label": "HubSpot Pipeline",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "deal_information",
        },
        {
            "name": "closedate",
            "label": "Close Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "deal_information",
        },
        {
            "name": "hs_closedate",
            "label": "HubSpot Close Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "deal_information",
        },
        {
            "name": "revenue",
            "label": "Revenue",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial",
        },
        {
            "name": "agreement",
            "label": "Agreement",
            "type": "bool",
            "fieldType": "checkbox",
            "groupName": "legal",
        },
        {
            "name": "notes",
            "label": "Notes",
            "type": "string",
            "fieldType": "textarea",
            "groupName": "notes",
        },
        {
            "name": "attachment",
            "label": "Attachment",
            "type": "string",
            "fieldType": "file",
            "groupName": "documents",
        },
    ]

    result = HubSpotFormatter.format_deal_properties(properties_data)

    assert "**🔢 Deal Amount**" in result  # number field type takes precedence
    assert "**🔢 HubSpot Deal Amount**" in result
    assert "**🏷️ Deal Name**" in result
    assert "**🏷️ HubSpot Deal Name**" in result
    assert "**📊 Deal Stage**" in result
    assert "**📊 HubSpot Deal Stage**" in result
    assert "**🔄 Pipeline**" in result
    assert "**🔄 HubSpot Pipeline**" in result
    assert "**📅 Close Date**" in result
    assert "**📅 HubSpot Close Date**" in result
    assert "**🔢 Revenue**" in result
    assert "**☑️ Agreement**" in result
    assert "**📄 Notes**" in result
    assert "**📎 Attachment**" in result


def test_format_company_properties_with_special_field_names():
    """Test company properties with special field names to achieve coverage."""
    properties_data = [
        {
            "name": "domain",
            "label": "Company Domain",
            "type": "string",
            "fieldType": "text",
            "groupName": "company_information",
        },
        {
            "name": "website",
            "label": "Website",
            "type": "string",
            "fieldType": "text",
            "groupName": "company_information",
        },
        {
            "name": "industry",
            "label": "Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "company_information",
        },
        {
            "name": "type",
            "label": "Company Type",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "company_information",
        },
        {
            "name": "city",
            "label": "City",
            "type": "string",
            "fieldType": "text",
            "groupName": "location",
        },
        {
            "name": "state",
            "label": "State",
            "type": "string",
            "fieldType": "text",
            "groupName": "location",
        },
        {
            "name": "country",
            "label": "Country",
            "type": "string",
            "fieldType": "text",
            "groupName": "location",
        },
        {
            "name": "revenue",
            "label": "Revenue",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial",
        },
        {
            "name": "agreement",
            "label": "Agreement",
            "type": "bool",
            "fieldType": "checkbox",
            "groupName": "legal",
        },
        {
            "name": "notes",
            "label": "Notes",
            "type": "string",
            "fieldType": "textarea",
            "groupName": "notes",
        },
        {
            "name": "attachment",
            "label": "Attachment",
            "type": "string",
            "fieldType": "file",
            "groupName": "documents",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "**🌐 Company Domain**" in result
    assert "**🌐 Website**" in result
    assert "**📋 Industry**" in result  # select field type takes precedence
    assert "**📋 Company Type**" in result  # select field type takes precedence
    assert "**📍 City**" in result
    assert "**📍 State**" in result
    assert "**📍 Country**" in result
    assert "**🔢 Revenue**" in result
    assert "**☑️ Agreement**" in result
    assert "**📄 Notes**" in result
    assert "**📎 Attachment**" in result


def test_format_properties_with_missing_fields():
    """Test properties formatting with missing fields."""
    properties_data = [
        {
            "name": "test_field",
            # Missing label, type, fieldType
            "groupName": "test_group",
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📝 N/A**" in result
    assert "`test_field`" in result
    assert "N/A (N/A)" in result


def test_format_properties_with_empty_options():
    """Test properties formatting with empty options list."""
    properties_data = [
        {
            "name": "test_select",
            "label": "Test Select",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "test",
            "options": [],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📋 Test Select**" in result
    assert "📋 Options:" not in result  # Should not show options if empty


def test_format_deal_properties_empty():
    """Test deal properties formatting with empty list."""
    result = HubSpotFormatter.format_deal_properties([])

    assert "❌ **No properties found**" in result
    assert "Unable to retrieve deal properties" in result


def test_format_contact_properties_with_options_missing_labels():
    """Test contact properties with options missing labels."""
    properties_data = [
        {
            "name": "status",
            "label": "Status",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "test",
            "options": [
                {"value": "active"},  # Missing label
                {"label": "Inactive", "value": "inactive"},
                {},  # Empty option
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "**📋 Status**" in result
    assert "active, Inactive" in result


def test_format_company_properties_with_all_special_field_names():
    """Test company properties with many options to trigger '... and more' logic."""
    properties_data = [
        {
            "name": "industry_detailed",
            "label": "Detailed Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "business",
            "options": [
                {"label": "Technology", "value": "tech"},
                {"label": "Finance", "value": "finance"},
                {"label": "Healthcare", "value": "healthcare"},
                {"label": "Education", "value": "education"},
                {"label": "Manufacturing", "value": "manufacturing"},
                {"label": "Retail", "value": "retail"},
                {"label": "Consulting", "value": "consulting"},
                {"label": "Government", "value": "government"},
            ],
        }
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "**📋 Detailed Industry**" in result
    assert "Technology, Finance, Healthcare, Education, Manufacturing" in result
    assert "... and 3 more" in result


def test_format_deal_properties_with_hubspot_field_names():
    """Test deal properties with HubSpot specific field names and many options."""
    properties_data = [
        {
            "name": "dealstage_detailed",
            "label": "Detailed Deal Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "deal_info",
            "options": [
                {"label": "Appointment Scheduled", "value": "appointmentscheduled"},
                {"label": "Qualified to Buy", "value": "qualifiedtobuy"},
                {"label": "Presentation Scheduled", "value": "presentationscheduled"},
                {"label": "Decision Maker Bought-In", "value": "decisionmakerboughtin"},
                {"label": "Contract Sent", "value": "contractsent"},
                {"label": "Closed Won", "value": "closedwon"},
                {"label": "Closed Lost", "value": "closedlost"},
                {"label": "In Progress", "value": "inprogress"},
            ],
        }
    ]

    result = HubSpotFormatter.format_deal_properties(properties_data)

    assert "**📋 Detailed Deal Stage**" in result
    assert (
        "Appointment Scheduled, Qualified to Buy, Presentation Scheduled, Decision Maker Bought-In, Contract Sent"
        in result
    )
    assert "... and 3 more" in result


def test_format_deal():
    """Test the format_deal method."""
    deal_data = {
        "id": "123",
        "properties": {
            "dealname": "Test Deal",
            "amount": "1000",
            "dealstage": "proposal",
            "pipeline": "sales",
            "closedate": "2024-12-31",
            "createdate": "2024-01-01",
            "lastmodifieddate": "2024-06-01",
            "hubspot_owner_id": "456",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "💰 **HubSpot Deal**" in result
    assert "**Test Deal**" in result
    assert "$1,000.00" in result
    assert "proposal" in result
    assert "sales" in result
    assert "2024-12-31" in result
    assert "🆔 ID: 123" in result


def test_format_deal_missing_properties():
    """Test format_deal with missing properties."""
    deal_data = {
        "id": "789",
        # Missing properties key
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Unnamed deal**" in result
    assert "💰 Amount: N/A" in result


def test_format_deal_with_special_characters():
    """Test deal formatting with special characters."""
    deal_data = {
        "id": "special123",
        "properties": {
            "dealname": "Deal with <special> & characters",
            "amount": "2500.50",
            "dealstage": "stage & more",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Deal with <special> & characters**" in result
    assert "$2,500.50" in result
    assert "stage & more" in result


def test_format_deal_with_html_entities():
    """Test deal formatting with HTML entities."""
    deal_data = {
        "id": "html123",
        "properties": {
            "dealname": "Deal &amp; More",
            "amount": "1500",
            "dealstage": "&lt;stage&gt;",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Deal &amp; More**" in result
    assert "&lt;stage&gt;" in result


def test_format_deal_with_very_long_values():
    """Test deal formatting with very long values."""
    deal_data = {
        "id": "long123",
        "properties": {
            "dealname": "A" * 100,  # Very long deal name
            "amount": "999999999.99",
            "dealstage": "B" * 50,  # Very long stage
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "A" * 100 in result
    assert "$999,999,999.99" in result
    assert "B" * 50 in result


def test_format_deal_with_none_values():
    """Test deal formatting with None values."""
    deal_data = {
        "id": "none123",
        "properties": {
            "dealname": None,
            "amount": None,
            "dealstage": None,
            "pipeline": None,
            "closedate": None,
            "createdate": None,
            "lastmodifieddate": None,
            "hubspot_owner_id": None,
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Unnamed deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🔄 Pipeline: N/A" in result


def test_format_deal_with_empty_string_values():
    """Test deal formatting with empty string values."""
    deal_data = {
        "id": "empty123",
        "properties": {
            "dealname": "",
            "amount": "",
            "dealstage": "",
            "pipeline": "",
            "closedate": "",
            "createdate": "",
            "lastmodifieddate": "",
            "hubspot_owner_id": "",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "****" in result  # Empty string is preserved by clean() function
    assert "💰 Amount: N/A" in result


def test_format_deal_with_whitespace_values():
    """Test deal formatting with whitespace-only values."""
    deal_data = {
        "id": "space123",
        "properties": {
            "dealname": "   ",
            "amount": "  ",
            "dealstage": "\t",
            "pipeline": "\n",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**   **" in result  # Whitespace preserved
    assert "💰 Amount: $  " in result  # Whitespace preserved in amount too


def test_format_deal_with_missing_properties():
    """Test deal formatting when properties dict is missing keys."""
    deal_data = {
        "id": "missing123",
        "properties": {},  # Empty properties
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Unnamed deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result


def test_format_deal_with_missing_properties_key():
    """Test deal formatting when properties key is missing entirely."""
    deal_data = {
        "id": "noprops123",
        # No properties key at all
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Unnamed deal**" in result
    assert "💰 Amount: N/A" in result


def test_format_deal_with_invalid_amount():
    """Test deal formatting with invalid amount in format_deal method."""
    deal_data = {
        "id": "invalid123",
        "properties": {
            "dealname": "Invalid Amount Deal",
            "amount": "not_a_number",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Invalid Amount Deal**" in result
    assert "$not_a_number" in result


def test_format_deal_with_zero_amount():
    """Test deal formatting with zero amount in format_deal method."""
    deal_data = {
        "id": "zero123",
        "properties": {
            "dealname": "Zero Amount Deal",
            "amount": "0",
        },
    }

    result = HubSpotFormatter.format_deal(deal_data)

    assert "**Zero Amount Deal**" in result
    assert "💰 Amount: N/A" in result


def test_format_deal_properties_with_exact_field_names_for_coverage():
    """Test deal properties with exact field names to hit specific icon assignment lines."""
    properties_data = [
        {
            "name": "amount",
            "label": "Amount",
            "type": "string",  # Not number type so field name check applies
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "hs_deal_amount",
            "label": "HubSpot Amount",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "dealname",
            "label": "Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "hs_deal_name",
            "label": "HubSpot Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "dealstage",
            "label": "Deal Stage",
            "type": "string",
            "fieldType": "text",  # Not select type so field name check applies
            "groupName": "deal_info",
        },
        {
            "name": "hs_deal_stage",
            "label": "HubSpot Deal Stage",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "pipeline",
            "label": "Pipeline",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "hs_pipeline",
            "label": "HubSpot Pipeline",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
        {
            "name": "closedate",
            "label": "Close Date",
            "type": "string",
            "fieldType": "text",  # Not date type so field name check applies
            "groupName": "deal_info",
        },
        {
            "name": "hs_closedate",
            "label": "HubSpot Close Date",
            "type": "string",
            "fieldType": "text",
            "groupName": "deal_info",
        },
    ]

    result = HubSpotFormatter.format_deal_properties(properties_data)

    # These should hit the specific field name icon assignments
    assert "**💰 Amount**" in result
    assert "**💰 HubSpot Amount**" in result
    assert "**🏷️ Deal Name**" in result
    assert "**🏷️ HubSpot Deal Name**" in result
    assert "**📊 Deal Stage**" in result
    assert "**📊 HubSpot Deal Stage**" in result
    assert "**🔄 Pipeline**" in result
    assert "**🔄 HubSpot Pipeline**" in result
    assert "**📅 Close Date**" in result
    assert "**📅 HubSpot Close Date**" in result


def test_format_company_properties_with_exact_field_names_for_coverage():
    """Test company properties with exact field names to hit specific icon assignment lines."""
    properties_data = [
        {
            "name": "industry",
            "label": "Industry",
            "type": "string",
            "fieldType": "text",  # Not select type so field name check applies
            "groupName": "company_info",
        },
        {
            "name": "type",
            "label": "Company Type",
            "type": "string",
            "fieldType": "text",
            "groupName": "company_info",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    # These should hit the specific field name icon assignments
    assert "**🏭 Industry**" in result
    assert "**🏭 Company Type**" in result
