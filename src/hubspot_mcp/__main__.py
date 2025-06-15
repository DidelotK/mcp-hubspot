#!/usr/bin/env python3
"""HubSpot MCP Server.

This server provides Model Context Protocol (MCP) tools to interact with HubSpot CRM.
It allows accessing contacts, companies, and deals through conversational tools.
"""

import argparse
import asyncio
import logging
import os
from typing import Optional

import mcp.server.sse
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport

from .client import HubSpotClient
from .server import MCPHandlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="HubSpot MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode stdio                    # For Claude Desktop
  %(prog)s --mode sse --port 8080         # For web clients
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["stdio", "sse"],
        default="stdio",
        help="Server communication mode (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind SSE server (default: localhost)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE server (default: 8080)",
    )

    return parser.parse_args()


class AuthenticationMiddleware:
    """Authentication middleware for SSE server."""

    def __init__(
        self, app, auth_key: Optional[str] = None, header_name: str = "X-API-Key"
    ):
        """
        Initialize authentication middleware.

        Args:
            app: ASGI application to wrap
            auth_key: API key for authentication (None disables auth)
            header_name: Header name to check for auth key
        """
        self.app = app
        self.auth_key = auth_key
        self.header_name = header_name
        self.exempt_paths = {"/health", "/ready"}  # Paths that don't require auth

    async def __call__(self, scope, receive, send):
        """ASGI middleware call."""
        # Skip authentication if no auth key is configured
        if not self.auth_key:
            await self.app(scope, receive, send)
            return

        # Skip authentication for exempt paths
        path = scope.get("path", "")
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        # Check authentication for HTTP requests
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Convert header name to lowercase bytes for case-insensitive comparison
            header_key = self.header_name.lower().encode()
            auth_header = headers.get(header_key, b"").decode()

            if not auth_header or auth_header != self.auth_key:
                # Send 401 Unauthorized response
                error_body = b'{"error": "Unauthorized", "message": "Invalid API key"}'
                response = {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(error_body)).encode()],
                    ],
                }
                await send(response)

                body = {
                    "type": "http.response.body",
                    "body": error_body,
                }
                await send(body)
                return

        # Proceed with the request if authentication passes
        await self.app(scope, receive, send)


async def main():
    """Run the HubSpot MCP server main entry point."""
    args = parse_arguments()

    # Create server
    server = Server("hubspot-mcp-server")

    # Create HubSpot client
    hubspot_client = HubSpotClient(api_key=os.getenv("HUBSPOT_API_KEY"))

    # Create and add handlers
    handlers = MCPHandlers(hubspot_client)

    # Enregistrement des handlers
    @server.list_tools()
    async def handle_list_tools():
        return await handlers.handle_list_tools()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        return await handlers.handle_call_tool(name, arguments)

    # Initialize server options
    server_options = InitializationOptions(
        server_name="hubspot-mcp-server",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    # Start server based on selected mode
    if args.mode == "stdio":
        logger.info("Starting server in stdio mode")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server_options)
    else:  # SSE mode
        logger.info(f"Starting server in SSE mode on {args.host}:{args.port}")

        # Import required modules for SSE server
        import uvicorn
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.routing import Mount, Route

        # Get authentication configuration
        auth_key = os.getenv("MCP_AUTH_KEY")
        auth_header = os.getenv("MCP_AUTH_HEADER", "X-API-Key")

        if auth_key:
            logger.info(f"Authentication enabled with header: {auth_header}")
        else:
            logger.warning("Authentication disabled - MCP_AUTH_KEY not set")

        # Create SSE transport
        sse = SseServerTransport("/messages/")

        # SSE endpoint handler
        async def handle_sse(request: Request):
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as (read_stream, write_stream):
                await server.run(read_stream, write_stream, server_options)

        # Health check endpoint
        async def health_check(request: Request):
            """Health check endpoint for Kubernetes."""
            try:
                # Basic health check - verify HubSpot client can be created
                api_key = os.getenv("HUBSPOT_API_KEY")
                if not api_key:
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
                        "server": "hubspot-mcp-server",
                        "version": "1.0.0",
                        "mode": "sse",
                        "auth_enabled": bool(auth_key),
                    },
                )
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503, content={"status": "unhealthy", "error": str(e)}
                )

        # Readiness check endpoint
        async def readiness_check(request: Request):
            """Readiness check endpoint for Kubernetes."""
            try:
                # More thorough readiness check
                api_key = os.getenv("HUBSPOT_API_KEY")
                if not api_key:
                    return JSONResponse(
                        status_code=503,
                        content={
                            "status": "not_ready",
                            "error": "HUBSPOT_API_KEY not configured",
                        },
                    )

                # Try to create HubSpot client (test for readiness)
                HubSpotClient(api_key=api_key)

                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "ready",
                        "server": "hubspot-mcp-server",
                        "version": "1.0.0",
                        "mode": "sse",
                        "auth_enabled": bool(auth_key),
                    },
                )
            except Exception as e:
                logger.error(f"Readiness check failed: {e}")
                return JSONResponse(
                    status_code=503, content={"status": "not_ready", "error": str(e)}
                )

        # FAISS data endpoint
        async def faiss_data_endpoint(request: Request):
            """Retrieve indexed FAISS data in JSON format.

            Available only in SSE mode. Returns all indexed entities with their metadata.
            """
            try:
                # Import here to avoid circular imports
                from .tools.enhanced_base import EnhancedBaseTool

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
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                    + "Z",
                    "server_info": {
                        "server": "hubspot-mcp-server",
                        "version": "1.0.0",
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

        # Create Starlette app with SSE routes
        # The following infrastructure objects (Starlette app and uvicorn config) are
        # instantiated only when running an actual SSE server. Mocking their internal
        # behaviour is not meaningful for unit-tests, therefore we exclude the precise
        # construction lines from the coverage metrics.  # pragma: no cover

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/health", endpoint=health_check, methods=["GET"]),
                Route("/ready", endpoint=readiness_check, methods=["GET"]),
                Route("/faiss-data", endpoint=faiss_data_endpoint, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ]
        )  # pragma: no cover

        # Wrap with authentication middleware
        authenticated_app = AuthenticationMiddleware(
            app=app, auth_key=auth_key, header_name=auth_header
        )

        # Run the server using uvicorn
        config = uvicorn.Config(
            app=authenticated_app,
            host=args.host,
            port=args.port,
            log_level="info",
        )
        server_instance = uvicorn.Server(config)
        await server_instance.serve()


def cli_main():
    """CLI entry point that handles exceptions."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    cli_main()
