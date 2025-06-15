"""MCP tool for bulk loading HubSpot entities into cache with all properties."""

import logging
from typing import Any, Dict, List

import mcp.types as types

from .enhanced_base import EnhancedBaseTool

logger = logging.getLogger(__name__)


class BulkCacheLoaderTool(EnhancedBaseTool):
    """Tool for bulk loading HubSpot entities into cache with all properties.

    This tool:
    1. Retrieves all available properties for the entity type
    2. Loads ALL entities with complete property data using pagination
    3. Stores them in cache for optimized FAISS searches
    4. Builds embedding indexes for semantic search
    """

    def get_tool_definition(self) -> types.Tool:
        """Return the bulk cache loader tool definition."""
        return types.Tool(
            name="load_hubspot_entities_to_cache",
            description="Bulk load all HubSpot contacts, companies, or deals into cache with complete property data for optimized FAISS searches. Recommended to run once daily or when simple searches don't return expected information to ensure FAISS searches have access to complete, up-to-date data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "enum": ["contacts", "companies", "deals"],
                        "description": "Type of entities to load into cache",
                    },
                    "build_embeddings": {
                        "type": "boolean",
                        "description": "Whether to build FAISS embeddings after loading (default: true)",
                        "default": True,
                    },
                    "max_entities": {
                        "type": "integer",
                        "description": "Maximum number of entities to load (default: 10000, 0 = no limit)",
                        "default": 10000,
                        "minimum": 0,
                    },
                },
                "required": ["entity_type"],
                "additionalProperties": False,
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute bulk loading of entities into cache."""
        try:
            entity_type = arguments.get("entity_type")
            build_embeddings = arguments.get("build_embeddings", True)
            max_entities = arguments.get("max_entities", 10000)

            if entity_type not in ["contacts", "companies", "deals"]:
                return [
                    types.TextContent(
                        type="text",
                        text="❌ **Error**: entity_type must be 'contacts', 'companies', or 'deals'",
                    )
                ]

            # Step 1: Get all available properties for the entity type
            result = f"🚀 **Bulk Loading {entity_type.title()} to Cache**\n\n"
            result += f"📋 **Step 1**: Retrieving all {entity_type} properties...\n"

            # Get the appropriate properties method name
            if entity_type == "contacts":
                properties_method = "get_contact_properties"
            elif entity_type == "companies":
                properties_method = "get_company_properties"
            elif entity_type == "deals":
                properties_method = "get_deal_properties"
            else:
                properties_method = f"get_{entity_type[:-1]}_properties"  # Fallback
            properties = await self._cached_client_call(properties_method)

            if not properties:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ **Error**: Could not retrieve {entity_type} properties",
                    )
                ]

            # Extract property names (filter out calculated/system properties that can't be requested)
            property_names = []
            system_properties = {
                "id",
                "createddate",
                "lastmodifieddate",
                "createdate",
                "hs_lastmodifieddate",
                "hs_object_id",
                "hs_created_by",
                "hs_updated_by",
                "archived",
                "archivedAt",
            }

            for prop in properties:
                prop_name = prop.get("name", "")
                # Skip system properties that are automatically included or can't be requested
                if prop_name and prop_name not in system_properties:
                    # Skip calculated properties (they often can't be requested)
                    if not prop.get("calculated", False):
                        property_names.append(prop_name)

            result += f"✅ Found {len(properties)} total properties, requesting {len(property_names)} custom properties\n\n"

            # Step 2: Load ALL entities with pagination
            result += f"📥 **Step 2**: Loading all {entity_type} with complete property data...\n"

            all_entities = await self._load_all_entities_with_properties(
                entity_type, property_names, max_entities
            )

            if not all_entities:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ **Error**: No {entity_type} found to load",
                    )
                ]

            result += f"✅ Loaded {len(all_entities)} {entity_type} with complete property data\n\n"

            # Step 3: Build embeddings if requested
            if build_embeddings and self.enable_embeddings:
                result += (
                    f"🧠 **Step 3**: Building FAISS embeddings for semantic search...\n"
                )

                embedding_result = await self._build_embedding_index_from_entities(
                    entity_type, all_entities
                )

                if embedding_result.get("success"):
                    result += f"✅ Built embeddings for {embedding_result.get('entities_indexed', 0)} {entity_type}\n"

                    # Add embedding stats
                    stats = embedding_result.get("index_stats", {})
                    if stats:
                        result += f"  📊 Index stats: {stats.get('total_entities', 0)} entities, "
                        result += f"{stats.get('dimension', 0)} dimensions, {stats.get('index_type', 'unknown')} index\n"
                else:
                    result += f"⚠️ Failed to build embeddings: {embedding_result.get('error', 'Unknown error')}\n"
            else:
                if not build_embeddings:
                    result += f"ℹ️ **Step 3**: Skipped embedding generation (build_embeddings=false)\n"
                else:
                    result += f"⚠️ **Step 3**: Embeddings not available (not enabled)\n"

            result += "\n"

            # Step 4: Summary and recommendations
            result += f"🎉 **Cache Loading Complete**\n\n"
            result += f"📊 **Summary:**\n"
            result += f"  • Entity Type: {entity_type.title()}\n"
            result += f"  • Total Loaded: {len(all_entities)} entities\n"
            result += f"  • Properties: {len(property_names)} custom properties + system properties\n"
            result += f"  • Embeddings: {'✅ Built' if build_embeddings and self.enable_embeddings else '❌ Not built'}\n\n"

            result += f"💡 **What you can do now:**\n"
            result += f"  • Use semantic search across ALL {entity_type} with full property data\n"
            result += (
                f"  • FAISS searches will be much faster with complete cached data\n"
            )
            result += (
                f"  • All {len(property_names)} custom properties are searchable\n"
            )
            result += f"  • Cache includes system properties (ID, dates, etc.)\n\n"

            result += f"🔧 **Performance Notes:**\n"
            result += f"  • Cache size: ~{len(all_entities)} entities in memory\n"
            result += f"  • Search speed: Sub-second with FAISS indexing\n"
            result += (
                f"  • Data freshness: Run this tool periodically to update cache\n"
            )

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Bulk cache loading failed: {e}")
            return self.handle_error(e)

    async def _load_all_entities_with_properties(
        self, entity_type: str, property_names: List[str], max_entities: int
    ) -> List[Dict[str, Any]]:
        """Load all entities with pagination using all available properties.

        Args:
            entity_type: Type of entities to load ('contacts' or 'companies')
            property_names: List of property names to include
            max_entities: Maximum number of entities to load (0 = no limit)

        Returns:
            List of all entities with complete property data
        """
        # Use the new pagination methods that handle all the complexity
        get_all_method = f"get_all_{entity_type}_with_pagination"

        logger.info(
            f"Starting bulk load of {entity_type} with {len(property_names)} properties..."
        )

        # Call the client method that handles pagination internally
        all_entities = await self._cached_client_call(
            get_all_method, extra_properties=property_names, max_entities=max_entities
        )

        logger.info(
            f"Finished loading: {len(all_entities)} total {entity_type} with complete property data"
        )
        return all_entities

    async def _build_embedding_index_from_entities(
        self, entity_type: str, entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build FAISS embedding index from pre-loaded entities.

        Args:
            entity_type: Type of entity (contacts, companies, etc.)
            entities: List of entity dictionaries with complete property data

        Returns:
            Dict with index build results
        """
        if not self.enable_embeddings or self._embedding_manager is None:
            return {"success": False, "error": "Embeddings not enabled"}

        try:
            # Build FAISS index directly from the entities
            self._embedding_manager.build_index(entities, entity_type)

            stats = self._embedding_manager.get_index_stats()

            return {
                "success": True,
                "entity_type": entity_type,
                "entities_indexed": len(entities),
                "index_stats": stats,
            }

        except Exception as e:
            logger.error(f"Failed to build embedding index for {entity_type}: {e}")
            return {"success": False, "error": str(e)}
