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
