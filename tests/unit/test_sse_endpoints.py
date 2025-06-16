"""Tests for SSE endpoints."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request

from hubspot_mcp.sse.endpoints import (
    faiss_data_endpoint,
    force_reindex_endpoint,
    handle_sse,
    health_check,
    readiness_check,
)


class TestHandleSSE:
    """Test the handle_sse endpoint function."""

    @pytest.mark.asyncio
    async def test_handle_sse_connection(self):
        """Test handle_sse establishes SSE connection and runs server."""
        # Mock request, server, sse, and server_options
        mock_request = MagicMock(spec=Request)
        mock_request.scope = {"type": "http", "method": "GET"}
        mock_request.receive = AsyncMock()
        mock_request._send = AsyncMock()

        mock_server = AsyncMock()
        mock_sse = MagicMock()
        mock_server_options = {"option1": "value1"}

        # Mock read and write streams
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        # Mock the connect_sse context manager
        mock_connect_sse = AsyncMock()
        mock_connect_sse.__aenter__ = AsyncMock(
            return_value=(mock_read_stream, mock_write_stream)
        )
        mock_connect_sse.__aexit__ = AsyncMock(return_value=None)
        mock_sse.connect_sse.return_value = mock_connect_sse

        # Call handle_sse
        await handle_sse(mock_request, mock_server, mock_sse, mock_server_options)

        # Verify SSE connection was established
        mock_sse.connect_sse.assert_called_once_with(
            mock_request.scope,
            mock_request.receive,
            mock_request._send,
        )

        # Verify server.run was called with streams and options
        mock_server.run.assert_called_once_with(
            mock_read_stream,
            mock_write_stream,
            mock_server_options,
        )


class TestHealthCheck:
    """Test the health_check endpoint function."""

    @pytest.mark.asyncio
    async def test_health_check_healthy_with_api_key(self):
        """Test health_check returns healthy status when API key is configured."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # Mock settings with API key configured
            mock_settings.hubspot_api_key = "test-api-key"
            mock_settings.server_name = "test-server"
            mock_settings.server_version = "1.0.0"
            mock_settings.is_authentication_enabled.return_value = True

            response = await health_check(mock_request)

            assert response.status_code == 200
            response_body = response.body.decode("utf-8")
            assert '"status":"healthy"' in response_body
            assert '"server":"test-server"' in response_body
            assert '"version":"1.0.0"' in response_body
            assert '"mode":"sse"' in response_body
            assert '"auth_enabled":true' in response_body

    @pytest.mark.asyncio
    async def test_health_check_exception_handling(self):
        """Test health_check exception handling."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # Configure settings to have API key but raise exception on server_name access
            mock_settings.hubspot_api_key = "test-key"

            # Create a property that raises an exception when accessed
            def raise_exception():
                raise Exception("Settings error")

            type(mock_settings).server_name = property(lambda self: raise_exception())

            with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                response = await health_check(mock_request)

                assert response.status_code == 503
                response_body = response.body.decode("utf-8")
                assert '"status":"unhealthy"' in response_body
                assert '"error":"Settings error"' in response_body

                # Verify error was logged
                mock_logger.error.assert_called_once_with(
                    "Health check failed: Settings error"
                )


class TestReadinessCheck:
    """Test the readiness_check endpoint function."""

    @pytest.mark.asyncio
    async def test_readiness_check_ready_with_api_key(self):
        """Test readiness_check returns ready status when API key is configured."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # Mock settings with API key configured
            mock_settings.hubspot_api_key = "test-api-key"
            mock_settings.server_name = "test-server"
            mock_settings.server_version = "1.0.0"
            mock_settings.is_authentication_enabled.return_value = False

            with patch("hubspot_mcp.sse.endpoints.HubSpotClient") as mock_client_class:
                # Mock successful client creation
                mock_client_instance = MagicMock()
                mock_client_class.return_value = mock_client_instance

                response = await readiness_check(mock_request)

                assert response.status_code == 200
                response_body = response.body.decode("utf-8")
                assert '"status":"ready"' in response_body
                assert '"server":"test-server"' in response_body
                assert '"version":"1.0.0"' in response_body
                assert '"mode":"sse"' in response_body
                assert '"auth_enabled":false' in response_body

                # Verify HubSpot client was created for readiness test
                mock_client_class.assert_called_once_with(api_key="test-api-key")

    @pytest.mark.asyncio
    async def test_readiness_check_client_creation_failure(self):
        """Test readiness_check when HubSpot client creation fails."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # Mock settings with API key configured
            mock_settings.hubspot_api_key = "invalid-api-key"

            with patch("hubspot_mcp.sse.endpoints.HubSpotClient") as mock_client_class:
                # Mock client creation failure
                mock_client_class.side_effect = Exception("Invalid API key")

                with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                    response = await readiness_check(mock_request)

                    assert response.status_code == 503
                    response_body = response.body.decode("utf-8")
                    assert '"status":"not_ready"' in response_body
                    assert '"error":"Invalid API key"' in response_body

                    # Verify error was logged
                    mock_logger.error.assert_called_once_with(
                        "Readiness check failed: Invalid API key"
                    )

    @pytest.mark.asyncio
    async def test_readiness_check_settings_exception(self):
        """Test readiness_check exception handling from settings access."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # Configure settings to have API key but raise exception on server_name access
            mock_settings.hubspot_api_key = "test-key"

            # Create a property that raises an exception when accessed
            def raise_exception():
                raise Exception("Settings access error")

            type(mock_settings).server_name = property(lambda self: raise_exception())

            with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                response = await readiness_check(mock_request)

                assert response.status_code == 503
                response_body = response.body.decode("utf-8")
                assert '"status":"not_ready"' in response_body
                assert '"error":"Settings access error"' in response_body

                # Verify error was logged
                mock_logger.error.assert_called_once_with(
                    "Readiness check failed: Settings access error"
                )


