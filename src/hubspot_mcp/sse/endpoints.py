"""SSE server endpoints for HubSpot MCP server."""

import logging
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from ..client import HubSpotClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


async def handle_sse(request: Request, server, sse, server_options):
    """SSE endpoint handler."""
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server_options)


async def health_check(request: Request):
    """Health check endpoint for Kubernetes."""
    try:
        # Basic health check - verify HubSpot client can be created
        if not settings.hubspot_api_key:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "HUBSPOT_API_KEY not configured",
                },
            )

        # Return healthy status
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "server": settings.server_name,
                "version": settings.server_version,
                "mode": "sse",
                "auth_enabled": settings.is_authentication_enabled(),
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


async def readiness_check(request: Request):
    """Readiness check endpoint for Kubernetes."""
    try:
        # More thorough readiness check
        if not settings.hubspot_api_key:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "error": "HUBSPOT_API_KEY not configured",
                },
            )

        # Try to create HubSpot client (test for readiness)
        HubSpotClient(api_key=settings.hubspot_api_key)

        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "server": settings.server_name,
                "version": settings.server_version,
                "mode": "sse",
                "auth_enabled": settings.is_authentication_enabled(),
            },
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "error": str(e)}
        )


async def faiss_data_endpoint(request: Request):
    """Retrieve indexed FAISS data in JSON format.

    Available only in SSE mode. Returns all indexed entities with their metadata.
    """
    try:
        # Import here to avoid circular imports
        from ..tools.enhanced_base import EnhancedBaseTool

        # Get the shared embedding manager
        embedding_manager = EnhancedBaseTool.get_embedding_manager()

        if embedding_manager is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unavailable",
                    "error": "Embedding system not initialized",
                    "message": "No FAISS index has been built yet. Use the embedding management tool to build an index first.",
                },
            )

        # Get index statistics
        stats = embedding_manager.get_index_stats()

        if stats.get("status") != "ready":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "error": "FAISS index not ready",
                    "stats": stats,
                    "message": "The FAISS index is not ready. Build an index using the embedding management tool.",
                },
            )

        # Extract indexed entities data
        indexed_entities = []
        entity_counts = {}

        for idx, metadata in embedding_manager.entity_metadata.items():
            entity = metadata.get("entity", {})
            entity_type = metadata.get("entity_type", "unknown")
            text = metadata.get("text", "")

            # Count entities by type
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

            # Add to indexed entities
            indexed_entities.append(
                {
                    "index": idx,
                    "entity_type": entity_type,
                    "entity_id": entity.get("id"),
                    "entity_data": entity,
                    "searchable_text": text,
                    "text_length": len(text),
                }
            )

        # Prepare response data
        response_data = {
            "status": "success",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "server_info": {
                "server": settings.server_name,
                "version": settings.server_version,
                "mode": "sse",
            },
            "faiss_stats": {
                "index_status": stats.get("status"),
                "total_entities": stats.get("total_entities", 0),
                "vector_dimension": stats.get("dimension"),
                "index_type": stats.get("index_type"),
                "model_name": stats.get("model_name"),
                "cache_size": stats.get("cache_size", 0),
            },
            "entity_summary": {
                "total_indexed": len(indexed_entities),
                "types_count": entity_counts,
                "available_types": list(entity_counts.keys()),
            },
            "indexed_entities": indexed_entities,
        }

        logger.info(
            f"FAISS data endpoint accessed - returning {len(indexed_entities)} indexed entities"
        )

        return JSONResponse(
            status_code=200,
            content=response_data,
        )

    except Exception as e:
        logger.error(f"FAISS data endpoint failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "message": "Internal server error while retrieving FAISS data",
            },
        )


