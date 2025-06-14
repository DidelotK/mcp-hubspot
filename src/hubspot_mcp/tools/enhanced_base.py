"""Enhanced base class for HubSpot MCP tools with embedding capabilities."""

import logging
from typing import Any, Dict, List, Optional, Tuple

import mcp.types as types

from ..embeddings import EmbeddingManager
from .base import BaseTool

logger = logging.getLogger(__name__)


class EnhancedBaseTool(BaseTool):
    """Enhanced base class for HubSpot tools with embedding capabilities.

    This class extends BaseTool to provide:
    - All existing cachetools functionality
    - FAISS-based semantic search
    - Embedding generation and caching
    - Hybrid search capabilities
    """

    # Shared embedding manager across all tool instances
    _embedding_manager: Optional[EmbeddingManager] = None

    def __init__(self, client, enable_embeddings: bool = True):
        """Initialize the enhanced tool.

        Args:
            client: The HubSpot client instance
            enable_embeddings: Whether to enable embedding functionality
        """
        super().__init__(client)
        self.enable_embeddings = enable_embeddings

        if enable_embeddings and self._embedding_manager is None:
            EnhancedBaseTool._embedding_manager = EmbeddingManager()

    @classmethod
    def get_embedding_manager(cls) -> Optional[EmbeddingManager]:
        """Get the shared embedding manager instance.

        Returns:
            EmbeddingManager instance or None if not initialized
        """
        return EnhancedBaseTool._embedding_manager

    async def build_embedding_index(
        self, entity_type: str, limit: int = 1000
    ) -> Dict[str, Any]:
        """Build or rebuild the embedding index for an entity type.

        Args:
            entity_type: Type of entity (contacts, companies, deals, etc.)
            limit: Maximum number of entities to index

        Returns:
            Dict with index build results
        """
        if not self.enable_embeddings or self._embedding_manager is None:
            return {"success": False, "error": "Embeddings not enabled"}

        try:
            # Fetch entities using existing cache system
            method_name = f"get_{entity_type}"
            entities = await self._cached_client_call(method_name, limit=limit)

            if not entities:
                return {"success": False, "error": f"No {entity_type} found to index"}

            # Build FAISS index
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

    async def semantic_search(
        self, query: str, k: int = 5, threshold: float = 0.5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Perform semantic search across indexed entities.

        Args:
            query: Search query text
            k: Number of results to return
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of tuples containing (entity, similarity_score)
        """
        if not self.enable_embeddings or self._embedding_manager is None:
            return []

        try:
            return self._embedding_manager.search_similar(query, k, threshold)
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def hybrid_search(
        self,
        query: str,
        entity_type: str,
        k: int = 5,
        semantic_weight: float = 0.7,
        threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining API filters and semantic similarity.

        Args:
            query: Search query
            entity_type: Type of entity to search
            k: Number of results to return
            semantic_weight: Weight for semantic results (0.0 to 1.0)
            threshold: Minimum similarity threshold

        Returns:
            List of ranked entities combining both methods
        """
        if not self.enable_embeddings or self._embedding_manager is None:
            # Fallback to regular API search
            return await self._fallback_search(query, entity_type, k)

        try:
            # 1. Semantic search
            semantic_results = await self.semantic_search(query, k * 2, threshold)

            # 2. API-based search (using existing cached client call)
            search_method = f"search_{entity_type}"
            if hasattr(self.client, search_method):
                api_results = await self._cached_client_call(
                    search_method, limit=k * 2, filters={"search": query}
                )
            else:
                api_results = []

            # 3. Combine and rank results
            combined_results = self._combine_search_results(
                semantic_results, api_results, semantic_weight, k
            )

            return combined_results

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return await self._fallback_search(query, entity_type, k)

    def _combine_search_results(
        self,
        semantic_results: List[Tuple[Dict[str, Any], float]],
        api_results: List[Dict[str, Any]],
        semantic_weight: float,
        k: int,
    ) -> List[Dict[str, Any]]:
        """Combine semantic and API search results with weighted scoring.

        Args:
            semantic_results: Results from semantic search
            api_results: Results from API search
            semantic_weight: Weight for semantic scores
            k: Number of final results

        Returns:
            List of combined and ranked results
        """
        # Create a mapping of entity IDs to combined scores
        entity_scores: Dict[str, Dict[str, Any]] = {}

        # Process semantic results
        for entity, similarity in semantic_results:
            entity_id = entity.get("id")
            if entity_id:
                entity_scores[entity_id] = {
                    "entity": entity,
                    "semantic_score": similarity * semantic_weight,
                    "api_score": 0.0,
                }

        # Process API results (give them a default relevance score)
        api_weight = 1.0 - semantic_weight
        for i, entity in enumerate(api_results):
            entity_id = entity.get("id")
            if entity_id:
                # API results are ordered by relevance, so higher index = lower score
                api_relevance = max(0.1, 1.0 - (i / len(api_results)))

                if entity_id in entity_scores:
                    # Entity found in both - combine scores
                    entity_scores[entity_id]["api_score"] = api_relevance * api_weight
                else:
                    # New entity from API
                    entity_scores[entity_id] = {
                        "entity": entity,
                        "semantic_score": 0.0,
                        "api_score": api_relevance * api_weight,
                    }

        # Calculate final scores and sort
        final_results = []
        for entity_data in entity_scores.values():
            total_score = entity_data["semantic_score"] + entity_data["api_score"]
            final_results.append(
                {
                    "entity": entity_data["entity"],
                    "total_score": total_score,
                    "semantic_score": entity_data["semantic_score"],
                    "api_score": entity_data["api_score"],
                }
            )

        # Sort by total score and return top k entities
        final_results.sort(key=lambda x: x["total_score"], reverse=True)
        return [result["entity"] for result in final_results[:k]]

    async def _fallback_search(
        self, query: str, entity_type: str, k: int
    ) -> List[Dict[str, Any]]:
        """Fallback search using only API when embeddings are not available.

        Args:
            query: Search query
            entity_type: Type of entity to search
            k: Number of results

        Returns:
            List of entities from API search
        """
        try:
            search_method = f"search_{entity_type}"
            if hasattr(self.client, search_method):
                return await self._cached_client_call(
                    search_method, limit=k, filters={"search": query}
                )
            else:
                # If no search method available, get all and filter
                get_method = f"get_{entity_type}"
                all_entities = await self._cached_client_call(get_method, limit=100)

                # Simple text matching fallback
                filtered = []
                query_lower = query.lower()
                for entity in all_entities:
                    entity_text = str(entity.get("properties", {})).lower()
                    if query_lower in entity_text:
                        filtered.append(entity)
                        if len(filtered) >= k:
                            break

                return filtered
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding system.

        Returns:
            Dict containing embedding system statistics
        """
        if not self.enable_embeddings or self._embedding_manager is None:
            return {"enabled": False, "status": "disabled"}

        stats = self._embedding_manager.get_index_stats()
        stats["enabled"] = True
        return stats

    @classmethod
    def clear_embedding_cache(cls) -> None:
        """Clear the embedding cache and index."""
        if EnhancedBaseTool._embedding_manager:
            EnhancedBaseTool._embedding_manager.clear_cache()
            logger.info("Embedding cache cleared")

    def handle_error(self, error: Exception) -> List[types.TextContent]:
        """Enhanced error handling that includes embedding context.

        Args:
            error: The exception that occurred

        Returns:
            List of TextContent with error information
        """
        # Use parent error handling
        base_result = super().handle_error(error)

        # Add embedding context if relevant
        if "embedding" in str(error).lower() or "faiss" in str(error).lower():
            embedding_info = "\n\n💡 **Embedding Tip**: If you're experiencing embedding-related issues, try:\n"
            embedding_info += "- Rebuilding the embedding index\n"
            embedding_info += "- Clearing the embedding cache\n"
            embedding_info += (
                "- Checking if the sentence transformer model is properly loaded"
            )

            base_result[0] = types.TextContent(
                type="text", text=base_result[0].text + embedding_info
            )

        return base_result
