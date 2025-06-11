#!/usr/bin/env python3
"""
Point d'entrée principal du serveur MCP HubSpot.
"""

import argparse
import asyncio
import logging

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.server.sse

from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.config import Settings
from src.hubspot_mcp.server import MCPHandlers

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hubspot-mcp-server")


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Serveur MCP HubSpot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Mode stdio (défaut)
  python main.py --mode stdio
  
  # Mode SSE
  python main.py --mode sse --host 127.0.0.1 --port 8080
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse"],
        default="stdio",
        help="Mode de transport du serveur (défaut: stdio)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse d'écoute pour le mode SSE (défaut: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port d'écoute pour le mode SSE (défaut: 8080)"
    )
    
    return parser.parse_args()


async def main():
    """Point d'entrée principal du serveur."""
    # Parse des arguments
    args = parse_arguments()
    
    # Chargement de la configuration
    settings = Settings()
    
    # Validation de la configuration
    if not settings.validate():
        missing = settings.get_missing_config()
        logger.error(f"Configuration manquante: {', '.join(missing)}")
        return
    
    # Initialisation du client HubSpot
    hubspot_client = HubSpotClient(settings.hubspot_api_key)
    logger.info("Client HubSpot initialisé")
    
    # Initialisation des handlers
    handlers = MCPHandlers(hubspot_client)
    
    # Initialisation du serveur MCP
    server = Server(settings.server_name)
    
    # Enregistrement des handlers
    @server.list_tools()
    async def handle_list_tools():
        return await handlers.handle_list_tools()
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        return await handlers.handle_call_tool(name, arguments)
    
    # Options d'initialisation
    init_options = InitializationOptions(
        server_name=settings.server_name,
        server_version=settings.server_version,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    
    # Démarrage du serveur selon le mode choisi
    if args.mode == "stdio":
        logger.info("Démarrage du serveur en mode stdio")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                init_options
            )
    
    elif args.mode == "sse":
        logger.info(f"Démarrage du serveur en mode SSE sur {args.host}:{args.port}")
        async with mcp.server.sse.sse_server(
            host=args.host,
            port=args.port
        ) as sse_server:
            await server.run_sse(
                sse_server,
                init_options
            )


if __name__ == "__main__":
    asyncio.run(main()) 