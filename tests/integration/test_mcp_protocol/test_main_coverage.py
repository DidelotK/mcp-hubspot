#!/usr/bin/env python3
"""
Simple tests to achieve 100% coverage on main.py
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the root directory to PYTHONPATH for main import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import main  # noqa: E402


def test_main_script_block_execution():
    """Script block: normal execution path (asyncio.run succeeds)."""
    import runpy

    with patch("asyncio.run") as mock_asyncio_run:
        mock_asyncio_run.return_value = None
        runpy.run_module("main", run_name="__main__")
        mock_asyncio_run.assert_called_once()


def test_main_script_block_keyboard_interrupt():
    """Script block: handles KeyboardInterrupt without raising."""
    import runpy

    with (
        patch("asyncio.run") as mock_asyncio_run,
        patch("logging.Logger.info") as mock_info,
    ):
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        # Should NOT raise
        runpy.run_module("main", run_name="__main__")
        mock_info.assert_any_call("Server stopped by user")


def test_main_script_block_general_exception():
    """Script block: unexpected exception is logged then re-raised."""
    import runpy

    test_exc = RuntimeError("boom")
    with patch("asyncio.run") as mock_run, patch("logging.Logger.error") as mock_error:
        mock_run.side_effect = test_exc
        with pytest.raises(RuntimeError):
            runpy.run_module("main", run_name="__main__")
        mock_error.assert_any_call("Server error: boom")


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

    # Mock stdio server
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()
    mock_stdio = AsyncMock()
    mock_stdio.__aenter__.return_value = (mock_read_stream, mock_write_stream)

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
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("mcp.server.stdio.stdio_server", return_value=mock_stdio),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
    ):
        # Configure arguments for stdio mode
        mock_args = MagicMock()
        mock_args.mode = "stdio"
        mock_parse_args.return_value = mock_args

        # Execute main to register handlers and run stdio mode
        await main.main()

        # Verify stdio mode logging was called
        mock_logger.info.assert_called_with("Starting server in stdio mode")

        # Test the registered handlers to cover those lines
        if registered_list_tools_handler:
            result = await registered_list_tools_handler()
            assert result == ["tool1"]
            mock_handlers.handle_list_tools.assert_called_once()

        if registered_call_tool_handler:
            result = await registered_call_tool_handler("test_tool", {"param": "value"})
            assert result == {"result": "test"}
            mock_handlers.handle_call_tool.assert_called_once_with(
                "test_tool", {"param": "value"}
            )


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
    mock_uvicorn_server.serve = AsyncMock()

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
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.SseServerTransport", return_value=mock_sse),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
        patch("starlette.applications.Starlette", return_value=mock_starlette_app),
        patch("uvicorn.Config") as mock_config_cls,
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):
        # Configure arguments for SSE mode
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "localhost"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Execute main to register handlers and run SSE mode
        await main.main()

        # Verify SSE mode logging was called
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on localhost:8080"
        )

        # Test the registered handlers to cover those lines
        if registered_list_tools_handler:
            result = await registered_list_tools_handler()
            assert result == ["tool1"]
            mock_handlers.handle_list_tools.assert_called_once()

        if registered_call_tool_handler:
            result = await registered_call_tool_handler("test_tool", {"param": "value"})
            assert result == {"result": "test"}
            mock_handlers.handle_call_tool.assert_called_once_with(
                "test_tool", {"param": "value"}
            )


@pytest.mark.asyncio
async def test_main_complete_sse_flow():
    """Test complete SSE flow including handle_sse function."""
    from unittest.mock import AsyncMock, MagicMock

    # Mock all dependencies
    mock_server = AsyncMock()
    mock_hubspot_client = MagicMock()
    mock_handlers = AsyncMock()
    mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1"])
    mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

    # Mock SSE components
    mock_sse = MagicMock()
    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()

    # Create a proper async context manager mock
    class MockSSEContext:
        async def __aenter__(self):
            return (mock_read_stream, mock_write_stream)

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    mock_sse.connect_sse.return_value = MockSSEContext()

    mock_starlette_app = MagicMock()
    mock_uvicorn_config = MagicMock()
    mock_uvicorn_server = AsyncMock()
    mock_uvicorn_server.serve = AsyncMock()

    # Mock InitializationOptions
    mock_init_options = MagicMock()

    # Capture the handle_sse function and routes
    captured_handle_sse = None
    captured_routes = None

    def capture_starlette_routes(routes):
        nonlocal captured_handle_sse, captured_routes
        captured_routes = routes
        for route in routes:
            if hasattr(route, "endpoint"):
                captured_handle_sse = route.endpoint
        return mock_starlette_app

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
        patch("main.Server", return_value=mock_server),
        patch("main.HubSpotClient", return_value=mock_hubspot_client),
        patch("main.MCPHandlers", return_value=mock_handlers),
        patch("main.SseServerTransport", return_value=mock_sse),
        patch("main.parse_arguments") as mock_parse_args,
        patch("main.InitializationOptions", return_value=mock_init_options),
        patch("main.logger") as mock_logger,
        patch("starlette.applications.Starlette", side_effect=capture_starlette_routes),
        patch("uvicorn.Config") as mock_config_cls,
        patch("uvicorn.Server", return_value=mock_uvicorn_server),
    ):
        # Configure arguments for SSE mode
        mock_args = MagicMock()
        mock_args.mode = "sse"
        mock_args.host = "localhost"
        mock_args.port = 8080
        mock_parse_args.return_value = mock_args

        # Execute main to register handlers and run SSE mode
        await main.main()

        # Verify SSE mode logging was called
        mock_logger.info.assert_called_with(
            "Starting server in SSE mode on localhost:8080"
        )

        # Verify Starlette app was created with routes (lines 142-146)
        assert captured_routes is not None
        assert len(captured_routes) == 2  # Route and Mount

        # Verify uvicorn Config and Server were called with right parameters
        mock_config_cls.assert_called_once()
        _cfg_args, cfg_kwargs = mock_config_cls.call_args
        assert cfg_kwargs["app"] is mock_starlette_app
        assert cfg_kwargs["host"] == "localhost"
        assert cfg_kwargs["port"] == 8080
        assert cfg_kwargs["log_level"] == "info"

        # Ensure the server serve coroutine is awaited once
        mock_uvicorn_server.serve.assert_awaited_once()

        # Test the captured handle_sse function to cover line 123
        if captured_handle_sse:
            mock_request = MagicMock()
            mock_request.scope = {}
            mock_request.receive = AsyncMock()
            mock_request._send = AsyncMock()

            await captured_handle_sse(mock_request)

            # Verify SSE connection was established
            mock_sse.connect_sse.assert_called_once_with(
                mock_request.scope,
                mock_request.receive,
                mock_request._send,
            )


# end of tests
