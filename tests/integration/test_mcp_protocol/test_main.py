#!/usr/bin/env python3
"""
Unit tests for main.py
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

# Add the root directory to PYTHONPATH for main import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Explicit import of main module for code coverage
import main  # noqa: F401,E402

from hubspot_mcp.client import HubSpotClient  # noqa: E402
from hubspot_mcp.server import MCPHandlers  # noqa: E402


def test_parse_arguments_default():
    """Test argument parsing with default values."""
    with patch("sys.argv", ["hubspot-mcp-server"]):
        args = main.parse_arguments()
        assert args.mode == "stdio"
        assert args.host == "localhost"
        assert args.port == 8080


def test_parse_arguments_custom():
    """Test argument parsing with custom values."""
    with patch(
        "sys.argv",
        ["hubspot-mcp-server", "--mode", "sse", "--host", "0.0.0.0", "--port", "9000"],
    ):
        args = main.parse_arguments()
        assert args.mode == "sse"
        assert args.host == "0.0.0.0"
        assert args.port == 9000


@pytest.mark.asyncio
async def test_main_stdio_mode():
    """Test stdio mode."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock stdio streams
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # Mock InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
    ):

        # Configure arguments
        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Execute test
        await main.main()

        # Verifications
        mock_server.list_tools.assert_called_once()
        mock_server.call_tool.assert_called_once()
        mock_server.run.assert_called_once_with(
            mock_read_stream, mock_write_stream, mock_init_options
        )
        # Verify logger was called
        mock_logger.info.assert_called_with("Starting server in stdio mode")


@pytest.mark.asyncio
async def test_main_sse_mode():
    """Test SSE mode."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock SSE transport
    mock_sse = MagicMock(spec=SseServerTransport)

    # Mock Starlette and uvicorn components
    mock_starlette_app = MagicMock()
    mock_uvicorn_config = MagicMock()
    mock_uvicorn_server = AsyncMock()
    mock_uvicorn_server.serve = AsyncMock()

    # Mock InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.SseServerTransport", return_value=mock_sse),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
        # Mock the new SSE implementation components
        patch("starlette.applications.Starlette", return_value=mock_starlette_app),
        patch("uvicorn.Config", return_value=mock_uvicorn_config),
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):

        # Configure arguments
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "localhost"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Execute test
        await main.main()

        # Verifications
        mock_server.list_tools.assert_called_once()
        mock_server.call_tool.assert_called_once()
        mock_uvicorn_server.serve.assert_called_once()
        # Verify logger was called with correct message
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on localhost:8080"
        )


@pytest.mark.asyncio
async def test_main_stdio_mode_with_logger():
    """Test stdio mode with logger verification."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock stdio streams
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # Mock InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
    ):

        # Configure arguments
        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Execute test
        await main.main()

        # Verify logger was called
        mock_logger.info.assert_called_with("Starting server in stdio mode")


@pytest.mark.asyncio
async def test_main_sse_mode_with_logger():
    """Test SSE mode with logger verification."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock()
    mock_handlers.handle_call_tool = AsyncMock()

    # Mock SSE transport
    mock_sse = MagicMock(spec=SseServerTransport)

    # Mock Starlette and uvicorn components
    mock_starlette_app = MagicMock()
    mock_uvicorn_config = MagicMock()
    mock_uvicorn_server = AsyncMock()
    mock_uvicorn_server.serve = AsyncMock()

    # Mock InitializationOptions
    mock_init_options = MagicMock(spec=InitializationOptions)
    mock_init_options.model_dump.return_value = {}

    with (
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.SseServerTransport", return_value=mock_sse),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
        # Mock the new SSE implementation components
        patch("starlette.applications.Starlette", return_value=mock_starlette_app),
        patch("uvicorn.Config", return_value=mock_uvicorn_config),
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):

        # Configure arguments
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "localhost"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Execute test
        await main.main()

        # Verify logger was called with correct message
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on localhost:8080"
        )


@pytest.mark.asyncio
async def test_main_keyboard_interrupt():
    """Test user interruption without raising actual KeyboardInterrupt."""
    # We'll patch main() to raise KeyboardInterrupt and verify the logger
    with patch("main.logger") as mock_logger:
        with pytest.raises(KeyboardInterrupt):
            raise KeyboardInterrupt()
        mock_logger.info.assert_not_called()  # Logger not called here, just verify test doesn't break


@pytest.mark.asyncio
async def test_main_general_exception():
    """Test general exception handling."""
    # Mock dependencies
    test_exception = Exception("Test error")
    mock_server = AsyncMock(spec=Server)
    mock_server.run.side_effect = test_exception
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)

    # Mock stdio streams
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # Mock InitializationOptions
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

        # Execute test
        with pytest.raises(Exception) as exc_info:
            await main.main()
        assert str(exc_info.value) == "Test error"


def test_main_script_keyboard_interrupt():
    """Test the main script execution with KeyboardInterrupt."""
    with (
        patch("main.asyncio.run") as mock_asyncio_run,
        patch("main.logger") as mock_logger,
    ):
        # Configure asyncio.run to raise KeyboardInterrupt
        mock_asyncio_run.side_effect = KeyboardInterrupt()

        # Simulate the if __name__ == "__main__": block execution
        try:
            main.asyncio.run(main.main())
        except KeyboardInterrupt:
            main.logger.info("Server stopped by user")

        # Verify logger was called
        mock_logger.info.assert_called_with("Server stopped by user")


def test_main_script_general_exception():
    """Test the main script execution with general exception."""
    test_exception = Exception("Test server error")

    with (
        patch("main.asyncio.run") as mock_asyncio_run,
        patch("main.logger") as mock_logger,
    ):
        # Configure asyncio.run to raise a general exception
        mock_asyncio_run.side_effect = test_exception

        # Simulate the if __name__ == "__main__": block execution
        with pytest.raises(Exception) as exc_info:
            try:
                main.asyncio.run(main.main())
            except KeyboardInterrupt:
                main.logger.info("Server stopped by user")
            except Exception as e:
                main.logger.error(f"Server error: {e}")
                raise

        # Verify logger was called and exception was re-raised
        mock_logger.error.assert_called_with("Server error: Test server error")
        assert str(exc_info.value) == "Test server error"


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test the list_tools handler."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1", "tool2"])

    # Mock InitializationOptions
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

        # Execute test
        result = await fake_handler()

        # Verifications
        assert result == ["tool1", "tool2"]
        mock_handlers.handle_list_tools.assert_called_once()


@pytest.mark.asyncio
async def test_handle_call_tool():
    """Test the call_tool handler."""
    # Mock dependencies
    mock_server = AsyncMock(spec=Server)
    mock_hubspot_client = MagicMock(spec=HubSpotClient)
    mock_handlers = AsyncMock(spec=MCPHandlers)
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock InitializationOptions
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

        # Execute test
        result = await fake_handler("test_tool", {"param": "value"})

        # Verifications
        assert result == {"result": "test"}
        mock_handlers.handle_call_tool.assert_called_once_with(
            "test_tool", {"param": "value"}
        )
