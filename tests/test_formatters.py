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

    result = HubSpotFormatter.format_contacts(contacts_data)

    assert "👥 **HubSpot Contacts** (2 found)" in result
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

    result = HubSpotFormatter.format_companies(companies_data)

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
        {"id": "202", "properties": {"dealname": "Deal without amount"}},
    ]

    result = HubSpotFormatter.format_deals(deals_data)

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


def test_format_deals_with_invalid_amount():
    """Test deal formatting with invalid amount."""
    deals_data = [
        {
            "id": "300",
            "properties": {
                "dealname": "Deal with invalid amount",
                "amount": "invalid_amount",
            },
        }
    ]

    result = HubSpotFormatter.format_deals(deals_data)

    assert "**Deal with invalid amount**" in result
    assert "$invalid_amount" in result


def test_format_empty_lists():
    """Test formatting with empty lists."""
    assert "👥 **HubSpot Contacts** (0 found)" in HubSpotFormatter.format_contacts([])
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
    """Test contact properties formatting with special field types."""
    properties_data = [
        {
            "name": "email",
            "label": "Email Address",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
            "description": "Contact email",
        },
        {
            "name": "phone",
            "label": "Phone Number",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
        },
        {
            "name": "birthdate",
            "label": "Birth Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "demographic_information",
        },
        {
            "name": "notes",
            "label": "Notes",
            "type": "string",
            "fieldType": "textarea",
            "groupName": "other",
        },
        {
            "name": "resume",
            "label": "Resume",
            "type": "string",
            "fieldType": "file",
            "groupName": "other",
        },
        {
            "name": "newsletter",
            "label": "Newsletter Subscription",
            "type": "boolean",
            "fieldType": "checkbox",
            "groupName": "preferences",
        },
        {
            "name": "company",
            "label": "Company",
            "type": "string",
            "fieldType": "text",
            "groupName": "company_info",
        },
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    # Check for specific icons based on field types and names
    assert "📧 Email Address" in result  # Email icon
    assert "📞 Phone Number" in result  # Phone icon
    assert "📅 Birth Date" in result  # Date icon
    assert "📄 Notes" in result  # Textarea icon
    assert "📎 Resume" in result  # File icon
    assert "☑️ Newsletter Subscription" in result  # Checkbox icon
    assert "🏢 Company" in result  # Company icon


def test_format_contact_properties_with_select_options():
    """Test contact properties formatting with select field options."""
    properties_data = [
        {
            "name": "industry",
            "label": "Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "company_information",
            "options": [
                {"label": "Technology", "value": "TECH"},
                {"label": "Finance", "value": "FIN"},
                {"label": "Healthcare", "value": "HEALTH"},
                {"label": "Education", "value": "EDU"},
                {"label": "Manufacturing", "value": "MFG"},
                {"label": "Retail", "value": "RETAIL"},
                {"label": "Other", "value": "OTHER"},
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "📋 Industry" in result  # Select icon
    assert (
        "📋 Options: Technology, Finance, Healthcare, Education, Manufacturing, ... and 2 more"
        in result
    )


def test_format_contact_properties_with_few_select_options():
    """Test contact properties formatting with few select options."""
    properties_data = [
        {
            "name": "status",
            "label": "Status",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "other",
            "options": [
                {"label": "Active", "value": "ACTIVE"},
                {"label": "Inactive", "value": "INACTIVE"},
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "📋 Status" in result
    assert "📋 Options: Active, Inactive" in result  # Should not show "... and X more"


def test_format_deal_properties_with_special_field_names():
    """Test deal properties formatting with special field names."""
    properties_data = [
        {
            "name": "amount",
            "label": "Deal Amount",
            "type": "number",
            "fieldType": "number",
            "groupName": "dealinformation",
            "description": "The deal amount",
        },
        {
            "name": "dealname",
            "label": "Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "dealinformation",
        },
        {
            "name": "dealstage",
            "label": "Deal Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "dealinformation",
        },
        {
            "name": "pipeline",
            "label": "Pipeline",
            "type": "string",
            "fieldType": "text",
            "groupName": "dealinformation",
        },
        {
            "name": "closedate",
            "label": "Close Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "dealinformation",
        },
    ]

    result = HubSpotFormatter.format_deal_properties(properties_data)

    # Check for specific icons based on field type first, then name
    # field_type has priority over name in the elif chain, but "text" is not in field_type conditions
    assert "🔢 Deal Amount" in result  # number field type has priority over amount name
    assert (
        "🏷️ Deal Name" in result
    )  # text field type not in elif, so dealname name condition applies
    assert (
        "📋 Deal Stage" in result
    )  # select field type has priority over dealstage name
    assert (
        "🔄 Pipeline" in result
    )  # text field type not in elif, so pipeline name condition applies
    assert "📅 Close Date" in result  # date field type has priority over closedate name


def test_format_company_properties_with_special_field_names():
    """Test company properties formatting with special field names."""
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
            "description": "The company website",
        },
        {
            "name": "industry",
            "label": "Industry",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "business_information",
        },
        {
            "name": "annualrevenue",
            "label": "Annual Revenue",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial_information",
        },
        {
            "name": "city",
            "label": "City",
            "type": "string",
            "fieldType": "text",
            "groupName": "address_information",
        },
        {
            "name": "phone",
            "label": "Phone",
            "type": "string",
            "fieldType": "text",
            "groupName": "contact_information",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    # Check for specific icons based on field names
    assert "🏢 Company Name" in result  # Company name icon
    assert "🌐 Website Domain" in result  # Domain icon
    assert "📋 Industry" in result  # Industry icon
    assert "🔢 Annual Revenue" in result  # Revenue icon
    assert "📍 City" in result  # City icon
    assert "📞 Phone" in result  # Phone icon


def test_format_properties_with_missing_fields():
    """Test properties formatting with missing fields."""
    properties_data = [
        {
            "name": "custom_field",
            # Missing label, type, fieldType, groupName, description
        },
        {
            "label": "Another Field",
            "type": "string",
            # Missing name, fieldType, groupName
        },
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "🔧 **HubSpot Contact Properties** (2 properties)" in result
    assert "## 📁 Other" in result  # Default group for missing groupName
    assert "**📝 N/A**" in result  # Default label
    assert "`custom_field`" in result
    assert "`N/A`" in result  # Default name


def test_format_properties_with_empty_options():
    """Test properties formatting with empty options list."""
    properties_data = [
        {
            "name": "status",
            "label": "Status",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "other",
            "options": [],  # Empty options
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "📋 Status" in result
    # Should not include options line when options is empty
    assert "📋 Options:" not in result


def test_format_deal_properties_empty():
    """Test deal properties formatting with empty list."""
    result = HubSpotFormatter.format_deal_properties([])

    assert "❌ **No properties found**" in result
    assert "Unable to retrieve deal properties" in result


def test_format_contact_properties_with_options_missing_labels():
    """Test contact properties with options that have missing labels."""
    properties_data = [
        {
            "name": "priority",
            "label": "Priority",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "other",
            "options": [
                {"value": "HIGH"},  # Missing label
                {"label": "Medium", "value": "MEDIUM"},
                {"value": "LOW"},  # Missing label
            ],
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "📋 Priority" in result
    assert (
        "📋 Options: HIGH, Medium, LOW" in result
    )  # Should use value when label is missing


def test_format_company_properties_with_all_special_field_names():
    """Test company properties with all special field name cases."""
    properties_data = [
        {
            "name": "hs_email_domain",
            "label": "Email Domain",
            "type": "string",
            "fieldType": "text",
            "groupName": "contact_info",
        },
        {
            "name": "mobilephone",
            "label": "Mobile Phone",
            "type": "string",
            "fieldType": "text",
            "groupName": "contact_info",
        },
        {
            "name": "associatedcompanyid",
            "label": "Associated Company",
            "type": "string",
            "fieldType": "text",
            "groupName": "associations",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    # These names are not in the special company name lists, so they use default text icon
    assert (
        "📝 Email Domain" in result
    )  # Default text icon (not in company special names)
    assert (
        "📝 Mobile Phone" in result
    )  # Default text icon (not in company special names)
    assert (
        "📝 Associated Company" in result
    )  # Default text icon (not in company special names)


def test_format_deal_properties_with_hubspot_field_names():
    """Test deal properties with HubSpot-specific field names."""
    properties_data = [
        {
            "name": "hs_deal_amount",
            "label": "HubSpot Deal Amount",
            "type": "number",
            "fieldType": "number",
            "groupName": "dealinformation",
        },
        {
            "name": "hs_deal_name",
            "label": "HubSpot Deal Name",
            "type": "string",
            "fieldType": "text",
            "groupName": "dealinformation",
        },
        {
            "name": "hs_deal_stage",
            "label": "HubSpot Deal Stage",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "dealinformation",
        },
        {
            "name": "hs_pipeline",
            "label": "HubSpot Pipeline",
            "type": "string",
            "fieldType": "text",
            "groupName": "dealinformation",
        },
        {
            "name": "hs_closedate",
            "label": "HubSpot Close Date",
            "type": "date",
            "fieldType": "date",
            "groupName": "dealinformation",
        },
    ]

    result = HubSpotFormatter.format_deal_properties(properties_data)

    # Check for specific icons based on field type first, then name
    # field_type has priority over name in the elif chain, but "text" is not in field_type conditions
    assert (
        "🔢 HubSpot Deal Amount" in result
    )  # number field type has priority over hs_deal_amount name
    assert (
        "🏷️ HubSpot Deal Name" in result
    )  # text field type not in elif, so hs_deal_name name condition applies
    assert (
        "📋 HubSpot Deal Stage" in result
    )  # select field type has priority over hs_deal_stage name
    assert (
        "🔄 HubSpot Pipeline" in result
    )  # text field type not in elif, so hs_pipeline name condition applies
    assert (
        "📅 HubSpot Close Date" in result
    )  # date field type has priority over hs_closedate name


def test_format_deal():
    """Test formatting a single deal."""
    deal = {
        "id": "12345",
        "properties": {
            "dealname": "Enterprise Contract",
            "amount": "75000",
            "dealstage": "contractsent",
            "pipeline": "enterprise",
            "closedate": "2024-12-31",
            "description": "Large enterprise deal for Q4",
        },
    }

    result = HubSpotFormatter.format_deal(deal)

    assert "💰 **HubSpot Deal Updated**" in result
    assert "**Enterprise Contract**" in result
    assert "💰 Amount: 75000" in result
    assert "📊 Stage: contractsent" in result
    assert "🔄 Pipeline: enterprise" in result
    assert "📅 Close Date: 2024-12-31" in result
    assert "📝 Description: Large enterprise deal for Q4" in result
    assert "🆔 ID: 12345" in result


def test_format_deal_missing_properties():
    """Test formatting a deal with missing properties."""
    deal = {"id": "12345", "properties": {"dealname": "Enterprise Contract"}}

    result = HubSpotFormatter.format_deal(deal)

    assert "💰 **HubSpot Deal Updated**" in result
    assert "**Enterprise Contract**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🔄 Pipeline: N/A" in result
    assert "📅 Close Date: N/A" in result
    assert "📝 Description: N/A" in result
    assert "🆔 ID: 12345" in result


def test_format_deal_empty():
    """Test formatting an empty deal."""
    deal = {"id": "12345", "properties": {}}

    result = HubSpotFormatter.format_deal(deal)

    assert "💰 **HubSpot Deal Updated**" in result
    assert "**Unnamed Deal**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🔄 Pipeline: N/A" in result
    assert "📅 Close Date: N/A" in result
    assert "📝 Description: N/A" in result
    assert "🆔 ID: 12345" in result
