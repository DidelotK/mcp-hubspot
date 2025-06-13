"""Tests for format_engagements."""

from hubspot_mcp.formatters.hubspot_formatter import HubSpotFormatter


def test_format_engagements_returns_string():
    data = [
        {
            "id": "1",
            "properties": {
                "engagement_type": "EMAIL",
                "subject": "Intro Email",
                "createdate": "2024-01-01T10:00:00.000Z",
                "lastmodifieddate": "2024-01-01T11:00:00.000Z",
            },
        }
    ]

    out = HubSpotFormatter.format_engagements(data)
    assert "Intro Email" in out
    assert "📞" in out
