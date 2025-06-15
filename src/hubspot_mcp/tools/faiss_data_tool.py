"""MCP tool for browsing HubSpot FAISS indexed data."""

from typing import Any, Dict, List

import mcp.types as types

from .enhanced_base import EnhancedBaseTool


class FaissDataTool(EnhancedBaseTool):
    """Tool for browsing HubSpot FAISS indexed data with pagination and filtering."""

    def get_tool_definition(self) -> types.Tool:
        """Return the FAISS data browsing tool definition."""
        return types.Tool(
            name="browse_hubspot_indexed_data",
            description="Browse and search HubSpot entities indexed in FAISS with pagination and filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["list", "stats", "search"],
                        "default": "list",
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Filter by entity type (optional)",
                        "enum": ["contacts", "companies", "deals", "engagements"],
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of entities to skip for pagination (default: 0)",
                        "default": 0,
                        "minimum": 0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entities to return (default: 20, max: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "search_text": {
                        "type": "string",
                        "description": "Search within indexed text content (case-insensitive)",
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Include full entity data in results (default: false for compact view)",
                        "default": False,
                    },
                },
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute FAISS data browsing action."""
        try:
            action = arguments.get("action", "list")

            if action == "stats":
                formatted_result = self._get_index_statistics()
            elif action == "list":
                formatted_result = self._list_indexed_entities(arguments)
            elif action == "search":
                formatted_result = self._search_indexed_entities(arguments)
            else:
                formatted_result = f"❌ **Invalid Action**\n\nUnknown action: {action}. Valid actions are: list, stats, search"

            return [types.TextContent(type="text", text=formatted_result)]

        except Exception as e:
            return self.handle_error(e)

    def _get_index_statistics(self) -> str:
        """Get comprehensive statistics about the FAISS index."""
        embedding_manager = self.get_embedding_manager()

        if not embedding_manager:
            return (
                "📊 **FAISS Index Statistics**\n\n"
                "❌ **Status**: No embedding manager available\n\n"
                "The FAISS embedding system is not initialized. "
                "Use the 'manage_hubspot_embeddings' tool to build an index first."
            )

        stats = embedding_manager.get_index_stats()

        if stats.get("status") != "ready":
            return (
                "📊 **FAISS Index Statistics**\n\n"
                f"❌ **Status**: {stats.get('status', 'unknown')}\n\n"
                "The FAISS index is not ready for querying. "
                "Use the 'manage_hubspot_embeddings' tool to build an index."
            )

        # Count entities by type
        entity_counts = {}
        total_entities = 0

        for metadata in embedding_manager.entity_metadata.values():
            entity_type = metadata.get("entity_type", "unknown")
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            total_entities += 1

        result = "📊 **FAISS Index Statistics**\n\n"
        result += f"✅ **Status**: {stats.get('status')}\n"
        result += f"📈 **Index Information:**\n"
        result += f"  • Total indexed entities: {total_entities}\n"
        result += f"  • Vector dimension: {stats.get('dimension', 'N/A')}\n"
        result += f"  • Index type: {stats.get('index_type', 'N/A')}\n"
        result += f"  • Model: {stats.get('model_name', 'N/A')}\n"
        result += f"  • Cache size: {stats.get('cache_size', 0)} entries\n\n"

        if entity_counts:
            result += "📂 **Entities by Type:**\n"
            for entity_type, count in sorted(entity_counts.items()):
                percentage = (count / total_entities * 100) if total_entities > 0 else 0
                result += f"  • {entity_type}: {count} ({percentage:.1f}%)\n"
        else:
            result += "📂 **Entities by Type:** None indexed\n"

        result += f"\n💡 **Usage Tips:**\n"
        result += f"• Use action='list' to browse indexed entities\n"
        result += f"• Use action='search' to find entities by text content\n"
        result += f"• Apply entity_type filter to narrow results\n"
        result += f"• Use offset/limit for pagination through large datasets\n"

        return result

    def _list_indexed_entities(self, arguments: Dict[str, Any]) -> str:
        """List indexed entities with pagination and filtering."""
        embedding_manager = self.get_embedding_manager()

        if not embedding_manager:
            return (
                "📋 **Indexed Entities**\n\n"
                "❌ **Error**: No embedding manager available\n\n"
                "The FAISS embedding system is not initialized."
            )

        stats = embedding_manager.get_index_stats()
        if stats.get("status") != "ready":
            return (
                "📋 **Indexed Entities**\n\n"
                "❌ **Error**: FAISS index not ready\n\n"
                f"Current status: {stats.get('status', 'unknown')}"
            )

        # Extract parameters
        entity_type_filter = arguments.get("entity_type")
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit", 20)
        include_content = arguments.get("include_content", False)

        # Collect and filter entities
        all_entities = []
        for idx, metadata in embedding_manager.entity_metadata.items():
            entity = metadata.get("entity", {})
            entity_type = metadata.get("entity_type", "unknown")
            text = metadata.get("text", "")

            # Apply entity type filter
            if entity_type_filter and entity_type != entity_type_filter:
                continue

            all_entities.append(
                {
                    "index": idx,
                    "entity_type": entity_type,
                    "entity_id": entity.get("id"),
                    "entity_data": entity,
                    "searchable_text": text,
                    "text_length": len(text),
                }
            )

        # Sort by index for consistent ordering
        all_entities.sort(key=lambda x: x["index"])

        # Apply pagination
        total_count = len(all_entities)
        paginated_entities = all_entities[offset : offset + limit]

        # Build result
        filter_desc = (
            f" (filtered by {entity_type_filter})" if entity_type_filter else ""
        )
        result = f"📋 **Indexed Entities{filter_desc}**\n\n"
        result += f"📊 **Pagination Info:**\n"
        result += f"  • Total entities: {total_count}\n"
        result += f"  • Showing: {offset + 1}-{min(offset + len(paginated_entities), total_count)} of {total_count}\n"
        result += f"  • Page size: {limit}\n\n"

        if not paginated_entities:
            if offset >= total_count and total_count > 0:
                result += "❌ **No entities found**: Offset exceeds total count\n"
                result += (
                    f"💡 **Tip**: Maximum valid offset is {max(0, total_count - 1)}\n"
                )
            else:
                result += (
                    "❌ **No entities found**: No indexed data matches your criteria\n"
                )
            return result

        result += "📄 **Entities:**\n"
        for i, entity in enumerate(paginated_entities, 1):
            entity_type = entity["entity_type"]
            entity_id = entity["entity_id"]
            text_length = entity["text_length"]

            # Get entity name/title for display
            entity_data = entity["entity_data"]
            entity_name = "Unknown"

            if entity_data:
                properties = entity_data.get("properties", {})
                # Try different name fields based on entity type
                if entity_type == "contacts":
                    entity_name = (
                        properties.get("firstname", "")
                        + " "
                        + properties.get("lastname", "")
                    )
                    entity_name = entity_name.strip() or properties.get("email", "")
                elif entity_type == "companies":
                    entity_name = properties.get("name", "")
                elif entity_type in ["deals", "engagements"]:
                    entity_name = properties.get("dealname", properties.get("name", ""))

                entity_name = entity_name.strip() or "Unnamed"

            result += f"\n**{offset + i}. {entity_name}**\n"
            result += f"  🏷️  Type: {entity_type}\n"
            result += f"  🆔 ID: {entity_id}\n"
            result += f"  📝 Text length: {text_length} chars\n"
            result += f"  📍 Index: {entity['index']}\n"

            if include_content:
                searchable_text = entity["searchable_text"]
                # Truncate long text for display
                if len(searchable_text) > 200:
                    searchable_text = searchable_text[:200] + "..."
                result += f"  📄 Content: {searchable_text}\n"

        # Add pagination navigation hints
        if total_count > offset + limit:
            next_offset = offset + limit
            result += (
                f"\n⏭️  **Next page**: Use offset={next_offset} to see more entities\n"
            )

        if offset > 0:
            prev_offset = max(0, offset - limit)
            result += f"⏮️  **Previous page**: Use offset={prev_offset} to go back\n"

        result += f"\n💡 **Tips:**\n"
        result += f"• Set include_content=true to see full searchable text\n"
        result += f"• Use entity_type filter to focus on specific types\n"
        result += f"• Try action='search' to find entities by text content\n"

        return result

    def _search_indexed_entities(self, arguments: Dict[str, Any]) -> str:
        """Search entities by text content."""
        embedding_manager = self.get_embedding_manager()

        if not embedding_manager:
            return (
                "🔍 **Search Indexed Entities**\n\n"
                "❌ **Error**: No embedding manager available\n\n"
                "The FAISS embedding system is not initialized."
            )

        stats = embedding_manager.get_index_stats()
        if stats.get("status") != "ready":
            return (
                "🔍 **Search Indexed Entities**\n\n"
                "❌ **Error**: FAISS index not ready\n\n"
                f"Current status: {stats.get('status', 'unknown')}"
            )

        search_text = arguments.get("search_text", "").strip()
        if not search_text:
            return (
                "🔍 **Search Indexed Entities**\n\n"
                "❌ **Error**: No search text provided\n\n"
                "Please provide search_text parameter with your query."
            )

        # Extract parameters
        entity_type_filter = arguments.get("entity_type")
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit", 20)
        include_content = arguments.get("include_content", False)

        # Search entities
        matching_entities = []
        search_text_lower = search_text.lower()

        for idx, metadata in embedding_manager.entity_metadata.items():
            entity = metadata.get("entity", {})
            entity_type = metadata.get("entity_type", "unknown")
            text = metadata.get("text", "")

            # Apply entity type filter
            if entity_type_filter and entity_type != entity_type_filter:
                continue

            # Check if search text is in the indexed text (case-insensitive)
            if search_text_lower in text.lower():
                matching_entities.append(
                    {
                        "index": idx,
                        "entity_type": entity_type,
                        "entity_id": entity.get("id"),
                        "entity_data": entity,
                        "searchable_text": text,
                        "text_length": len(text),
                        "match_position": text.lower().find(search_text_lower),
                    }
                )

        # Sort by relevance (how early the match appears in the text)
        matching_entities.sort(key=lambda x: x["match_position"])

        # Apply pagination
        total_matches = len(matching_entities)
        paginated_entities = matching_entities[offset : offset + limit]

        # Build result
        filter_desc = f" in {entity_type_filter}" if entity_type_filter else ""
        result = f"🔍 **Search Results for '{search_text}'{filter_desc}**\n\n"
        result += f"📊 **Search Info:**\n"
        result += f"  • Total matches: {total_matches}\n"
        result += f"  • Showing: {offset + 1}-{min(offset + len(paginated_entities), total_matches)} of {total_matches}\n"
        result += f"  • Page size: {limit}\n\n"

        if not paginated_entities:
            if offset >= total_matches and total_matches > 0:
                result += "❌ **No results**: Offset exceeds total matches\n"
                result += (
                    f"💡 **Tip**: Maximum valid offset is {max(0, total_matches - 1)}\n"
                )
            else:
                result += f"❌ **No matches found** for '{search_text}'\n"
                result += "💡 **Tips:**\n"
                result += "• Try different keywords or shorter phrases\n"
                result += "• Check spelling and try variations\n"
                result += "• Remove entity_type filter to search all types\n"
            return result

        result += "📄 **Matching Entities:**\n"
        for i, entity in enumerate(paginated_entities, 1):
            entity_type = entity["entity_type"]
            entity_id = entity["entity_id"]
            text = entity["searchable_text"]

            # Get entity name for display
            entity_data = entity["entity_data"]
            entity_name = "Unknown"

            if entity_data:
                properties = entity_data.get("properties", {})
                if entity_type == "contacts":
                    entity_name = (
                        properties.get("firstname", "")
                        + " "
                        + properties.get("lastname", "")
                    )
                    entity_name = entity_name.strip() or properties.get("email", "")
                elif entity_type == "companies":
                    entity_name = properties.get("name", "")
                elif entity_type in ["deals", "engagements"]:
                    entity_name = properties.get("dealname", properties.get("name", ""))

                entity_name = entity_name.strip() or "Unnamed"

            result += f"\n**{offset + i}. {entity_name}**\n"
            result += f"  🏷️  Type: {entity_type}\n"
            result += f"  🆔 ID: {entity_id}\n"
            result += f"  📍 Index: {entity['index']}\n"

            # Show context around the match
            match_pos = entity["match_position"]
            context_start = max(0, match_pos - 50)
            context_end = min(len(text), match_pos + len(search_text) + 50)
            context = text[context_start:context_end]

            # Add ellipsis if truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."

            result += f"  🎯 Match: {context}\n"

            if include_content:
                # Show more content if requested
                full_text = text if len(text) <= 300 else text[:300] + "..."
                result += f"  📄 Full content: {full_text}\n"

        # Add pagination navigation hints
        if total_matches > offset + limit:
            next_offset = offset + limit
            result += (
                f"\n⏭️  **Next page**: Use offset={next_offset} to see more results\n"
            )

        if offset > 0:
            prev_offset = max(0, offset - limit)
            result += f"⏮️  **Previous page**: Use offset={prev_offset} to go back\n"

        result += f"\n💡 **Tips:**\n"
        result += f"• Set include_content=true to see full searchable text\n"
        result += f"• Use entity_type filter to focus on specific types\n"
        result += f"• Try semantic_search_hubspot for AI-powered similarity search\n"

        return result
