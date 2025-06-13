from unittest.mock import MagicMock, patch

import pytest

from src.hubspot_mcp.tools import deal_tools


def make_mock_deal(**kwargs):
    d = {
        "id": "1",
        "properties": {
            "dealname": "Test Deal",
            "amount": "1000",
            "dealstage": "appointmentscheduled",
            "pipeline": "default",
            "closedate": "2024-12-31",
        },
    }
    d["properties"].update(kwargs)
    return d


def make_mock_api_response(results):
    mock = MagicMock()
    mock.results = results
    return mock


def test_list_hubspot_deals():
    mock_deals = [make_mock_deal(dealname="Deal 1"), make_mock_deal(dealname="Deal 2")]
    with (
        patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls,
        patch(
            "src.hubspot_mcp.tools.deal_tools.HubSpotFormatter.format_single_deal",
            side_effect=lambda d: d["properties"]["dealname"],
        ),
    ):
        instance = mock_client_cls.return_value
        instance.crm.deals.basic_api.get_page.return_value = make_mock_api_response(
            mock_deals
        )
        result = deal_tools.list_hubspot_deals(limit=2)
        assert result == ["Deal 1", "Deal 2"]
        instance.crm.deals.basic_api.get_page.assert_called_once()


def test_create_deal():
    mock_deal = make_mock_deal(dealname="Created Deal")
    with (
        patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls,
        patch(
            "src.hubspot_mcp.tools.deal_tools.HubSpotFormatter.format_single_deal",
            return_value={"dealname": "Created Deal"},
        ),
    ):
        instance = mock_client_cls.return_value
        instance.crm.deals.basic_api.create.return_value = mock_deal
        result = deal_tools.create_deal(dealname="Created Deal")
        assert result["dealname"] == "Created Deal"
        instance.crm.deals.basic_api.create.assert_called_once()


def test_get_deal_by_name_found():
    mock_deal = make_mock_deal(dealname="Found Deal")
    with (
        patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls,
        patch(
            "src.hubspot_mcp.tools.deal_tools.HubSpotFormatter.format_single_deal",
            return_value={"dealname": "Found Deal"},
        ),
    ):
        instance = mock_client_cls.return_value
        instance.crm.deals.basic_api.get_page.return_value = make_mock_api_response(
            [mock_deal]
        )
        result = deal_tools.get_deal_by_name("Found Deal")
        assert result["dealname"] == "Found Deal"
        instance.crm.deals.basic_api.get_page.assert_called_once()


def test_get_deal_by_name_not_found():
    with patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls:
        instance = mock_client_cls.return_value
        instance.crm.deals.basic_api.get_page.return_value = make_mock_api_response([])
        result = deal_tools.get_deal_by_name("Not Found")
        assert result is None
        instance.crm.deals.basic_api.get_page.assert_called_once()


def test_get_hubspot_deal_properties():
    mock_props = [
        {"name": "dealname", "type": "string"},
        {"name": "amount", "type": "number"},
    ]
    with (
        patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls,
        patch(
            "src.hubspot_mcp.tools.deal_tools.HubSpotFormatter.format_deal_properties",
            return_value=mock_props,
        ),
    ):
        instance = mock_client_cls.return_value
        instance.crm.properties.core_api.get_all.return_value = "api_response"
        result = deal_tools.get_hubspot_deal_properties()
        assert result == mock_props
        instance.crm.properties.core_api.get_all.assert_called_once()


def test_update_deal():
    mock_deal = make_mock_deal(dealname="Updated Deal")
    with (
        patch("src.hubspot_mcp.tools.deal_tools.HubSpotClient") as mock_client_cls,
        patch(
            "src.hubspot_mcp.tools.deal_tools.HubSpotFormatter.format_single_deal",
            return_value={"dealname": "Updated Deal"},
        ),
    ):
        instance = mock_client_cls.return_value
        instance.crm.deals.basic_api.update.return_value = mock_deal
        result = deal_tools.update_deal("1", {"dealname": "Updated Deal"})
        assert result["dealname"] == "Updated Deal"
        instance.crm.deals.basic_api.update.assert_called_once()