class TestFaissDataEndpointCoverage:
    """Additional tests for FAISS data endpoint to improve coverage."""

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_successful_with_entities(self):
        """Test successful FAISS data endpoint with various entity types."""
        mock_request = MagicMock(spec=Request)

        # Mock embedding manager with comprehensive data
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "ready",
            "total_entities": 3,
            "dimension": 768,
            "index_type": "ivf",
            "model_name": "sentence-transformers/all-mpnet-base-v2",
            "cache_size": 10,
        }
        mock_embedding_manager.entity_metadata = {
            0: {
                "entity": {"id": "contact_123", "properties": {"name": "John Doe"}},
                "entity_type": "contacts",
                "text": "John Doe - Sales Representative",
            },
            1: {
                "entity": {"id": "company_456", "properties": {"name": "TechCorp"}},
                "entity_type": "companies",
                "text": "TechCorp - Technology Company",
            },
            2: {
                "entity": {"id": "deal_789", "properties": {"name": "Big Deal"}},
                "entity_type": "deals",
                "text": "Big Deal - $100,000 opportunity",
            },
        }

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            mock_settings.server_name = "hubspot-mcp-server"
            mock_settings.server_version = "2.0.0"

            # Use the pattern from existing tests - patch the tools module
            with patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ):
                with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                    response = await faiss_data_endpoint(mock_request)

                    assert response.status_code == 200
                    response_body = response.body.decode("utf-8")

                    # Verify response structure
                    assert '"status":"success"' in response_body
                    assert '"server":"hubspot-mcp-server"' in response_body
                    assert '"version":"2.0.0"' in response_body
                    assert '"total_entities":3' in response_body
                    assert '"vector_dimension":768' in response_body
                    assert '"index_type":"ivf"' in response_body
                    assert (
                        '"model_name":"sentence-transformers/all-mpnet-base-v2"'
                        in response_body
                    )

                    # Verify entity counts by type
                    assert '"contacts":1' in response_body
                    assert '"companies":1' in response_body
                    assert '"deals":1' in response_body

                    # Verify logging
                    mock_logger.info.assert_called_once_with(
                        "FAISS data endpoint accessed - returning 3 indexed entities"
                    )

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_with_missing_entity_fields(self):
        """Test FAISS endpoint with entities that have missing or incomplete fields."""
        mock_request = MagicMock(spec=Request)

        # Mock embedding manager with incomplete entity data
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "ready",
            "total_entities": 2,
            "dimension": 384,
            "index_type": "flat",
        }
        mock_embedding_manager.entity_metadata = {
            0: {
                "entity": {"properties": {"name": "No ID Entity"}},  # Missing 'id'
                "entity_type": "contacts",
                "text": "",  # Empty text
            },
            1: {
                "entity": {"id": "partial_data"},  # Missing 'properties'
                "entity_type": "unknown_type",
                # Missing 'text' field entirely
            },
        }

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            mock_settings.server_name = "test-server"
            mock_settings.server_version = "1.0.0"

            # Use the pattern from existing tests - patch the tools module
            with patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
                return_value=mock_embedding_manager,
            ):
                with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                    response = await faiss_data_endpoint(mock_request)

                    assert response.status_code == 200
                    response_body = response.body.decode("utf-8")

                    # Should handle missing fields gracefully
                    assert '"status":"success"' in response_body
                    assert '"total_indexed":2' in response_body

                    # Verify entity types are counted correctly
                    assert '"contacts":1' in response_body
                    assert '"unknown_type":1' in response_body

                    # Verify logging
                    mock_logger.info.assert_called_once_with(
                        "FAISS data endpoint accessed - returning 2 indexed entities"
                    )


