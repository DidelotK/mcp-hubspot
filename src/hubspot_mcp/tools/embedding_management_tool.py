"""MCP tool for managing HubSpot embedding indexes."""

from typing import Any, Dict, List

import mcp.types as types

from .enhanced_base import EnhancedBaseTool


class EmbeddingManagementTool(EnhancedBaseTool):
    """Tool for managing HubSpot embedding indexes and cache."""

    def get_tool_definition(self) -> types.Tool:
        """Return the embedding management tool definition."""
        return types.Tool(
            name="manage_hubspot_embeddings",
            description="Manage HubSpot embedding indexes for semantic search (build, stats, clear)",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform on embeddings",
                        "enum": ["info", "build", "clear", "rebuild"],
                        "default": "info",
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["contacts", "companies", "deals", "engagements"],
                        },
                        "description": "Entity types to build/rebuild indexes for (used with build/rebuild actions)",
                        "default": ["contacts", "companies", "deals", "engagements"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entities to index per type (default: 1000)",
                        "default": 1000,
                        "minimum": 10,
                        "maximum": 10000,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute embedding management action."""
        try:
            action = arguments.get("action", "info")
            entity_types = arguments.get(
                "entity_types", ["contacts", "companies", "deals", "engagements"]
            )
            limit = arguments.get("limit", 1000)

            if action == "info":
                formatted_result = await self._get_embedding_info()
            elif action == "build":
                formatted_result = await self._build_indexes(entity_types, limit)
            elif action == "rebuild":
                formatted_result = await self._rebuild_indexes(entity_types, limit)
            elif action == "clear":
                formatted_result = self._clear_embeddings()
            else:
                formatted_result = f"❌ **Invalid Action**\n\nUnknown action: {action}. Valid actions are: info, build, clear, rebuild"

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)

    async def _get_embedding_info(self) -> str:
        """Get information about the current embedding system status."""
        stats = self.get_embedding_stats()

        if not stats.get("enabled", False):
            return (
                "🤖 **HubSpot Embedding System**\n\n"
                "❌ **Status**: Disabled\n\n"
                "The embedding system is not currently enabled. "
                "This could be due to missing dependencies or initialization issues.\n\n"
                "💡 **To enable embeddings:**\n"
                "- Ensure faiss-cpu and sentence-transformers are installed\n"
                "- Try building an index using the 'build' action"
            )

        result = "🤖 **HubSpot Embedding System Information**\n\n"
        result += f"✅ **Status**: {stats.get('status', 'unknown')}\n"
        result += f"📊 **Statistics:**\n"
        result += f"  • Total indexed entities: {stats.get('total_entities', 0)}\n"
        result += f"  • Vector dimension: {stats.get('dimension', 'N/A')}\n"
        result += f"  • Index type: {stats.get('index_type', 'N/A')}\n"
        result += f"  • Model: {stats.get('model_name', 'N/A')}\n"
        result += f"  • Embedding cache size: {stats.get('cache_size', 0)} entries\n\n"

        if stats.get("total_entities", 0) > 0:
            result += "🔍 **Available for Semantic Search**: Yes\n\n"
            result += "💡 **Next Steps:**\n"
            result += "- Try semantic search with natural language queries\n"
            result += "- Use hybrid search for best results\n"
            result += "- Rebuild indexes periodically for fresh data\n"
        else:
            result += "🔍 **Available for Semantic Search**: No\n\n"
            result += "💡 **To start using semantic search:**\n"
            result += "1. Build embedding indexes using 'build' action\n"
            result += (
                "2. This will download the AI model and process your HubSpot data\n"
            )
            result += (
                "3. Once complete, you can use semantic search across all entities\n"
            )

        return result

    async def _build_indexes(self, entity_types: List[str], limit: int) -> str:
        """Build embedding indexes for specified entity types."""
        if not self.enable_embeddings:
            return (
                "❌ **Embeddings Disabled**\n\n"
                "Embedding functionality is not enabled for this tool instance."
            )

        result = f"🔨 **Building Embedding Indexes**\n\n"
        result += f"**Entity Types**: {', '.join(entity_types)}\n"
        result += f"**Limit per Type**: {limit}\n\n"

        build_results = {}
        total_indexed = 0

        for entity_type in entity_types:
            result += f"📊 **Processing {entity_type}...**\n"

            try:
                build_result = await self.build_embedding_index(entity_type, limit)
                build_results[entity_type] = build_result

                if build_result.get("success", False):
                    indexed_count = build_result.get("entities_indexed", 0)
                    total_indexed += indexed_count
                    result += f"  ✅ Indexed {indexed_count} {entity_type}\n"
                else:
                    error = build_result.get("error", "Unknown error")
                    result += f"  ❌ Failed: {error}\n"

            except Exception as e:
                result += f"  ❌ Error: {str(e)}\n"
                build_results[entity_type] = {"success": False, "error": str(e)}

        result += f"\n🎉 **Build Complete**\n"
        result += f"**Total Entities Indexed**: {total_indexed}\n"

        # Get final stats
        stats = self.get_embedding_stats()
        if stats.get("enabled", False):
            result += f"**Vector Dimension**: {stats.get('dimension', 'N/A')}\n"
            result += f"**Model**: {stats.get('model_name', 'N/A')}\n"

        result += f"\n💡 **What's Next?**\n"
        result += f"- Use 'semantic_search_hubspot' tool for AI-powered searches\n"
        result += f"- Try natural language queries like 'technology companies' or 'enterprise deals'\n"
        result += f"- Rebuild indexes periodically to include new HubSpot data\n"

        return result

    async def _rebuild_indexes(self, entity_types: List[str], limit: int) -> str:
        """Rebuild embedding indexes (clear and build)."""
        result = "🔄 **Rebuilding Embedding Indexes**\n\n"

        # Clear existing embeddings first
        result += "🗑️  Clearing existing indexes...\n"
        self.clear_embedding_cache()
        result += "✅ Existing indexes cleared\n\n"

        # Build new indexes
        build_result = await self._build_indexes(entity_types, limit)
        result += build_result.replace(
            "🔨 **Building Embedding Indexes**", "🔨 **Building New Indexes**"
        )

        return result

    def _clear_embeddings(self) -> str:
        """Clear all embedding data."""
        try:
            self.clear_embedding_cache()

            result = "🗑️ **Embedding Cache Cleared**\n\n"
            result += "✅ All embedding indexes and cache have been cleared.\n\n"
            result += "💡 **What this means:**\n"
            result += "- Semantic search is no longer available\n"
            result += "- All cached embeddings have been removed\n"
            result += "- Vector indexes have been reset\n\n"
            result += "🔨 **To restore semantic search:**\n"
            result += "- Use the 'build' action to recreate indexes\n"
            result += "- This will re-download and process your HubSpot data\n"

            return result

        except Exception as e:
            return f"❌ **Error Clearing Embeddings**\n\n{str(e)}"

    def _format_build_summary(self, build_results: Dict[str, Dict[str, Any]]) -> str:
        """Format a summary of build results."""
        successful = 0
        failed = 0
        total_entities = 0

        for entity_type, result in build_results.items():
            if result.get("success", False):
                successful += 1
                total_entities += result.get("entities_indexed", 0)
            else:
                failed += 1

        summary = f"📈 **Build Summary**\n"
        summary += f"  • Successful: {successful}/{len(build_results)} entity types\n"
        summary += f"  • Failed: {failed}/{len(build_results)} entity types\n"
        summary += f"  • Total entities indexed: {total_entities}\n"

        return summary
