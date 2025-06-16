#!/usr/bin/env python3
"""HubSpot MCP Server.

This server provides Model Context Protocol (MCP) tools to interact with HubSpot CRM.
It allows accessing contacts, companies, and deals through conversational tools.
"""

import argparse
import asyncio
import logging
import os

import mcp.server.sse
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport

from .client import HubSpotClient
from .config.settings import settings
from .server import HubSpotHandlers
from .sse import (
    AuthenticationMiddleware,
    faiss_data_endpoint,
    handle_sse,
    health_check,
    readiness_check,
)

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
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
        default=settings.mode,
        help=f"Server communication mode (default: {settings.mode})",
    )

    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind SSE server (default: {settings.host})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port for SSE server (default: {settings.port})",
    )

    return parser.parse_args()


async def main():
    """Run the HubSpot MCP server main entry point."""
    args = parse_arguments()

    # Create server
    server = Server(settings.server_name)

    # Create HubSpot client
    hubspot_client = HubSpotClient(api_key=settings.hubspot_api_key)

    # Create and add handlers
    handlers = HubSpotHandlers(hubspot_client)

    # Enregistrement des handlers
    @server.list_tools()
    async def handle_list_tools():
        return await handlers.handle_list_tools()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        return await handlers.handle_call_tool(name, arguments)

    @server.list_prompts()
    async def handle_list_prompts():
        return await handlers.handle_list_prompts()

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict = None):
        if arguments is None:
            arguments = {}
        return await handlers.handle_get_prompt(name, arguments)

    @server.list_resources()
    async def handle_list_resources():
        return await handlers.handle_list_resources()

    @server.read_resource()
    async def handle_read_resource(uri: str):
        return await handlers.handle_read_resource(uri)

    # Initialize server options
    server_options = InitializationOptions(
        server_name=settings.server_name,
        server_version=settings.server_version,
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
        from starlette.routing import Mount, Route

        # Get authentication configuration from settings
        auth_config = settings.get_auth_config()

        if auth_config["enabled"]:
            logger.info(
                f"Authentication enabled with header: {auth_config['auth_header']}"
            )
        else:
            logger.warning("Authentication disabled - MCP_AUTH_KEY not set")

        # Create SSE transport
        sse = SseServerTransport("/messages/")

        # SSE endpoint handler
        async def handle_sse_local(request: Request):
            return await handle_sse(request, server, sse, server_options)

        # Create Starlette app with SSE routes
        # The following infrastructure objects (Starlette app and uvicorn config) are
        # instantiated only when running an actual SSE server. Mocking their internal
        # behaviour is not meaningful for unit-tests, therefore we exclude the precise
        # construction lines from the coverage metrics.  # pragma: no cover

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse_local),
                Route("/health", endpoint=health_check, methods=["GET"]),
                Route("/ready", endpoint=readiness_check, methods=["GET"]),
                Route("/faiss-data", endpoint=faiss_data_endpoint, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ]
        )  # pragma: no cover

        # Wrap with authentication middleware
        authenticated_app = AuthenticationMiddleware(
            app=app,
            auth_key=auth_config["auth_key"],
            header_name=auth_config["auth_header"],
        )

        # Run the server using uvicorn
        config = uvicorn.Config(
            app=authenticated_app,
            host=args.host,
            port=args.port,
            log_level=settings.log_level.lower(),
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
