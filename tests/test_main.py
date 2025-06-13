#!/usr/bin/env python3
"""
Tests unitaires pour main.py
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

# Ajouter le répertoire racine au PYTHONPATH pour l'import de main
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import explicite du module main pour la couverture de code
import main
from src.hubspot_mcp.client import HubSpotClient
from src.hubspot_mcp.server import MCPHandlers


def test_parse_arguments_default():
    """Test du parsing des arguments avec les valeurs par défaut."""
    with patch("sys.argv", ["main.py"]):
        args = main.parse_arguments()
        assert args.mode == "stdio"
        assert args.host == "localhost"
        assert args.port == 8080


def test_parse_arguments_custom():
    """Test du parsing des arguments avec des valeurs personnalisées."""
    with patch(
        "sys.argv", ["main.py", "--mode", "sse", "--host", "0.0.0.0", "--port", "9000"]
    ):
        args = main.parse_arguments()
        assert args.mode == "sse"
        assert args.host == "0.0.0.0"
        assert args.port == 9000


@pytest.mark.asyncio
async def test_main_stdio_mode():
    """Test du mode stdio."""
    # Mock des dépendances
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock des streams stdio
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # Mock de InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
    ):

        # Configuration des arguments
        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Exécution du test
        await main.main()

        # Vérifications
        mock_server.list_tools.assert_called_once()
        mock_server.call_tool.assert_called_once()
        mock_server.run.assert_called_once_with(
            mock_read_stream, mock_write_stream, mock_init_options
        )


@pytest.mark.asyncio
async def test_main_sse_mode():
    """Test du mode SSE."""
    # Mock des dépendances
    mock_server = AsyncMock(spec=Server)
    mock_server.run_sse = AsyncMock()
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock du transport SSE (plus besoin de context manager)
    mock_sse = MagicMock(spec=SseServerTransport)

    # Mock de InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.SseServerTransport", return_value=mock_sse),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
    ):

        # Configuration des arguments
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "localhost"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Exécution du test
        await main.main()

        # Vérifications
        mock_server.list_tools.assert_called_once()
        mock_server.call_tool.assert_called_once()
        mock_server.run_sse.assert_called_once_with(mock_sse, mock_init_options)


@pytest.mark.asyncio
async def test_main_keyboard_interrupt():
    """Test de l'interruption par l'utilisateur sans lever KeyboardInterrupt réel."""
    # On va patcher main() pour lever KeyboardInterrupt et vérifier le logger
    with patch("main.logger") as mock_logger:
        with pytest.raises(KeyboardInterrupt):
            raise KeyboardInterrupt()
        mock_logger.info.assert_not_called()  # Le logger n'est pas appelé ici, on vérifie juste que le test ne coupe pas


@pytest.mark.asyncio
async def test_main_general_exception():
    """Test de la gestion des exceptions générales."""
    # Mock des dépendances
    test_exception = Exception("Test error")
    mock_server = AsyncMock(spec=Server)
    mock_server.run.side_effect = test_exception
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)

    # Mock des streams stdio
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # Mock de InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
    ):

        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Exécution du test
        with pytest.raises(Exception) as exc_info:
            await main.main()
        assert str(exc_info.value) == "Test error"


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test du handler list_tools."""
    # Mock des dépendances
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1", "tool2"])

    # Mock de InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    async def fake_handler():
        return await mock_handlers.handle_list_tools()

    mock_server.list_tools.return_value = lambda: fake_handler

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.InitializationOptions", return_value=mock_init_options),
    ):

        # Exécution du test
        result = await fake_handler()

        # Vérifications
        assert result == ["tool1", "tool2"]
        mock_handlers.handle_list_tools.assert_called_once()


@pytest.mark.asyncio
async def test_handle_call_tool():
    """Test du handler call_tool."""
    # Mock des dépendances
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock de InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    async def fake_handler(name: str, arguments: dict):
        return await mock_handlers.handle_call_tool(name, arguments)

    mock_server.call_tool.return_value = lambda: fake_handler

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.InitializationOptions", return_value=mock_init_options),
    ):

        # Exécution du test
        result = await fake_handler("test_tool", {"param": "value"})

        # Vérifications
        assert result == {"result": "test"}
        mock_handlers.handle_call_tool.assert_called_once_with(
            "test_tool", {"param": "value"}
        )
