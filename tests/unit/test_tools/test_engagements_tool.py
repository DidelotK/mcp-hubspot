"""Unit tests for EngagementsTool."""

from unittest.mock import AsyncMock, Mock

import pytest

from hubspot_mcp.tools.engagements import EngagementsTool


@pytest.mark.asyncio
async def test_engagements_tool_execute_returns_formatted_text():
    mock_client = Mock()
    mock_client.get_engagements = AsyncMock(
        return_value=[
            {
                "id": "1",
                "properties": {
                    "engagement_type": "CALL",
                    "subject": "Follow-up call",
                    "createdate": "2024-01-01T00:00:00.000Z",
                    "lastmodifieddate": "2024-01-02T00:00:00.000Z",
                },
            }
        ]
    )

    tool = EngagementsTool(client=mock_client)
    result = await tool.execute({"limit": 10})

    assert len(result) == 1
    assert "Follow-up call" in result[0].text
    mock_client.get_engagements.assert_called_once_with(limit=10, after=None)
