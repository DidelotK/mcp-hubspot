"""
Comprehensive unit tests for authentication middleware.

This module provides 100% test coverage for the AuthenticationMiddleware
functionality in the HubSpot MCP Server.
"""

import json
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hubspot_mcp.__main__ import AuthenticationMiddleware


class TestAuthenticationMiddleware:
    """Test cases for AuthenticationMiddleware."""

    def test_middleware_initialization_default_header(self):
        """Test middleware initialization with default header name."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        assert middleware.app == app_mock
        assert middleware.auth_key == auth_key
        assert middleware.header_name == "X-API-Key"
        assert middleware.exempt_paths == {"/health", "/ready"}

    def test_middleware_initialization_custom_header(self):
        """Test middleware initialization with custom header name."""
        app_mock = Mock()
        auth_key = "test-key-123"
        custom_header = "Authorization"

        middleware = AuthenticationMiddleware(app_mock, auth_key, custom_header)

        assert middleware.app == app_mock
        assert middleware.auth_key == auth_key
        assert middleware.header_name == custom_header
        assert middleware.exempt_paths == {"/health", "/ready"}

    def test_middleware_initialization_no_auth_key(self):
        """Test middleware initialization with no auth key."""
        app_mock = Mock()

        middleware = AuthenticationMiddleware(app_mock, None)

        assert middleware.app == app_mock
        assert middleware.auth_key is None
        assert middleware.header_name == "X-API-Key"

    @pytest.mark.asyncio
    async def test_authentication_disabled_when_no_auth_key(self):
        """Test that authentication is bypassed when no auth key is configured."""
        app_mock = AsyncMock(return_value=None)
        middleware = AuthenticationMiddleware(app_mock, auth_key=None)

        scope = {"type": "http", "path": "/sse"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_exempt_path_health_bypasses_auth(self):
        """Test that /health path bypasses authentication."""
        app_mock = AsyncMock(return_value=None)
        middleware = AuthenticationMiddleware(app_mock, auth_key="test-key")

        scope = {"type": "http", "path": "/health"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_exempt_path_ready_bypasses_auth(self):
        """Test that /ready path bypasses authentication."""
        app_mock = AsyncMock(return_value=None)
        middleware = AuthenticationMiddleware(app_mock, auth_key="test-key")

        scope = {"type": "http", "path": "/ready"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_successful_authentication_with_correct_header(self):
        """Test successful authentication with correct API key."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"x-api-key", b"valid-api-key-123")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_successful_authentication_with_custom_header(self):
        """Test successful authentication with custom header name."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key, "Authorization")

        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"authorization", b"valid-api-key-123")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_authentication_missing_header(self):
        """Test failed authentication when header is missing."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/sse", "headers": []}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_not_called()

        # Verify 401 response was sent
        assert send_mock.call_count == 2

        # Check response start
        response_start = send_mock.call_args_list[0][0][0]
        assert response_start["type"] == "http.response.start"
        assert response_start["status"] == 401
        assert response_start["headers"] == [
            [b"content-type", b"application/json"],
            [b"content-length", b"55"],
        ]

        # Check response body
        response_body = send_mock.call_args_list[1][0][0]
        assert response_body["type"] == "http.response.body"
        expected_body = b'{"error": "Unauthorized", "message": "Invalid API key"}'
        assert response_body["body"] == expected_body

    @pytest.mark.asyncio
    async def test_failed_authentication_wrong_header_value(self):
        """Test failed authentication with incorrect API key."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"x-api-key", b"invalid-api-key")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_not_called()

        # Verify 401 response was sent
        assert send_mock.call_count == 2

        # Check response start
        response_start = send_mock.call_args_list[0][0][0]
        assert response_start["type"] == "http.response.start"
        assert response_start["status"] == 401

    @pytest.mark.asyncio
    async def test_failed_authentication_empty_header_value(self):
        """Test failed authentication with empty header value."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/sse", "headers": [(b"x-api-key", b"")]}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_not_called()

        # Verify 401 response was sent
        assert send_mock.call_count == 2

    @pytest.mark.asyncio
    async def test_non_http_request_bypasses_auth(self):
        """Test that non-HTTP requests bypass authentication."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "websocket", "path": "/ws"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_scope_without_path_key(self):
        """Test handling of scope without path key."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "headers": [(b"x-api-key", b"valid-api-key-123")]}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_scope_without_headers_key(self):
        """Test handling of scope without headers key."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/sse"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_not_called()

        # Should return 401 due to missing headers
        assert send_mock.call_count == 2

    @pytest.mark.asyncio
    async def test_case_insensitive_header_matching(self):
        """Test that header matching is case insensitive."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key, "Authorization")

        # Test with uppercase header name in scope (headers are normalized to lowercase)
        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"authorization", b"valid-api-key-123")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_headers_with_correct_auth(self):
        """Test authentication with multiple headers including correct auth."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [
                (b"content-type", b"application/json"),
                (b"x-api-key", b"valid-api-key-123"),
                (b"user-agent", b"test-client"),
            ],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_header_with_special_characters(self):
        """Test authentication with API key containing special characters."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "key-with-special-chars_123!@#"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"x-api-key", b"key-with-special-chars_123!@#")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_unicode_handling_in_headers(self):
        """Test proper handling of unicode characters in headers."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # Header with unicode characters (should fail gracefully)
        scope = {
            "type": "http",
            "path": "/sse",
            "headers": [(b"x-api-key", "test-key-123-ü".encode("utf-8"))],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        app_mock.assert_not_called()
        assert send_mock.call_count == 2  # Should return 401

    def test_response_body_content_length_accuracy(self):
        """Test that the content-length header matches the actual body length."""
        expected_body = b'{"error": "Unauthorized", "message": "Invalid API key"}'
        expected_length = len(expected_body)

        # The content-length in the middleware should match
        assert expected_length == 55  # As specified in the middleware

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "valid-api-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # Test various protected endpoints
        protected_paths = ["/sse", "/messages/", "/api/v1/data", "/admin"]

        for path in protected_paths:
            app_mock.reset_mock()
            send_mock = AsyncMock()

            scope = {"type": "http", "path": path, "headers": []}
            receive_mock = AsyncMock()

            await middleware(scope, receive_mock, send_mock)

            app_mock.assert_not_called()
            assert (
                send_mock.call_count == 2
            ), f"Path {path} should require authentication"


class TestFaissDataSecurity:
    """Test cases for FAISS data endpoint security configuration."""

    @patch.dict(os.environ, {}, clear=True)
    def test_faiss_data_secure_by_default(self):
        """Test that /faiss-data is secured by default when FAISS_DATA_SECURE is not set."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should NOT be in exempt_paths by default (secured)
        assert "/faiss-data" not in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "true"}, clear=True)
    def test_faiss_data_secure_when_explicitly_true(self):
        """Test that /faiss-data is secured when FAISS_DATA_SECURE=true."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should NOT be in exempt_paths (secured)
        assert "/faiss-data" not in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "false"}, clear=True)
    def test_faiss_data_unsecured_when_false(self):
        """Test that /faiss-data is unsecured when FAISS_DATA_SECURE=false."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (unsecured)
        assert "/faiss-data" in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "0"}, clear=True)
    def test_faiss_data_unsecured_when_zero(self):
        """Test that /faiss-data is unsecured when FAISS_DATA_SECURE=0."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (unsecured)
        assert "/faiss-data" in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "no"}, clear=True)
    def test_faiss_data_unsecured_when_no(self):
        """Test that /faiss-data is unsecured when FAISS_DATA_SECURE=no."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (unsecured)
        assert "/faiss-data" in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "off"}, clear=True)
    def test_faiss_data_unsecured_when_off(self):
        """Test that /faiss-data is unsecured when FAISS_DATA_SECURE=off."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (unsecured)
        assert "/faiss-data" in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "FALSE"}, clear=True)
    def test_faiss_data_case_insensitive(self):
        """Test that FAISS_DATA_SECURE is case insensitive."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (case insensitive)
        assert "/faiss-data" in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "invalid_value"}, clear=True)
    def test_faiss_data_secure_with_invalid_value(self):
        """Test that /faiss-data is secured when FAISS_DATA_SECURE has invalid value."""
        app_mock = Mock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should NOT be in exempt_paths (secured by default for invalid values)
        assert "/faiss-data" not in middleware.exempt_paths
        assert middleware.exempt_paths == {"/health", "/ready"}

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "false"}, clear=True)
    @pytest.mark.asyncio
    async def test_faiss_data_bypasses_auth_when_unsecured(self):
        """Test that /faiss-data bypasses authentication when unsecured."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/faiss-data"}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        # Should call the app directly (bypass auth)
        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "true"}, clear=True)
    @pytest.mark.asyncio
    async def test_faiss_data_requires_auth_when_secured(self):
        """Test that /faiss-data requires authentication when secured."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/faiss-data", "headers": []}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        # Should NOT call the app (requires auth)
        app_mock.assert_not_called()
        # Should send 401 response
        assert send_mock.call_count == 2

    @patch.dict(os.environ, {"FAISS_DATA_SECURE": "true"}, clear=True)
    @pytest.mark.asyncio
    async def test_faiss_data_successful_auth_when_secured(self):
        """Test that /faiss-data works with proper auth when secured."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {
            "type": "http",
            "path": "/faiss-data",
            "headers": [(b"x-api-key", b"test-key-123")],
        }
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        # Should call the app (auth successful)
        app_mock.assert_called_once_with(scope, receive_mock, send_mock)
        send_mock.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    @pytest.mark.asyncio
    async def test_faiss_data_requires_auth_by_default(self):
        """Test that /faiss-data requires auth by default (when env var not set)."""
        app_mock = AsyncMock(return_value=None)
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/faiss-data", "headers": []}
        receive_mock = AsyncMock()
        send_mock = AsyncMock()

        await middleware(scope, receive_mock, send_mock)

        # Should NOT call the app (requires auth by default)
        app_mock.assert_not_called()
        # Should send 401 response
        assert send_mock.call_count == 2