class TestEndpointErrorPaths:
    """Test error paths and edge cases to improve coverage."""

    @pytest.mark.asyncio
    async def test_health_check_without_api_key(self):
        """Test health_check when no API key is configured (line 31)."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # No API key configured
            mock_settings.hubspot_api_key = None

            response = await health_check(mock_request)

            assert response.status_code == 503
            response_body = response.body.decode("utf-8")
            assert '"status":"unhealthy"' in response_body
            assert '"error":"HUBSPOT_API_KEY not configured"' in response_body

    @pytest.mark.asyncio
    async def test_readiness_check_without_api_key(self):
        """Test readiness_check when no API key is configured (line 62)."""
        mock_request = MagicMock(spec=Request)

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            # No API key configured
            mock_settings.hubspot_api_key = None

            response = await readiness_check(mock_request)

            assert response.status_code == 503
            response_body = response.body.decode("utf-8")
            assert '"status":"not_ready"' in response_body
            assert '"error":"HUBSPOT_API_KEY not configured"' in response_body

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_no_embedding_manager(self):
        """Test FAISS endpoint when no embedding manager is available (line 103)."""
        mock_request = MagicMock(spec=Request)

        # Mock get_embedding_manager to return None
        with patch(
            "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
            return_value=None,
        ):
            response = await faiss_data_endpoint(mock_request)

            assert response.status_code == 503
            response_body = response.body.decode("utf-8")
            assert '"status":"unavailable"' in response_body
            assert '"error":"Embedding system not initialized"' in response_body

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_index_not_ready(self):
        """Test FAISS endpoint when index is not ready (line 116)."""
        mock_request = MagicMock(spec=Request)

        # Mock embedding manager with not ready status
        mock_embedding_manager = MagicMock()
        mock_embedding_manager.get_index_stats.return_value = {
            "status": "not_initialized",
            "total_entities": 0,
        }

        with patch(
            "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
            return_value=mock_embedding_manager,
        ):
            response = await faiss_data_endpoint(mock_request)

            assert response.status_code == 503
            response_body = response.body.decode("utf-8")
            assert '"status":"not_ready"' in response_body
            assert '"error":"FAISS index not ready"' in response_body

    @pytest.mark.asyncio
    async def test_faiss_data_endpoint_exception_handling(self):
        """Test FAISS endpoint exception handling (lines 184-186)."""
        mock_request = MagicMock(spec=Request)

        # Mock embedding manager to raise exception
        with patch(
            "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool.get_embedding_manager",
            side_effect=Exception("Test exception"),
        ):
            with patch("hubspot_mcp.sse.endpoints.logger") as mock_logger:
                response = await faiss_data_endpoint(mock_request)

                assert response.status_code == 500
                response_body = response.body.decode("utf-8")
                assert '"status":"error"' in response_body
                assert '"error":"Test exception"' in response_body
                assert (
                    '"message":"Internal server error while retrieving FAISS data"'
                    in response_body
                )

                # Verify error was logged
                mock_logger.error.assert_called_once_with(
                    "FAISS data endpoint failed: Test exception"
                )


class TestForceReindexEndpoint:
    """Test cases for the force reindex endpoint."""

    @pytest.mark.asyncio
    async def test_force_reindex_success_basic(self):
        """Test successful force reindex operation."""
        # Mock settings
        with (
            patch("hubspot_mcp.sse.endpoints.settings") as mock_settings,
            patch("hubspot_mcp.sse.endpoints.HubSpotClient") as mock_client_class,
            patch(
                "hubspot_mcp.tools.bulk_cache_loader.BulkCacheLoaderTool"
            ) as mock_bulk_loader_class,
            patch(
                "hubspot_mcp.tools.embedding_management_tool.EmbeddingManagementTool"
            ) as mock_embedding_tool_class,
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool"
            ) as mock_enhanced_base,
        ):
            # Setup mocks
            mock_settings.hubspot_api_key = "test-api-key"
            mock_settings.server_name = "test-server"
            mock_settings.server_version = "0.1.0"

            # Mock client
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock bulk loader
            mock_bulk_loader = MagicMock()
            mock_bulk_loader_class.return_value = mock_bulk_loader
            mock_bulk_loader.clear_cache = MagicMock()

            # Mock successful bulk loader execution
            mock_result = MagicMock()
            mock_result.text = (
                "✅ Built embeddings for 100 contacts\nTotal Loaded: 100 entities"
            )
            mock_bulk_loader.execute = AsyncMock(return_value=[mock_result])

            # Mock embedding tool
            mock_embedding_tool = MagicMock()
            mock_embedding_tool_class.return_value = mock_embedding_tool
            mock_embedding_tool.clear_embedding_cache = MagicMock()

            # Mock embedding manager
            mock_embedding_manager = MagicMock()
            mock_enhanced_base.get_embedding_manager.return_value = (
                mock_embedding_manager
            )
            mock_embedding_manager.get_index_stats.return_value = {
                "status": "ready",
                "total_entities": 300,
                "dimension": 384,
                "index_type": "Flat",
                "model_name": "all-MiniLM-L6-v2",
            }

            # Import and test the endpoint
            from hubspot_mcp.sse.endpoints import force_reindex_endpoint

            # Create mock request
            mock_request = MagicMock()

            # Call the endpoint
            response = await force_reindex_endpoint(mock_request)

            # Verify response
            assert response.status_code == 200
            response_data = json.loads(response.body)

            assert response_data["status"] == "success"
            assert "server_info" in response_data
            assert "process_log" in response_data
            assert "entity_results" in response_data
            assert "summary" in response_data

            # Verify all entity types were processed
            assert len(response_data["entity_results"]) == 3
            assert "contacts" in response_data["entity_results"]
            assert "companies" in response_data["entity_results"]
            assert "deals" in response_data["entity_results"]

            # Verify methods were called
            mock_bulk_loader.clear_cache.assert_called_once()
            mock_embedding_tool.clear_embedding_cache.assert_called_once()
            assert mock_bulk_loader.execute.call_count == 3  # Once for each entity type

    @pytest.mark.asyncio
    async def test_force_reindex_no_api_key(self):
        """Test force reindex when HubSpot API key is not configured."""
        from unittest.mock import patch

        with patch("hubspot_mcp.sse.endpoints.settings") as mock_settings:
            mock_settings.hubspot_api_key = None

            from hubspot_mcp.sse.endpoints import force_reindex_endpoint

            mock_request = MagicMock()
            response = await force_reindex_endpoint(mock_request)

            assert response.status_code == 503
            response_data = json.loads(response.body)
            assert response_data["status"] == "error"
            assert "HUBSPOT_API_KEY not configured" in response_data["error"]

    @pytest.mark.asyncio
    async def test_force_reindex_partial_failure(self):
        """Test force reindex with some entity types failing."""
        from unittest.mock import AsyncMock, MagicMock, patch

        with (
            patch("hubspot_mcp.sse.endpoints.settings") as mock_settings,
            patch("hubspot_mcp.sse.endpoints.HubSpotClient") as mock_client_class,
            patch(
                "hubspot_mcp.tools.bulk_cache_loader.BulkCacheLoaderTool"
            ) as mock_bulk_loader_class,
            patch(
                "hubspot_mcp.tools.embedding_management_tool.EmbeddingManagementTool"
            ) as mock_embedding_tool_class,
            patch(
                "hubspot_mcp.tools.enhanced_base.EnhancedBaseTool"
            ) as mock_enhanced_base,
        ):
            # Setup mocks
            mock_settings.hubspot_api_key = "test-api-key"
            mock_settings.server_name = "test-server"
            mock_settings.server_version = "0.1.0"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_bulk_loader = MagicMock()
            mock_bulk_loader_class.return_value = mock_bulk_loader
            mock_bulk_loader.clear_cache = MagicMock()

            # Mock mixed success/failure results
            call_count = 0

            async def mock_execute(args):
                nonlocal call_count
                call_count += 1
                if call_count == 1:  # contacts succeed
                    mock_result = MagicMock()
                    mock_result.text = "✅ Built embeddings for 100 contacts\nTotal Loaded: 100 entities"
                    return [mock_result]
                elif call_count == 2:  # companies fail
                    raise Exception("API rate limit exceeded")
                else:  # deals succeed
                    mock_result = MagicMock()
                    mock_result.text = (
                        "✅ Built embeddings for 200 deals\nTotal Loaded: 200 entities"
                    )
                    return [mock_result]

            mock_bulk_loader.execute = mock_execute

            mock_embedding_tool = MagicMock()
            mock_embedding_tool_class.return_value = mock_embedding_tool
            mock_embedding_tool.clear_embedding_cache = MagicMock()

            # Mock embedding manager
            mock_embedding_manager = MagicMock()
            mock_enhanced_base.get_embedding_manager.return_value = (
                mock_embedding_manager
            )
            mock_embedding_manager.get_index_stats.return_value = {
                "status": "ready",
                "total_entities": 300,
            }

            from hubspot_mcp.sse.endpoints import force_reindex_endpoint

            mock_request = MagicMock()
            response = await force_reindex_endpoint(mock_request)

            # Should still return 200 with partial success
            assert response.status_code == 200
            response_data = json.loads(response.body)

            assert response_data["status"] == "success"

            # Check entity results
            entity_results = response_data["entity_results"]
            assert entity_results["contacts"]["status"] == "success"
            assert entity_results["companies"]["status"] == "error"
            assert entity_results["deals"]["status"] == "success"

            # Check summary
            summary = response_data["summary"]
            assert summary["successful_entity_types"] == 2
            assert summary["failed_entity_types"] == 1
            assert summary["total_entities_loaded"] == 300

    @pytest.mark.asyncio
    async def test_force_reindex_complete_failure(self):
        """Test force reindex with complete failure."""
        from unittest.mock import MagicMock, patch

        with (
            patch("hubspot_mcp.sse.endpoints.settings") as mock_settings,
            patch("hubspot_mcp.sse.endpoints.HubSpotClient") as mock_client_class,
        ):
            mock_settings.hubspot_api_key = "test-api-key"
            mock_client_class.side_effect = Exception("Cannot connect to HubSpot")

            from hubspot_mcp.sse.endpoints import force_reindex_endpoint

            mock_request = MagicMock()
            response = await force_reindex_endpoint(mock_request)

            assert response.status_code == 500
            response_data = json.loads(response.body)
            assert response_data["status"] == "error"
            assert "Cannot connect to HubSpot" in response_data["error"]
