"""Tests pour les formatters HubSpot."""

import pytest

from src.hubspot_mcp.formatters import HubSpotFormatter


def test_format_contacts():
    """Test du formatage des contacts."""
    contacts_data = [
        {
            "id": "1",
            "properties": {
                "firstname": "Jean",
                "lastname": "Dupont", 
                "email": "jean.dupont@example.com",
                "company": "Acme Corp",
                "phone": "+33123456789",
                "createdate": "2024-01-01T00:00:00Z"
            }
        },
        {
            "id": "2",
            "properties": {
                "firstname": "Marie",
                "lastname": "Martin",
                "email": "marie.martin@example.com"
            }
        }
    ]
    
    result = HubSpotFormatter.format_contacts(contacts_data)
    
    assert "📋 **Contacts HubSpot** (2 trouvés)" in result
    assert "**Jean Dupont**" in result
    assert "jean.dupont@example.com" in result
    assert "Acme Corp" in result
    assert "**Marie Martin**" in result
    assert "marie.martin@example.com" in result
    assert "🆔 ID: 1" in result
    assert "🆔 ID: 2" in result


def test_format_companies():
    """Test du formatage des entreprises."""
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
                "createdate": "2024-01-15T00:00:00Z"
            }
        },
        {
            "id": "101",
            "properties": {
                "name": "Startup Inc"
            }
        }
    ]
    
    result = HubSpotFormatter.format_companies(companies_data)
    
    assert "🏢 **Entreprises HubSpot** (2 trouvées)" in result
    assert "**Tech Solutions**" in result
    assert "techsolutions.com" in result
    assert "Paris, Île-de-France, France" in result
    assert "Technology" in result
    assert "**Startup Inc**" in result
    assert "🆔 ID: 100" in result
    assert "🆔 ID: 101" in result


def test_format_deals():
    """Test du formatage des transactions."""
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
                "hubspot_owner_id": "12345"
            }
        },
        {
            "id": "201",
            "properties": {
                "dealname": "Petit deal",
                "amount": "0"
            }
        },
        {
            "id": "202",
            "properties": {
                "dealname": "Deal sans montant"
            }
        }
    ]
    
    result = HubSpotFormatter.format_deals(deals_data)
    
    assert "💰 **Transactions HubSpot** (3 trouvées)" in result
    assert "**Gros contrat**" in result
    assert "50,000.00 €" in result
    assert "negotiation" in result
    assert "sales" in result
    assert "**Petit deal**" in result
    assert "**Deal sans montant**" in result
    assert "🆔 ID: 200" in result
    assert "🆔 ID: 201" in result
    assert "🆔 ID: 202" in result


def test_format_deals_with_invalid_amount():
    """Test du formatage des deals avec montant invalide."""
    deals_data = [
        {
            "id": "300",
            "properties": {
                "dealname": "Deal avec montant invalide",
                "amount": "invalid_amount"
            }
        }
    ]
    
    result = HubSpotFormatter.format_deals(deals_data)
    
    assert "**Deal avec montant invalide**" in result
    assert "invalid_amount €" in result


def test_format_empty_lists():
    """Test du formatage avec des listes vides."""
    assert "📋 **Contacts HubSpot** (0 trouvés)" in HubSpotFormatter.format_contacts([])
    assert "🏢 **Entreprises HubSpot** (0 trouvées)" in HubSpotFormatter.format_companies([])
    assert "💰 **Transactions HubSpot** (0 trouvées)" in HubSpotFormatter.format_deals([])


def test_format_single_transaction():
    """Test du formatage d'une transaction unique."""
    transaction_data = {
        "id": "500",
        "properties": {
            "dealname": "Contrat Premium",
            "amount": "25000.00",
            "dealstage": "proposal",
            "pipeline": "enterprise",
            "closedate": "2024-12-31",
            "createdate": "2024-06-01T00:00:00Z",
            "lastmodifieddate": "2024-06-12T12:00:00Z",
            "hubspot_owner_id": "98765"
        }
    }
    
    result = HubSpotFormatter.format_single_transaction(transaction_data)
    
    assert "💰 **Transaction HubSpot**" in result
    assert "**Contrat Premium**" in result
    assert "25,000.00 €" in result
    assert "proposal" in result
    assert "enterprise" in result
    assert "2024-12-31" in result
    assert "🆔 ID: 500" in result


def test_format_single_transaction_not_found():
    """Test du formatage quand aucune transaction n'est trouvée."""
    result = HubSpotFormatter.format_single_transaction(None)
    
    assert "🔍 **Transaction non trouvée**" in result
    assert "Aucune transaction ne correspond au nom spécifié" in result


def test_format_single_transaction_minimal_data():
    """Test du formatage d'une transaction avec données minimales."""
    transaction_data = {
        "id": "600",
        "properties": {
            "dealname": "Deal Simple"
        }
    }
    
    result = HubSpotFormatter.format_single_transaction(transaction_data)
    
    assert "**Deal Simple**" in result
    assert "💰 Montant: N/A" in result
    assert "📊 Étape: N/A" in result
    assert "🆔 ID: 600" in result 