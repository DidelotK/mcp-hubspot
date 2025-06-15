"""Tests for the FAISS data endpoint in SSE mode."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import hubspot_mcp.__main__ as main


class TestFaissDataEndpoint:
    """Test cases for the FAISS data endpoint."""

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_success(self):
        """Test successful FAISS data endpoint response."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_handlers.handle_list_tools = AsyncMock(return_value=["tool1"])
        mock_handlers.handle_call_tool = AsyncMock(return_value={"result": "test"})

        # Mock SSE components
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Mock embedding manager with data
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "ready",
            "total_entities": 2,
            "dimension": 384,
            "index_type": "flat",
            "model_name": "all-MiniLM-L6-v2",
            "cache_size": 5,
        }
        mock_embedding_manager.entity_metadata = {
            0: {
                "entity": {
                    "id": "contact1",
                    "properties": {"firstname": "John", "lastname": "Doe"},
                },
                "entity_type": "contacts",
                "text": "John Doe john@example.com Software Engineer",
            },
            1: {
                "entity": {
                    "id": "company1",
                    "properties": {"name": "TechCorp", "domain": "techcorp.com"},
                },
                "entity_type": "companies",
                "text": "TechCorp techcorp.com Technology",
            },
        }

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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

        # Set up environment
        test_env = {
            "HUBSPOT_API_KEY": "test_key",
            "MCP_AUTH_KEY": "test_auth",
        }

        with (
            patch("hubspot_mcp.__main__.Server", return_value=mock_server),
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, test_env),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ),
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):

            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            # Make sure uvicorn.Server.serve doesn't run indefinitely
            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 200
            response_body = json.loads(response.body.decode("utf-8"))

            # Verify response structure
            assert response_body["status"] == "success"
            assert "timestamp" in response_body
            assert response_body["timestamp"].endswith("Z")  # Check format
            assert response_body["server_info"]["server"] == "hubspot-mcp-server"
            assert response_body["server_info"]["mode"] == "sse"

            # Verify FAISS stats
            faiss_stats = response_body["faiss_stats"]
            assert faiss_stats["index_status"] == "ready"
            assert faiss_stats["total_entities"] == 2
            assert faiss_stats["vector_dimension"] == 384
            assert faiss_stats["index_type"] == "flat"
            assert faiss_stats["model_name"] == "all-MiniLM-L6-v2"

            # Verify entity summary
            entity_summary = response_body["entity_summary"]
            assert entity_summary["total_indexed"] == 2
            assert entity_summary["types_count"] == {"contacts": 1, "companies": 1}
            assert set(entity_summary["available_types"]) == {"contacts", "companies"}

            # Verify indexed entities
            indexed_entities = response_body["indexed_entities"]
            assert len(indexed_entities) == 2

            # Check first entity (contact)
            contact_entity = indexed_entities[0]
            assert contact_entity["index"] == 0
            assert contact_entity["entity_type"] == "contacts"
            assert contact_entity["entity_id"] == "contact1"
            assert contact_entity["entity_data"]["id"] == "contact1"
            assert (
                contact_entity["searchable_text"]
                == "John Doe john@example.com Software Engineer"
            )
            assert contact_entity["text_length"] == len(
                "John Doe john@example.com Software Engineer"
            )

            # Check second entity (company)
            company_entity = indexed_entities[1]
            assert company_entity["index"] == 1
            assert company_entity["entity_type"] == "companies"
            assert company_entity["entity_id"] == "company1"

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_no_embedding_manager(self):
        """Test FAISS data endpoint when embedding manager is not initialized."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=None,
            ),  # No embedding manager
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):
            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 503
            response_body = json.loads(response.body.decode("utf-8"))

            assert response_body["status"] == "unavailable"
            assert response_body["error"] == "Embedding system not initialized"
            assert "No FAISS index has been built yet" in response_body["message"]

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_index_not_ready(self):
        """Test FAISS data endpoint when index is not ready."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Mock embedding manager with not ready status
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "not_initialized",
            "total_entities": 0,
            "dimension": None,
            "index_type": "flat",
            "cache_size": 0,
        }

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ),
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):
            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 503
            response_body = json.loads(response.body.decode("utf-8"))

            assert response_body["status"] == "not_ready"
            assert response_body["error"] == "FAISS index not ready"
            assert "stats" in response_body
            assert response_body["stats"]["status"] == "not_initialized"
            assert "The FAISS index is not ready" in response_body["message"]

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_exception_handling(self):
        """Test FAISS data endpoint exception handling."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Mock embedding manager that raises an exception
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.side_effect = Exception("Test exception")

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ),
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):
            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 500
            response_body = json.loads(response.body.decode("utf-8"))

            assert response_body["status"] == "error"
            assert response_body["error"] == "Test exception"
            assert "Internal server error" in response_body["message"]

            # Verify error was logged
            mock_endpoints_logger.error.assert_called_with(
                "FAISS data endpoint failed: Test exception"
            )

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_empty_metadata(self):
        """Test FAISS data endpoint with empty entity metadata."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Mock embedding manager with ready status but empty metadata
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "ready",
            "total_entities": 0,
            "dimension": 384,
            "index_type": "flat",
            "model_name": "all-MiniLM-L6-v2",
            "cache_size": 0,
        }
        mock_embedding_manager.entity_metadata = {}  # Empty metadata

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ),
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):
            # Mock datetime for consistent timestamp
            mock_datetime = MagicMock()
            mock_datetime.utcnow.return_value.isoformat.return_value = (
                "2024-01-01T12:00:00"
            )

            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 200
            response_body = json.loads(response.body.decode("utf-8"))

            # Verify response structure with empty data
            assert response_body["status"] == "success"
            assert response_body["entity_summary"]["total_indexed"] == 0
            assert response_body["entity_summary"]["types_count"] == {}
            assert response_body["entity_summary"]["available_types"] == []
            assert response_body["indexed_entities"] == []

            # Verify logging
            mock_endpoints_logger.info.assert_called_with(
                "FAISS data endpoint accessed - returning 0 indexed entities"
            )

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_with_missing_entity_fields(self):
        """Test FAISS data endpoint with entities missing some fields."""
        # Mock all dependencies
        mock_server = AsyncMock()
        mock_hubspot_client = MagicMock()
        mock_handlers = AsyncMock()
        mock_sse = MagicMock()
        mock_uvicorn_config = MagicMock()
        mock_uvicorn_server = AsyncMock()

        # Mock embedding manager with entities missing some fields
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "ready",
            "total_entities": 1,
            "dimension": 384,
            "index_type": "flat",
            "model_name": "all-MiniLM-L6-v2",
            "cache_size": 1,
        }
        mock_embedding_manager.entity_metadata = {
            0: {
                "entity": {"properties": {"name": "Test Entity"}},  # Missing id
                "entity_type": "test_type",
                "text": "",  # Empty text
            }
        }

        # Capture the faiss_data_endpoint function
        captured_faiss_endpoint = None

        def capture_starlette_app(*args, **kwargs):
            routes = kwargs.get("routes", [])
            nonlocal captured_faiss_endpoint

            for route in routes:
                if hasattr(route, "path") and route.path == "/faiss-data":
                    captured_faiss_endpoint = route.endpoint

            return MagicMock()

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
            patch(
                "hubspot_mcp.__main__.HubSpotClient", return_value=mock_hubspot_client
            ),
            patch("hubspot_mcp.__main__.MCPHandlers", return_value=mock_handlers),
            patch("hubspot_mcp.__main__.SseServerTransport", return_value=mock_sse),
            patch("hubspot_mcp.__main__.parse_arguments") as mock_parse_args,
            patch(
                "hubspot_mcp.__main__.InitializationOptions",
                return_value=mock_init_options,
            ),
            patch("hubspot_mcp.__main__.logger") as mock_logger,
            patch(
                "starlette.applications.Starlette", side_effect=capture_starlette_app
            ),
            patch("uvicorn.Config", return_value=mock_uvicorn_config),
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}),
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ),
            patch("hubspot_mcp.sse.endpoints.logger") as mock_endpoints_logger,
        ):
            # Mock datetime for consistent timestamp
            mock_datetime = MagicMock()
            mock_datetime.utcnow.return_value.isoformat.return_value = (
                "2024-01-01T12:00:00"
            )

            # Configure parse_arguments to return SSE mode
            mock_args = MagicMock()
            mock_args.mode = "sse"
            mock_args.host = "localhost"
            mock_args.port = 8080
            mock_parse_args.return_value = mock_args

            mock_uvicorn_server.serve = AsyncMock(return_value=None)

            # Call main() to trigger SSE mode and capture endpoints
            await main.main()

            # Test the captured FAISS endpoint function
            assert captured_faiss_endpoint is not None

            mock_request = MagicMock()
            response = await captured_faiss_endpoint(mock_request)

            assert response.status_code == 200
            response_body = json.loads(response.body.decode("utf-8"))

            # Verify response handles missing fields gracefully
            assert response_body["status"] == "success"
            assert response_body["entity_summary"]["total_indexed"] == 1
            assert response_body["entity_summary"]["types_count"] == {"test_type": 1}

            # Check that missing entity_id is handled (should be None)
            entity = response_body["indexed_entities"][0]
            assert entity["entity_id"] is None
            assert entity["entity_type"] == "test_type"
            assert entity["searchable_text"] == ""
            assert entity["text_length"] == 0
