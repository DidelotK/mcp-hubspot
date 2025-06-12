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
<<<<<<< HEAD
    """Test du formatage des deals."""
=======
    """Test deal formatting."""
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
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

<<<<<<< HEAD
    assert "💰 **Deals HubSpot** (3 trouvés)" in result
=======
    assert "💰 **HubSpot Deals** (3 found)" in result
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
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
<<<<<<< HEAD
    """Test du formatage avec des listes vides."""
    assert "📋 **Contacts HubSpot** (0 trouvés)" in HubSpotFormatter.format_contacts([])
    assert (
        "🏢 **Entreprises HubSpot** (0 trouvées)"
        in HubSpotFormatter.format_companies([])
    )
    assert "💰 **Deals HubSpot** (0 trouvés)" in HubSpotFormatter.format_deals(
        []
    )


def test_format_single_deal():
    """Test du formatage d'un deal unique."""
    deal_data = {
=======
    """Test formatting with empty lists."""
    assert "📋 **HubSpot Contacts** (0 found)" in HubSpotFormatter.format_contacts([])
    assert "🏢 **HubSpot Companies** (0 found)" in HubSpotFormatter.format_companies([])
    assert "💰 **HubSpot Deals** (0 found)" in HubSpotFormatter.format_deals([])


def test_format_single_transaction():
    """Test single transaction formatting."""
    transaction_data = {
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
        "id": "500",
        "properties": {
            "dealname": "Contrat Premium",
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

<<<<<<< HEAD
    assert "💰 **Deal HubSpot**" in result
=======
    assert "💰 **HubSpot Transaction**" in result
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage
    assert "**Contrat Premium**" in result
    assert "$25,000.00" in result
    assert "proposal" in result
    assert "enterprise" in result
    assert "2024-12-31" in result
    assert "🆔 ID: 500" in result


<<<<<<< HEAD
def test_format_single_deal_not_found():
    """Test du formatage quand aucun deal n'est trouvé."""
    result = HubSpotFormatter.format_single_deal(None)

    assert "🔍 **Deal non trouvé**" in result
    assert "Aucun deal ne correspond au nom spécifié" in result


def test_format_single_deal_minimal_data():
    """Test du formatage d'un deal avec données minimales."""
    deal_data = {"id": "600", "properties": {"dealname": "Deal Simple"}}
=======
def test_format_single_transaction_not_found():
    """Test formatting when no transaction is found."""
    result = HubSpotFormatter.format_single_transaction(None)

    assert "🔍 **Transaction not found**" in result
    assert "No transaction matches the specified name" in result


def test_format_single_transaction_minimal_data():
    """Test transaction formatting with minimal data."""
    transaction_data = {"id": "600", "properties": {"dealname": "Deal Simple"}}
>>>>>>> feat: add get_hubspot_deal_properties tool - Add new DealPropertiesTool to retrieve HubSpot deal properties - Add get_deal_properties method to HubSpotClient - Add format_deal_properties method to HubSpotFormatter - Register new tool in handlers and tools module - Add comprehensive tests for the new tool - Translate all remaining French text to English - Update test assertions to match English translations - All 35 tests passing with 89% coverage

    result = HubSpotFormatter.format_single_deal(deal_data)

    assert "**Deal Simple**" in result
    assert "💰 Amount: N/A" in result
    assert "📊 Stage: N/A" in result
    assert "🆔 ID: 600" in result


def test_format_contact_properties():
    """Test contact properties formatting."""
    properties_data = [
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
        {
            "name": "birthdate",
            "label": "Date de naissance",
            "type": "date",
            "fieldType": "date",
            "groupName": "demographic_information",
        },
        {
            "name": "industry",
            "label": "Secteur d'activité",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "company_information",
            "options": [
                {"label": "Technologie", "value": "TECHNOLOGY"},
                {"label": "Finance", "value": "FINANCE"},
                {"label": "Santé", "value": "HEALTHCARE"},
            ],
        },
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "🔧 **HubSpot Contact Properties** (4 properties)" in result
    assert "## 📁 contactinformation" in result
    assert "**📝 Prénom**" in result
    assert "`firstname`" in result
    assert "**📧 Adresse e-mail**" in result
    assert "`email`" in result
    assert "## 📁 demographic_information" in result
    assert "**📅 Date de naissance**" in result
    assert "## 📁 company_information" in result
    assert "**📋 Secteur d'activité**" in result
    assert "Technologie, Finance, Santé" in result


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
            "label": "Champ personnalisé",
            "type": "string",
            "fieldType": "text",
        }
    ]

    result = HubSpotFormatter.format_contact_properties(properties_data)

    assert "🔧 **HubSpot Contact Properties** (1 properties)" in result
    assert "## 📁 Other" in result
    assert "**📝 Champ personnalisé**" in result
    assert "`custom_field`" in result


def test_format_company_properties():
    """Test du formatage des propriétés d'entreprises."""
    properties_data = [
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
        {
            "name": "industry",
            "label": "Secteur d'activité",
            "type": "enumeration",
            "fieldType": "select",
            "groupName": "business_information",
            "options": [
                {"label": "Technologie", "value": "TECHNOLOGY"},
                {"label": "Finance", "value": "FINANCE"},
                {"label": "Santé", "value": "HEALTHCARE"},
            ],
        },
        {
            "name": "annualrevenue",
            "label": "Chiffre d'affaires annuel",
            "type": "number",
            "fieldType": "number",
            "groupName": "financial_information",
        },
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "🏢 **Propriétés des Entreprises HubSpot** (4 propriétés)" in result
    assert "## 📁 companyinformation" in result
    assert "## 📁 business_information" in result
    assert "## 📁 financial_information" in result
    assert "**🏢 Nom de l'entreprise**" in result
    assert "**🌐 Domaine web**" in result
    assert "**📋 Secteur d'activité**" in result
    assert "**🔢 Chiffre d'affaires annuel**" in result
    assert "`name`" in result
    assert "`domain`" in result
    assert "Le nom de l'entreprise" in result
    assert "Le domaine web de l'entreprise" in result
    assert "Technologie, Finance, Santé" in result


def test_format_company_properties_empty():
    """Test du formatage des propriétés d'entreprises avec liste vide."""
    result = HubSpotFormatter.format_company_properties([])

    assert "❌ **Aucune propriété trouvée**" in result
    assert "Impossible de récupérer les propriétés des entreprises" in result


def test_format_company_properties_minimal():
    """Test du formatage des propriétés d'entreprises avec données minimales."""
    properties_data = [
        {
            "name": "custom_company_field",
            "label": "Champ personnalisé entreprise",
            "type": "string",
            "fieldType": "text",
        }
    ]

    result = HubSpotFormatter.format_company_properties(properties_data)

    assert "🏢 **Propriétés des Entreprises HubSpot** (1 propriétés)" in result
    assert "## 📁 Autres" in result  # Groupe par défaut
    assert "**📝 Champ personnalisé entreprise**" in result
    assert "`custom_company_field`" in result
