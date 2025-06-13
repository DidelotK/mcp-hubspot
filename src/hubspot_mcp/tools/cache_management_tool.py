"""MCP tool for managing the HubSpot cache system."""

from typing import Any, Dict, List

import mcp.types as types

from .base import BaseTool


class CacheManagementTool(BaseTool):
    """Tool for managing the HubSpot cache system."""

    def get_tool_definition(self) -> types.Tool:
        """Return the cache management tool definition."""
        return types.Tool(
            name="manage_hubspot_cache",
            description="Manage the HubSpot cache system (view stats, clear cache)",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform on the cache",
                        "enum": ["info", "clear"],
                        "default": "info",
                    }
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute cache management action."""
        try:
            action = arguments.get("action", "info")

            if action == "info":
                cache_info = self.get_cache_info()
                formatted_result = self._format_cache_info(cache_info)
            elif action == "clear":
                self.clear_cache()
                formatted_result = "✅ **Cache Cleared Successfully**\n\nThe HubSpot cache has been cleared. All subsequent requests will fetch fresh data from the API."
            else:
                formatted_result = f"❌ **Invalid Action**\n\nUnknown action: {action}. Valid actions are: info, clear"

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)

    def _format_cache_info(self, cache_info: Dict[str, Any]) -> str:
        """Format cache information for display.

        Args:
            cache_info: Dictionary containing cache statistics

        Returns:
            str: Formatted cache information
        """
        result = "🗄️ **HubSpot Cache Information**\n\n"
        result += f"📊 **Statistics:**\n"
        result += f"  • Current size: {cache_info['size']} entries\n"
        result += f"  • Maximum size: {cache_info['maxsize']} entries\n"
        result += f"  • Time to live (TTL): {cache_info['ttl']} seconds\n"
        result += f"  • Cache utilization: {(cache_info['size'] / cache_info['maxsize'] * 100):.1f}%\n\n"

        if cache_info["size"] > 0:
            result += f"🔑 **Sample Cache Keys** (showing first {min(len(cache_info['keys']), 10)}):\n"
            for i, key in enumerate(cache_info["keys"][:10], 1):
                result += f"  {i}. {key[:16]}...\n"
        else:
            result += "🔑 **Cache Keys:** None (cache is empty)\n"

        result += "\n💡 **Tips:**\n"
        result += "  • Cache automatically expires after 5 minutes\n"
        result += "  • Use `clear` action to force refresh all data\n"
        result += "  • Cache is shared across all HubSpot tools\n"
        result += "  • Different API keys maintain separate cache entries"

        return result
