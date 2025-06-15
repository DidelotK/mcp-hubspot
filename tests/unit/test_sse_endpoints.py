"""Tests for SSE endpoints."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request

from hubspot_mcp.sse.endpoints import (
    faiss_data_endpoint,
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
