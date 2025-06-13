"""Base class for HubSpot MCP tools."""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx
import mcp.types as types
from cachetools import TTLCache

from ..client import HubSpotClient

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all HubSpot tools.

    This abstract base class defines the interface that all HubSpot tools must implement.
    It provides common functionality for error handling, client management, and caching.
    """

    # Shared cache across all tool instances
    # TTL of 300 seconds (5 minutes) and max 1000 entries
    _cache: TTLCache = TTLCache(maxsize=1000, ttl=300)

    def __init__(self, client: HubSpotClient):
        """Initialize the tool with a HubSpot client.

        Args:
            client: The HubSpot client instance to use for API calls
        """
        self.client = client

    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition for MCP.

        Returns:
            types.Tool: The tool definition containing name, description, and input schema
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute the tool with provided arguments.

        Args:
            arguments: Dictionary containing the tool's input parameters

        Returns:
            List[types.TextContent]: List of text content items representing the tool's output
        """
        pass

    def _generate_cache_key(self, method_name: str, **kwargs) -> str:
        """Generate a cache key based on method name and arguments.

        Args:
            method_name: Name of the method being cached
            **kwargs: Arguments passed to the method

        Returns:
            str: A unique cache key for this method call
        """
        # Sort kwargs to ensure consistent key generation
        sorted_kwargs = dict(sorted(kwargs.items()))
        key_data = {
            "method": method_name,
            "args": sorted_kwargs,
            # Using SHA-256 to avoid weak-hash security warnings (Bandit B324)
            "api_key_hash": hashlib.sha256(
                str(self.client.api_key).encode()
            ).hexdigest()[:8],
        }
        key_string = json.dumps(key_data, sort_keys=True)
        # Final cache key derived from full payload using SHA-256
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def _cached_client_call(self, method_name: str, **kwargs) -> Any:
        """Execute a client method call with caching.

        Args:
            method_name: Name of the client method to call
            **kwargs: Arguments to pass to the client method

        Returns:
            Any: The result of the client method call (from cache or fresh)
        """
        cache_key = self._generate_cache_key(method_name, **kwargs)

        # Check if result is in cache
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {method_name} with key {cache_key[:8]}...")
            return self._cache[cache_key]

        # Execute the method and cache the result
        logger.debug(f"Cache miss for {method_name} with key {cache_key[:8]}...")
        method = getattr(self.client, method_name)
        result = await method(**kwargs)

        # Store in cache
        self._cache[cache_key] = result
        logger.debug(
            f"Cached result for {method_name} (cache size: {len(self._cache)})"
        )

        return result

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the entire cache.

        Useful for testing or when fresh data is required.
        """
        cls._cache.clear()
        logger.info("Tool cache cleared")

    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """Get information about the current cache state.

        Returns:
            Dict[str, Any]: Cache statistics including size, max size, and TTL
        """
        return {
            "size": len(cls._cache),
            "maxsize": cls._cache.maxsize,
            "ttl": cls._cache.ttl,
            "keys": list(cls._cache.keys())[:10],  # Show first 10 keys for debugging
        }

    def handle_error(self, error: Exception) -> List[types.TextContent]:
        """Handle errors in a unified way.

        Args:
            error: The exception that occurred during tool execution

        Returns:
            List[types.TextContent]: List containing a single text content item with the error message
        """
        if isinstance(error, httpx.HTTPStatusError):
            error_msg = f"HubSpot API Error ({error.response.status_code}): {error.response.text}"
        else:
            error_msg = f"Unexpected error: {str(error)}"

        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