async def force_reindex_endpoint(request: Request):
    """Force complete reindexing of all HubSpot entities.

    This endpoint:
    1. Resets the cache completely
    2. Loads all contacts, companies, and deals with their properties
    3. Builds FAISS indexes for semantic search
    4. Returns detailed progress and results
    """
    try:
        logger.info("Starting force reindex process...")

        # Verify HubSpot API key is configured
        if not settings.hubspot_api_key:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "error": "HUBSPOT_API_KEY not configured",
                    "message": "Cannot perform reindexing without HubSpot API access",
                },
            )

        # Import required tools here to avoid circular imports
        from ..tools.bulk_cache_loader import BulkCacheLoaderTool
        from ..tools.embedding_management_tool import EmbeddingManagementTool
        from ..tools.enhanced_base import EnhancedBaseTool

        # Initialize HubSpot client
        hubspot_client = HubSpotClient(api_key=settings.hubspot_api_key)

        # Initialize tools
        bulk_loader = BulkCacheLoaderTool(hubspot_client)
        embedding_tool = EmbeddingManagementTool(hubspot_client)

        results = {
            "status": "success",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "server_info": {
                "server": settings.server_name,
                "version": settings.server_version,
                "mode": "sse",
            },
            "process_log": [],
            "entity_results": {},
            "final_stats": {},
        }

        # Step 1: Clear existing cache and embeddings
        results["process_log"].append("🗑️ Clearing existing cache and embeddings...")
        logger.info("Clearing cache and embeddings")

        # Clear both caches
        bulk_loader.clear_cache()
        embedding_tool.clear_embedding_cache()

        results["process_log"].append("✅ Cache and embeddings cleared successfully")

        # Step 2: Load entities for each type
        entity_types = ["contacts", "companies", "deals"]
        total_entities_loaded = 0

        for entity_type in entity_types:
            results["process_log"].append(
                f"📥 Loading {entity_type} with all properties..."
            )
            logger.info(f"Starting bulk load for {entity_type}")

            try:
                # Use bulk loader to load entities with embeddings
                load_result = await bulk_loader.execute(
                    {
                        "entity_type": entity_type,
                        "build_embeddings": True,
                        "max_entities": 10000,  # Load up to 10k entities per type
                    }
                )

                # Parse result text to extract useful info
                result_text = load_result[0].text if load_result else "No result"

                # Extract entity count from result text
                entity_count = 0
                if "Total Loaded:" in result_text:
                    for line in result_text.split("\n"):
                        if "Total Loaded:" in line:
                            entity_count = int(
                                line.split("Total Loaded: ")[1].split(" ")[0]
                            )
                            break

                total_entities_loaded += entity_count

                results["entity_results"][entity_type] = {
                    "status": "success",
                    "entities_loaded": entity_count,
                    "embeddings_built": "✅ Built" in result_text,
                }

                results["process_log"].append(
                    f"✅ {entity_type}: Loaded {entity_count} entities with embeddings"
                )
                logger.info(f"Successfully loaded {entity_count} {entity_type}")

            except Exception as e:
                error_msg = str(e)
                results["entity_results"][entity_type] = {
                    "status": "error",
                    "error": error_msg,
                }
                results["process_log"].append(f"❌ {entity_type}: Failed - {error_msg}")
                logger.error(f"Failed to load {entity_type}: {e}")

        # Step 3: Get final embedding statistics
        results["process_log"].append("📊 Gathering final statistics...")

        try:
            embedding_manager = EnhancedBaseTool.get_embedding_manager()
            if embedding_manager:
                final_stats = embedding_manager.get_index_stats()
                results["final_stats"] = final_stats

                results["process_log"].append(
                    f"✅ Final index stats: {final_stats.get('total_entities', 0)} entities indexed"
                )
            else:
                results["process_log"].append(
                    "⚠️ Could not retrieve embedding statistics"
                )

        except Exception as e:
            results["process_log"].append(f"⚠️ Error getting final stats: {str(e)}")
            logger.warning(f"Could not get final stats: {e}")

        # Step 4: Summary
        successful_types = len(
            [
                r
                for r in results["entity_results"].values()
                if r.get("status") == "success"
            ]
        )
        total_types = len(entity_types)

        results["summary"] = {
            "total_entity_types_processed": total_types,
            "successful_entity_types": successful_types,
            "failed_entity_types": total_types - successful_types,
            "total_entities_loaded": total_entities_loaded,
            "embeddings_ready": results["final_stats"].get("status") == "ready",
            "semantic_search_available": total_entities_loaded > 0
            and results["final_stats"].get("status") == "ready",
        }

        results["process_log"].append("🎉 Force reindex process completed!")
        results["process_log"].append(
            f"📈 Summary: {successful_types}/{total_types} entity types successful, {total_entities_loaded} total entities loaded"
        )

        if results["summary"]["semantic_search_available"]:
            results["process_log"].append("✅ Semantic search is now fully available!")
        else:
            results["process_log"].append(
                "⚠️ Semantic search may not be fully available - check individual entity results"
            )

        logger.info(
            f"Force reindex completed: {total_entities_loaded} entities loaded, {successful_types}/{total_types} types successful"
        )

        return JSONResponse(status_code=200, content=results)

    except Exception as e:
        logger.error(f"Force reindex endpoint failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "message": "Internal server error during force reindexing",
                "process_log": [f"❌ Fatal error: {str(e)}"],
            },
        )
