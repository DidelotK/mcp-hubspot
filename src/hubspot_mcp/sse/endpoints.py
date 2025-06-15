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
