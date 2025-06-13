from src.hubspot_mcp.tools import deal_tools


def test_get_deal_by_name_not_found_real_logic(monkeypatch):
    class DummyBasicApi:
        def get_page(self, *args, **kwargs):
            class DummyResponse:
                results = []

            return DummyResponse()

    class DummyCrm:
        deals = type("deals", (), {"basic_api": DummyBasicApi()})()

    class DummyClient:
        crm = DummyCrm()

    monkeypatch.setattr(deal_tools, "HubSpotClient", lambda: DummyClient())
    result = deal_tools.get_deal_by_name("NonExistentDeal")
    assert result is None
