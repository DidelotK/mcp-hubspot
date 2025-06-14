"""MCP tool for semantic search across HubSpot entities."""

from typing import Any, Dict, List, Union

import mcp.types as types

from ..formatters import HubSpotFormatter
from .enhanced_base import EnhancedBaseTool


class SemanticSearchTool(EnhancedBaseTool):
    """Tool for performing semantic search across HubSpot entities."""

    def get_tool_definition(self) -> types.Tool:
        """Return the semantic search tool definition."""
        return types.Tool(
            name="semantic_search_hubspot",
            description="Perform AI-powered semantic search across HubSpot contacts, companies, deals, and engagements using natural language queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'technology companies in Paris', 'software engineers', 'enterprise deals over 50k')",
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["contacts", "companies", "deals", "engagements"],
                        },
                        "description": "Types of entities to search (default: all types)",
                        "default": ["contacts", "companies", "deals", "engagements"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return per entity type (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0.0 to 1.0, default: 0.5)",
                        "default": 0.5,
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "search_mode": {
                        "type": "string",
                        "enum": ["semantic", "hybrid", "auto"],
                        "description": "Search mode: semantic (embeddings only), hybrid (embeddings + API), or auto (best available)",
                        "default": "auto",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute semantic search across HubSpot entities."""
        try:
            query = arguments.get("query", "")
            entity_types = arguments.get(
                "entity_types", ["contacts", "companies", "deals", "engagements"]
            )
            limit = arguments.get("limit", 5)
            threshold = arguments.get("threshold", 0.5)
            search_mode = arguments.get("search_mode", "auto")

            if not query.strip():
                return [
                    types.TextContent(
                        type="text", text="❌ **Error**: Search query cannot be empty."
                    )
                ]

            # Check if embeddings are available
            embedding_stats = self.get_embedding_stats()

            if not embedding_stats.get("enabled", False):
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Embeddings Not Available**\n\n"
                        "Semantic search requires embeddings to be enabled. "
                        "Please build the embedding index first using the embedding management tool.",
                    )
                ]

            # Perform search based on mode
            all_results: Dict[str, Union[List[Dict[str, Any]], Dict[str, str]]] = {}
            total_found = 0

            for entity_type in entity_types:
                try:
                    if search_mode == "semantic":
                        # Pure semantic search
                        results = await self.semantic_search(query, limit, threshold)
                        # Filter by entity type
                        filtered_results = [
                            (entity, score)
                            for entity, score in results
                            if self._get_entity_type_from_result(entity) == entity_type
                        ]
                        entities = [entity for entity, _ in filtered_results]

                    elif search_mode == "hybrid":
                        # Hybrid search (semantic + API)
                        entities = await self.hybrid_search(
                            query,
                            entity_type,
                            limit,
                            semantic_weight=0.7,
                            threshold=threshold,
                        )

                    else:  # auto mode
                        # Try hybrid first, fallback to semantic
                        entities = await self.hybrid_search(
                            query,
                            entity_type,
                            limit,
                            semantic_weight=0.6,
                            threshold=threshold,
                        )

                        # If no results from hybrid, try pure semantic
                        if not entities:
                            semantic_results = await self.semantic_search(
                                query, limit, threshold
                            )
                            filtered_results = [
                                (entity, score)
                                for entity, score in semantic_results
                                if self._get_entity_type_from_result(entity)
                                == entity_type
                            ]
                            entities = [entity for entity, _ in filtered_results]

                    if entities:
                        all_results[entity_type] = entities
                        total_found += len(entities)

                except Exception as e:
                    # Log error but continue with other entity types
                    all_results[entity_type] = {"error": str(e)}

            # Format results
            if total_found == 0:
                return [
                    types.TextContent(
                        type="text",
                        text=f"🔍 **Semantic Search Results**\n\n"
                        f'**Query:** "{query}"\n'
                        f"**Search Mode:** {search_mode}\n"
                        f"**Threshold:** {threshold}\n\n"
                        f"❌ No matching entities found. Try:\n"
                        f"- Lowering the similarity threshold\n"
                        f"- Using different keywords\n"
                        f"- Building or rebuilding the embedding index",
                    )
                ]

            # Format successful results
            formatted_text = self._format_search_results(
                all_results, query, search_mode, threshold, total_found
            )

            return [types.TextContent(type="text", text=formatted_text)]

        except Exception as e:
            return self.handle_error(e)

    def _get_entity_type_from_result(self, entity: Dict[str, Any]) -> str:
        """Determine entity type from the entity data.

        Args:
            entity: HubSpot entity

        Returns:
            str: Entity type (contacts, companies, deals, engagements)
        """
        # This is a heuristic approach - could be improved with metadata
        props = entity.get("properties", {})

        if "firstname" in props or "lastname" in props or "email" in props:
            return "contacts"
        elif "dealname" in props or "amount" in props or "dealstage" in props:
            return "deals"
        elif "name" in props and "domain" in props:
            return "companies"
        elif "hs_engagement_type" in props:
            return "engagements"
        else:
            # Fallback based on typical properties
            if any(key in props for key in ["company", "jobtitle", "phone"]):
                return "contacts"
            elif any(key in props for key in ["industry", "city", "country"]):
                return "companies"
            else:
                return "unknown"

    def _format_search_results(
        self,
        results: Dict[str, Union[List[Dict[str, Any]], Dict[str, str]]],
        query: str,
        search_mode: str,
        threshold: float,
        total_found: int,
    ) -> str:
        """Format search results for display.

        Args:
            results: Dictionary of results by entity type
            query: Original search query
            search_mode: Search mode used
            threshold: Similarity threshold
            total_found: Total number of results found

        Returns:
            str: Formatted results text
        """
        text = f"🔍 **Semantic Search Results**\n\n"
        text += f'**Query:** "{query}"\n'
        text += f"**Search Mode:** {search_mode}\n"
        text += f"**Similarity Threshold:** {threshold}\n"
        text += f"**Total Results:** {total_found}\n\n"

        # Format results for each entity type
        for entity_type, entities in results.items():
            if isinstance(entities, dict) and "error" in entities:
                text += f"❌ **{entity_type.title()}**: Error - {entities['error']}\n\n"
                continue

            if not entities:
                continue

            text += f"## 📊 {entity_type.title()} ({len(entities)} found)\n\n"

            # Use existing formatters
            if entity_type == "contacts":
                formatted = HubSpotFormatter.format_contacts(entities)
            elif entity_type == "companies":
                formatted = HubSpotFormatter.format_companies(entities)
            elif entity_type == "deals":
                formatted = HubSpotFormatter.format_deals(entities)
            elif entity_type == "engagements":
                formatted = HubSpotFormatter.format_engagements(entities)
            else:
                formatted = f"Found {len(entities)} {entity_type}"

            # Extract just the entities part (remove header)
            lines = formatted.split("\n")
            entity_lines = []
            skip_header = True

            for line in lines:
                if skip_header and line.startswith("**") and not line.startswith("  "):
                    skip_header = False
                    entity_lines.append(line)
                elif not skip_header:
                    entity_lines.append(line)

            text += "\n".join(entity_lines) + "\n\n"

        text += "---\n\n"
        text += "💡 **Tips for Better Results:**\n"
        text += "- Use natural language descriptions\n"
        text += "- Be specific about what you're looking for\n"
        text += "- Try different similarity thresholds\n"
        text += "- Use hybrid mode for the best balance of accuracy and coverage"

        return text
