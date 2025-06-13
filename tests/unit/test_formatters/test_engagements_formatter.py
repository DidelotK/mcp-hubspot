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
    assert "Snippet" not in out  # No body provided


def test_format_engagements_includes_body_snippet():
    data = [
        {
            "id": "2",
            "properties": {
                "engagement_type": "NOTE",
                "createdate": "2024-01-01T10:00:00.000Z",
                "lastmodifieddate": "2024-01-01T11:00:00.000Z",
                "metadata": {
                    "body": "This is a very important note about the customer meeting tomorrow at 10am.",
                },
            },
        }
    ]

    out = HubSpotFormatter.format_engagements(data)
    assert "📝 Snippet" in out
