#!/usr/bin/env python3
"""
Simple tests to achieve 100% coverage on main.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add src to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import hubspot_mcp.__main__ as main  # noqa: E402


def test_main_script_block_execution():
    """Script block: normal execution path (asyncio.run succeeds)."""
    with patch("hubspot_mcp.__main__.main") as mock_main:
        mock_main.return_value = None

        # Test cli_main directly instead of using runpy
        main.cli_main()

        mock_main.assert_called_once()


def test_main_script_block_keyboard_interrupt():
    """Script block: handles KeyboardInterrupt without raising."""
    with (
        patch("hubspot_mcp.__main__.main") as mock_main,
        patch("hubspot_mcp.__main__.logger") as mock_logger,
    ):
        mock_main.side_effect = KeyboardInterrupt()

        # Should NOT raise - cli_main catches KeyboardInterrupt
        main.cli_main()

        mock_main.assert_called_once()
        mock_logger.info.assert_called_with("Server stopped by user")


def test_main_script_block_general_exception():
    """Script block: unexpected exception is logged then re-raised."""
    test_exc = RuntimeError("boom")
    with (
        patch("hubspot_mcp.__main__.main") as mock_main,
        patch("hubspot_mcp.__main__.logger") as mock_logger,
    ):
        mock_main.side_effect = test_exc

        with pytest.raises(RuntimeError):
            main.cli_main()

        mock_main.assert_called_once()
        mock_logger.error.assert_called_with("Server error: boom")


def test_parse_arguments_default():
    """Test parse_arguments function with default values."""
    with patch("sys.argv", ["hubspot-mcp-server"]):
        args = main.parse_arguments()
        assert args.mode == "stdio"
        assert args.host == "localhost"
        assert args.port == 8080


def test_parse_arguments_stdio_mode():
    """Test parse_arguments function with stdio mode."""
    with patch("sys.argv", ["hubspot-mcp-server", "--mode", "stdio"]):
        args = main.parse_arguments()
        assert args.mode == "stdio"
        assert args.host == "localhost"
        assert args.port == 8080


def test_parse_arguments_sse_mode():
    """Test parse_arguments function with SSE mode and custom host/port."""
    with patch(
        "sys.argv",
        ["hubspot-mcp-server", "--mode", "sse", "--host", "0.0.0.0", "--port", "9000"],
    ):
        args = main.parse_arguments()
        assert args.mode == "sse"
        assert args.host == "0.0.0.0"
        assert args.port == 9000


def test_parse_arguments_help():
    """Test parse_arguments function help functionality."""
    with patch("sys.argv", ["hubspot-mcp-server", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main.parse_arguments()
        assert exc_info.value.code == 0


@pytest.mark.asyncio
async def test_main_stdio_mode_execution():
    """Test main() function execution in stdio mode to cover handlers and logging."""
    from unittest.mock import AsyncMock, MagicMock

    # Mock all dependencies
    mock_server = AsyncMock()
    mock_hubspot_client = MagicMock()
    mock_handlers = AsyncMock()
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1"])
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock stdio server with proper return values
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__ = AsyncMock(
        return_value=(mock_read_stream, mock_write_stream)
    )
    mock_stdio.__aexit__ = AsyncMock(return_value=None)

    # Mock InitializationOptions
    mock_init_options = MagicMock()

    # Mock server.run to avoid creating unawaited coroutines
    mock_server.run = AsyncMock(return_value=None)

    # Capture registered handlers
    registered_list_tools_handler = None
    registered_call_tool_handler = None

    def capture_list_tools():
        def decorator(func):
            nonlocal registered_list_tools_handler
            registered_list_tools_handler = func
            return func

        return decorator

    def capture_call_tool():
        def decorator(func):
            nonlocal registered_call_tool_handler
            registered_call_tool_handler = func
            return func

        return decorator

    mock_server.list_tools = capture_list_tools
    mock_server.call_tool = capture_call_tool

    with (
        patch("hubspot_mcp.__main__.Server", return_value=mock_server),
        patch("hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client),
        patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
        patch(
            "hubspot_mcp.__main__.InitializationOptions", return_value=mock_init_options
        ),
        patch("hubspot_mcp.__main__.logger") as mock_logger,
    ):
        # Configure parse_arguments to return stdio mode
        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Call main()
        await main.main()

        # Verify handlers were registered
        assert registered_list_tools_handler is not None
        assert registered_call_tool_handler is not None

        # Test the registered handlers
        list_result = await registered_list_tools_handler()
        call_result = await registered_call_tool_handler(
            "test_tool", {"param": "value"}
        )

        assert list_result == ["tool1"]
        assert call_result == {"result": "test"}

        # Verify logger was called
        mock_logger.info.assert_called_with("Starting server in stdio mode")


@pytest.mark.asyncio
async def test_main_sse_mode_execution():
    """Test main() function execution in SSE mode to cover SSE logging."""
    from unittest.mock import AsyncMock, MagicMock

    # Mock all dependencies
    mock_server = AsyncMock()
    mock_hubspot_client = MagicMock()
    mock_handlers = AsyncMock()
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1"])
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock SSE components
    mock_sse = MagicMock()
    mock_starlette_app = MagicMock()
    mock_uvicorn_config = MagicMock()
    mock_uvicorn_server = AsyncMock()
    mock_uvicorn_server.serve = AsyncMock(return_value=None)

    # Mock InitializationOptions
    mock_init_options = MagicMock()

    # Capture registered handlers
    registered_list_tools_handler = None
    registered_call_tool_handler = None

    def capture_list_tools():
        def decorator(func):
            nonlocal registered_list_tools_handler
            registered_list_tools_handler = func
            return func

        return decorator

    def capture_call_tool():
        def decorator(func):
            nonlocal registered_call_tool_handler
            registered_call_tool_handler = func
            return func

        return decorator

    mock_server.list_tools = capture_list_tools
    mock_server.call_tool = capture_call_tool

    with (
        patch("hubspot_mcp.__main__.Server", return_value=mock_server),
        patch("hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client),
        patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
        patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
        patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
        patch(
            "hubspot_mcp.__main__.InitializationOptions", return_value=mock_init_options
        ),
        patch("hubspot_mcp.__main__.logger") as mock_logger,
        patch("starlette.applications.Starlette", return_value=mock_starlette_app),
        patch("uvicorn.Config") as mock_config_cls,
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):
        # Configure parse_arguments to return SSE mode
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "0.0.0.0"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Configure uvicorn.Config return value
        mock_config_cls.return_value = mock_uvicorn_config

        # Call main()
        await main.main()

        # Verify handlers were registered
        assert registered_list_tools_handler is not None
        assert registered_call_tool_handler is not None

        # Test the registered handlers
        list_result = await registered_list_tools_handler()
        call_result = await registered_call_tool_handler(
            "test_tool", {"param": "value"}
        )

        assert list_result == ["tool1"]
        assert call_result == {"result": "test"}

        # Verify logger was called
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on 0.0.0.0:8080"
        )


@pytest.mark.asyncio
async def test_main_complete_sse_flow():
    """Test complete SSE flow including Starlette app creation."""
    from unittest.mock import AsyncMock, MagicMock

    # Mock all dependencies
    mock_server = AsyncMock()
    mock_hubspot_client = MagicMock()
    mock_handlers = AsyncMock()
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1"])
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock SSE components
    mock_sse = MagicMock()
    mock_starlette_app = MagicMock()
    mock_uvicorn_config = MagicMock()
    mock_uvicorn_server = AsyncMock()
    mock_uvicorn_server.serve = AsyncMock(return_value=None)

    # Mock InitializationOptions
    mock_init_options = MagicMock()

    # Capture registered handlers
    registered_list_tools_handler = None
    registered_call_tool_handler = None

    def capture_list_tools():
        def decorator(func):
            nonlocal registered_list_tools_handler
            registered_list_tools_handler = func
            return func

        return decorator

    def capture_call_tool():
        def decorator(func):
            nonlocal registered_call_tool_handler
            registered_call_tool_handler = func
            return func

        return decorator

    mock_server.list_tools = capture_list_tools
    mock_server.call_tool = capture_call_tool

    with (
        patch("hubspot_mcp.__main__.Server", return_value=mock_server),
        patch("hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client),
        patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
        patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
        patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
        patch(
            "hubspot_mcp.__main__.InitializationOptions", return_value=mock_init_options
        ),
        patch("hubspot_mcp.__main__.logger") as mock_logger,
        patch(
            "starlette.applications.Starlette", return_value=mock_starlette_app
        ) as mock_starlette,
        patch("uvicorn.Config") as mock_config_cls,
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):
        # Configure parse_arguments to return SSE mode
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "127.0.0.1"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Configure uvicorn.Config return value
        mock_config_cls.return_value = mock_uvicorn_config

        # Call main()
        await main.main()

        # Verify handlers were registered
        assert registered_list_tools_handler is not None
        assert registered_call_tool_handler is not None

        # Test the registered handlers
        list_result = await registered_list_tools_handler()
        call_result = await registered_call_tool_handler(
            "test_tool", {"param": "value"}
        )

        assert list_result == ["tool1"]
        assert call_result == {"result": "test"}

        # Verify Starlette was called to create the app
        mock_starlette.assert_called_once()
        # Verify the app was called with routes
        call_args = mock_starlette.call_args
        assert "routes" in call_args.kwargs
        routes = call_args.kwargs["routes"]
        assert len(routes) == 4  # /sse, /health, /ready routes and /messages/ mount

        # Verify logger was called
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on 127.0.0.1:8080"
        )


# end of tests
