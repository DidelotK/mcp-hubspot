#!/usr/bin/env python3
"""
HubSpot MCP Server

This server provides Model Context Protocol (MCP) tools to interact with HubSpot CRM.
It allows accessing contacts, companies, and deals through conversational tools.
"""

import argparse
import asyncio
import logging
import os
from pathlib import Path

import mcp.server.sse
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.server import MCPHandlers

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


async def main():
    """Main entry point for the HubSpot MCP server."""
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
        sse = SseServerTransport("/messages/")
        await server.run_sse(sse, server_options)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
