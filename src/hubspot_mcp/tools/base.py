"""Classe de base pour les outils MCP HubSpot."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import httpx
import mcp.types as types

from ..client import HubSpotClient

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Classe de base pour tous les outils HubSpot."""
    
    def __init__(self, client: HubSpotClient):
        self.client = client
    
    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Retourne la définition de l'outil pour MCP."""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Exécute l'outil avec les arguments fournis."""
        pass
    
    def handle_error(self, error: Exception) -> List[types.TextContent]:
        """Gère les erreurs de manière unifiée."""
        if isinstance(error, httpx.HTTPStatusError):
            error_msg = f"Erreur API HubSpot ({error.response.status_code}): {error.response.text}"
        else:
            error_msg = f"Erreur inattendue: {str(error)}"
        
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)] 