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


def test_list_hubspot_deals(monkeypatch):
    mock_deals = [make_mock_deal(dealname="Deal 1"), make_mock_deal(dealname="Deal 2")]
    mock_response = make_mock_api_response(mock_deals)
    mock_get_page = MagicMock(return_value=mock_response)
    mock_basic_api = MagicMock(get_page=mock_get_page)
    mock_deals = MagicMock(basic_api=mock_basic_api)
    mock_crm = MagicMock(deals=mock_deals)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    monkeypatch.setattr(
        deal_tools.HubSpotFormatter,
        "format_single_deal",
        lambda d: d["properties"]["dealname"],
    )
    result = deal_tools.list_hubspot_deals(limit=2)
    assert result == ["Deal 1", "Deal 2"]
    mock_get_page.assert_called_once()


def test_create_deal(monkeypatch):
    mock_deal = make_mock_deal(
        dealname="Created Deal",
        amount="1000",
        dealstage="appointmentscheduled",
        pipeline="default",
        closedate="2024-12-31",
        hubspot_owner_id="123",
        description="Test description",
    )
    mock_create = MagicMock(return_value=mock_deal)
    mock_basic_api = MagicMock(create=mock_create)
    mock_deals = MagicMock(basic_api=mock_basic_api)
    mock_crm = MagicMock(deals=mock_deals)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    monkeypatch.setattr(
        deal_tools.HubSpotFormatter,
        "format_single_deal",
        lambda d: {"dealname": d["properties"]["dealname"]},
    )
    result = deal_tools.create_deal(
        dealname="Created Deal",
        amount="1000",
        dealstage="appointmentscheduled",
        pipeline="default",
        closedate="2024-12-31",
        hubspot_owner_id="123",
        description="Test description",
    )
    assert result["dealname"] == "Created Deal"
    mock_create.assert_called_once()


def test_get_deal_by_name_found(monkeypatch):
    mock_deal = make_mock_deal(dealname="Found Deal")
    mock_response = make_mock_api_response([mock_deal])
    mock_get_page = MagicMock(return_value=mock_response)
    mock_basic_api = MagicMock(get_page=mock_get_page)
    mock_deals = MagicMock(basic_api=mock_basic_api)
    mock_crm = MagicMock(deals=mock_deals)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    monkeypatch.setattr(
        deal_tools.HubSpotFormatter,
        "format_single_deal",
        lambda d: {"dealname": d["properties"]["dealname"]},
    )
    result = deal_tools.get_deal_by_name("Found Deal")
    assert result["dealname"] == "Found Deal"
    mock_get_page.assert_called_once()


def test_get_deal_by_name_not_found(monkeypatch):
    mock_response = MagicMock()
    mock_response.results = []
    mock_get_page = MagicMock(return_value=mock_response)
    mock_basic_api = MagicMock(get_page=mock_get_page)
    mock_deals = MagicMock(basic_api=mock_basic_api)
    mock_crm = MagicMock(deals=mock_deals)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    result = deal_tools.get_deal_by_name("NonExistentDeal")
    assert result is None
    mock_get_page.assert_called_once_with(
        limit=1,
        properties=["dealname", "amount", "dealstage", "pipeline", "closedate"],
        filter_groups=[
            {
                "filters": [
                    {
                        "propertyName": "dealname",
                        "operator": "EQ",
                        "value": "NonExistentDeal",
                    }
                ]
            }
        ],
        archived=False,
    )


def test_get_hubspot_deal_properties(monkeypatch):
    mock_props = [
        {"name": "dealname", "type": "string"},
        {"name": "amount", "type": "number"},
    ]
    mock_get_all = MagicMock(return_value="api_response")
    mock_core_api = MagicMock(get_all=mock_get_all)
    mock_properties = MagicMock(core_api=mock_core_api)
    mock_crm = MagicMock(properties=mock_properties)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    monkeypatch.setattr(
        deal_tools.HubSpotFormatter, "format_deal_properties", lambda x: mock_props
    )
    result = deal_tools.get_hubspot_deal_properties()
    assert result == mock_props
    mock_get_all.assert_called_once()


def test_update_deal(monkeypatch):
    mock_deal = make_mock_deal(dealname="Updated Deal")
    mock_update = MagicMock(return_value=mock_deal)
    mock_basic_api = MagicMock(update=mock_update)
    mock_deals = MagicMock(basic_api=mock_basic_api)
    mock_crm = MagicMock(deals=mock_deals)
    mock_client = MagicMock(crm=mock_crm)
    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: mock_client
    )
    monkeypatch.setattr(
        deal_tools.HubSpotFormatter,
        "format_single_deal",
        lambda d: {"dealname": d["properties"]["dealname"]},
    )
    result = deal_tools.update_deal("1", {"dealname": "Updated Deal"})
    assert result["dealname"] == "Updated Deal"
    mock_update.assert_called_once()


def test_get_deal_by_name_not_found_real_logic(monkeypatch):
    # On instancie un vrai client, mais on monkeypatch juste la méthode get_page
    from src.hubspot_mcp.tools import deal_tools

    class DummyBasicApi:
        def get_page(self, *args, **kwargs):
            class DummyResponse:
                results = []

            return DummyResponse()

    class DummyCrm:
        deals = type("deals", (), {"basic_api": DummyBasicApi()})()

    class DummyClient:
        crm = DummyCrm()

    monkeypatch.setattr(
        deal_tools, "HubSpotClient", lambda *args, **kwargs: DummyClient()
    )
    result = deal_tools.get_deal_by_name("NonExistentDeal")
    assert result is None
