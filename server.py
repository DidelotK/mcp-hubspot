#!/usr/bin/env python3
"""
Serveur MCP HubSpot pour lister les contacts et entreprises avec filtrage.
"""

import argparse
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.server.sse
import mcp.types as types
from pydantic import AnyUrl

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hubspot-mcp-server")

class HubSpotClient:
    """Client pour interagir avec l'API HubSpot."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_contacts(self, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        """Récupère la liste des contacts avec filtrage optionnel."""
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        params = {
            "limit": limit,
            "properties": "firstname,lastname,email,company,phone,createdate,lastmodifieddate"
        }
        
        # Ajouter des filtres si fournis
        if filters:
            # HubSpot utilise des filtres complexes, on peut ajouter une recherche simple
            if "search" in filters:
                params["search"] = filters["search"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
    
    async def get_companies(self, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        """Récupère la liste des entreprises avec filtrage optionnel."""
        url = f"{self.base_url}/crm/v3/objects/companies"
        
        params = {
            "limit": limit,
            "properties": "name,domain,city,state,country,industry,createdate,lastmodifieddate"
        }
        
        # Ajouter des filtres si fournis
        if filters:
            if "search" in filters:
                params["search"] = filters["search"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

# Initialisation du serveur MCP
server = Server("hubspot-mcp-server")

# Client HubSpot global
hubspot_client: Optional[HubSpotClient] = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Liste les outils disponibles."""
    return [
        types.Tool(
            name="list_hubspot_contacts",
            description="Liste les contacts HubSpot avec possibilité de filtrage",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum de contacts à retourner (défaut: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtres optionnels pour la recherche",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Terme de recherche pour filtrer les contacts"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_hubspot_companies",
            description="Liste les entreprises HubSpot avec possibilité de filtrage",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum d'entreprises à retourner (défaut: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtres optionnels pour la recherche",
                        "properties": {
                            "search": {
                                "type": "string",
                                "description": "Terme de recherche pour filtrer les entreprises"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Gère les appels d'outils."""
    if hubspot_client is None:
        return [types.TextContent(
            type="text",
            text="Erreur: Client HubSpot non initialisé. Vérifiez votre clé API."
        )]
    
    try:
        if name == "list_hubspot_contacts":
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})
            
            contacts = await hubspot_client.get_contacts(limit=limit, filters=filters)
            
            # Formatage des résultats
            result = f"📋 **Contacts HubSpot** ({len(contacts)} trouvés)\n\n"
            
            for contact in contacts:
                props = contact.get("properties", {})
                result += f"**{props.get('firstname', '')} {props.get('lastname', '')}**\n"
                result += f"  📧 Email: {props.get('email', 'N/A')}\n"
                result += f"  🏢 Entreprise: {props.get('company', 'N/A')}\n"
                result += f"  📞 Téléphone: {props.get('phone', 'N/A')}\n"
                result += f"  📅 Créé: {props.get('createdate', 'N/A')}\n"
                result += f"  🆔 ID: {contact.get('id')}\n\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "list_hubspot_companies":
            limit = arguments.get("limit", 100)
            filters = arguments.get("filters", {})
            
            companies = await hubspot_client.get_companies(limit=limit, filters=filters)
            
            # Formatage des résultats
            result = f"🏢 **Entreprises HubSpot** ({len(companies)} trouvées)\n\n"
            
            for company in companies:
                props = company.get("properties", {})
                result += f"**{props.get('name', 'Nom non spécifié')}**\n"
                result += f"  🌐 Domaine: {props.get('domain', 'N/A')}\n"
                result += f"  📍 Localisation: {props.get('city', '')}, {props.get('state', '')}, {props.get('country', '')}\n"
                result += f"  🏭 Secteur: {props.get('industry', 'N/A')}\n"
                result += f"  📅 Créée: {props.get('createdate', 'N/A')}\n"
                result += f"  🆔 ID: {company.get('id')}\n\n"
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Outil inconnu: {name}"
            )]
    
    except httpx.HTTPStatusError as e:
        error_msg = f"Erreur API HubSpot ({e.response.status_code}): {e.response.text}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    
    except Exception as e:
        error_msg = f"Erreur inattendue: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]

def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Serveur MCP HubSpot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Mode stdio (défaut)
  python server.py --mode stdio
  
  # Mode SSE
  python server.py --mode sse --host 127.0.0.1 --port 8080
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
    global hubspot_client
    
    # Parse des arguments
    args = parse_arguments()
    
    # Récupération de la clé API depuis les variables d'environnement
    api_key = os.getenv("HUBSPOT_API_KEY")
    if not api_key:
        logger.error("HUBSPOT_API_KEY non trouvée dans les variables d'environnement")
        return
    
    # Initialisation du client HubSpot
    hubspot_client = HubSpotClient(api_key)
    logger.info("Client HubSpot initialisé")
    
    # Options d'initialisation
    init_options = InitializationOptions(
        server_name="hubspot-mcp-server",
        server_version="1.0.0",
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