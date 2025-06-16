"""
Comprehensive unit tests for authentication middleware.

This module provides 100% test coverage for the AuthenticationMiddleware
functionality in the HubSpot MCP Server.
"""

import json
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hubspot_mcp.config.settings import Settings
from hubspot_mcp.sse.middleware import AuthenticationMiddleware


class TestAuthenticationMiddleware:
    """Test authentication middleware functionality."""

    def test_middleware_init_without_auth_key(self):
        """Test middleware initialization without auth key."""
        app_mock = AsyncMock()
        middleware = AuthenticationMiddleware(app_mock)

        assert middleware.app == app_mock
        assert middleware.auth_key is None
        assert middleware.header_name == "X-API-Key"
        assert middleware.exempt_paths == {"/health", "/ready"}

    def test_middleware_init_with_auth_key(self):
        """Test middleware initialization with auth key."""
        app_mock = AsyncMock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key, "X-Custom-Key")

        assert middleware.app == app_mock
        assert middleware.auth_key == auth_key
        assert middleware.header_name == "X-Custom-Key"

    @pytest.mark.asyncio
    async def test_middleware_call_without_auth_key(self):
        """Test middleware call without auth key (auth disabled)."""
        app_mock = AsyncMock()
        middleware = AuthenticationMiddleware(app_mock)

        scope = {"type": "http", "path": "/test"}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify the app was called directly
        app_mock.assert_called_once_with(scope, receive, send)

    @pytest.mark.asyncio
    async def test_middleware_call_exempt_path(self):
        """Test middleware call for exempt paths."""
        app_mock = AsyncMock()
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/health"}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify the app was called directly (exempt path)
        app_mock.assert_called_once_with(scope, receive, send)

    @pytest.mark.asyncio
    async def test_middleware_call_with_valid_auth(self):
        """Test middleware call with valid authentication."""
        app_mock = AsyncMock()
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key, "X-API-Key")

        scope = {
            "type": "http",
            "path": "/protected",
            "headers": [[b"x-api-key", b"test-key-123"]],
        }
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify the app was called (auth passed)
        app_mock.assert_called_once_with(scope, receive, send)

    @pytest.mark.asyncio
    async def test_middleware_call_with_invalid_auth(self):
        """Test middleware call with invalid authentication."""
        app_mock = AsyncMock()
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key, "X-API-Key")

        scope = {
            "type": "http",
            "path": "/protected",
            "headers": [[b"x-api-key", b"wrong-key"]],
        }
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify 401 response was sent
        assert send.call_count == 2
        start_call = send.call_args_list[0][0][0]
        body_call = send.call_args_list[1][0][0]

        assert start_call["type"] == "http.response.start"
        assert start_call["status"] == 401
        assert body_call["type"] == "http.response.body"
        assert body_call["body"] == b"Unauthorized"

    @pytest.mark.asyncio
    async def test_middleware_call_without_auth_header(self):
        """Test middleware call without authentication header."""
        app_mock = AsyncMock()
        auth_key = "test-key-123"
        middleware = AuthenticationMiddleware(app_mock, auth_key)

        scope = {"type": "http", "path": "/protected", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify 401 response was sent
        assert send.call_count == 2
        start_call = send.call_args_list[0][0][0]
        body_call = send.call_args_list[1][0][0]

        assert start_call["type"] == "http.response.start"
        assert start_call["status"] == 401
        assert body_call["type"] == "http.response.body"
        assert body_call["body"] == b"Unauthorized"

    @pytest.mark.asyncio
    async def test_data_protection_disabled_exempts_force_reindex(self):
        """Test that /force-reindex is exempt when DATA_PROTECTION_DISABLED=true."""
        app_mock = AsyncMock()
        auth_key = "test-key"

        # Mock settings with DATA_PROTECTION_DISABLED=true
        with patch("hubspot_mcp.sse.middleware.settings") as mock_settings:
            mock_settings.faiss_data_secure = True  # Keep FAISS secure
            mock_settings.data_protection_disabled = True  # Disable data protection

            middleware = AuthenticationMiddleware(app_mock, auth_key)

            # /force-reindex should be in exempt paths
            assert "/force-reindex" in middleware.exempt_paths

            # Test request to /force-reindex without auth header
            scope = {
                "type": "http",
                "path": "/force-reindex",
                "method": "POST",
                "headers": [],
            }

            receive_mock = AsyncMock()
            send_mock = AsyncMock()

            await middleware(scope, receive_mock, send_mock)

            # Should call the app (not send 401)
            app_mock.assert_called_once_with(scope, receive_mock, send_mock)
            send_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_data_protection_enabled_requires_auth_for_force_reindex(self):
        """Test that /force-reindex requires auth when DATA_PROTECTION_DISABLED=false."""
        app_mock = AsyncMock()
        auth_key = "test-key"

        # Mock settings with DATA_PROTECTION_DISABLED=false (default)
        with patch("hubspot_mcp.sse.middleware.settings") as mock_settings:
            mock_settings.faiss_data_secure = True
            mock_settings.data_protection_disabled = (
                False  # Keep data protection enabled
            )

            middleware = AuthenticationMiddleware(app_mock, auth_key)

            # /force-reindex should NOT be in exempt paths
            assert "/force-reindex" not in middleware.exempt_paths

            # Test request to /force-reindex without auth header
            scope = {
                "type": "http",
                "path": "/force-reindex",
                "method": "POST",
                "headers": [],
            }

            receive_mock = AsyncMock()
            send_mock = AsyncMock()

            await middleware(scope, receive_mock, send_mock)

            # Should send 401 (not call the app)
            app_mock.assert_not_called()

            # Verify 401 response
            send_calls = send_mock.call_args_list
            assert len(send_calls) == 2

            # Check response start
            start_call = send_calls[0][0][0]
            assert start_call["type"] == "http.response.start"
            assert start_call["status"] == 401

            # Check response body
            body_call = send_calls[1][0][0]
            assert body_call["type"] == "http.response.body"
            assert body_call["body"] == b"Unauthorized"


class TestFaissDataSecurity:
    """Test FAISS data security configuration using centralized settings."""

    @patch("hubspot_mcp.sse.middleware.settings")
    def test_faiss_data_secured_by_default(self, mock_settings):
        """Test that /faiss-data is secured by default (FAISS_DATA_SECURE=true)."""
        mock_settings.faiss_data_secure = True
        mock_settings.data_protection_disabled = False  # Default value

        app_mock = AsyncMock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should not be in exempt_paths (secured)
        assert "/faiss-data" not in middleware.exempt_paths
        # /force-reindex should not be in exempt_paths (data protection enabled)
        assert "/force-reindex" not in middleware.exempt_paths
        # Only base exempt paths should be present
        assert middleware.exempt_paths == {"/health", "/ready"}

    @patch("hubspot_mcp.sse.middleware.settings")
    def test_faiss_data_unsecured_when_disabled(self, mock_settings):
        """Test that /faiss-data is unsecured when FAISS_DATA_SECURE=false."""
        mock_settings.faiss_data_secure = False
        mock_settings.data_protection_disabled = False  # Default value

        app_mock = AsyncMock()
        auth_key = "test-key-123"

        middleware = AuthenticationMiddleware(app_mock, auth_key)

        # /faiss-data should be in exempt_paths (unsecured)
        assert "/faiss-data" in middleware.exempt_paths
        # /force-reindex should not be in exempt_paths (data protection enabled)
        assert "/force-reindex" not in middleware.exempt_paths
        # Should have base paths plus faiss-data
        assert middleware.exempt_paths == {"/health", "/ready", "/faiss-data"}

    def test_faiss_data_secure_true_with_settings(self):
        """Test FAISS data security with settings when FAISS_DATA_SECURE=true."""
        with patch.dict(os.environ, {"FAISS_DATA_SECURE": "true"}, clear=True):
            test_settings = Settings()
            assert test_settings.faiss_data_secure is True

            with patch("hubspot_mcp.sse.middleware.settings", test_settings):
                app_mock = AsyncMock()
                auth_key = "test-key-123"
                middleware = AuthenticationMiddleware(app_mock, auth_key)

                assert "/faiss-data" not in middleware.exempt_paths

    def test_faiss_data_secure_false_with_settings(self):
        """Test FAISS data security with settings when FAISS_DATA_SECURE=false."""
        with patch.dict(os.environ, {"FAISS_DATA_SECURE": "false"}, clear=True):
            test_settings = Settings()
            assert test_settings.faiss_data_secure is False

            with patch("hubspot_mcp.sse.middleware.settings", test_settings):
                app_mock = AsyncMock()
                auth_key = "test-key-123"
                middleware = AuthenticationMiddleware(app_mock, auth_key)

                assert "/faiss-data" in middleware.exempt_paths

    def test_faiss_data_boolean_parsing_through_settings(self):
        """Test that boolean parsing works correctly through settings."""
        # Test various boolean values
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("TRUE", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("FALSE", False),
            ("random", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"FAISS_DATA_SECURE": env_value}, clear=True):
                test_settings = Settings()
                assert (
                    test_settings.faiss_data_secure is expected
                ), f"Failed for value: {env_value}"

    def test_settings_integration_with_middleware(self):
        """Test full integration between Settings and AuthenticationMiddleware."""
        # Create a test environment
        test_env = {
            "FAISS_DATA_SECURE": "false",
            "MCP_AUTH_KEY": "test-auth-key",
            "MCP_AUTH_HEADER": "X-Test-Auth",
        }

        with patch.dict(os.environ, test_env, clear=True):
            test_settings = Settings()

            # Verify settings are correct
            assert test_settings.faiss_data_secure is False
            assert test_settings.mcp_auth_key == "test-auth-key"
            assert test_settings.mcp_auth_header == "X-Test-Auth"

            # Test middleware with these settings
            with patch("hubspot_mcp.sse.middleware.settings", test_settings):
                app_mock = AsyncMock()
                middleware = AuthenticationMiddleware(
                    app_mock, test_settings.mcp_auth_key, test_settings.mcp_auth_header
                )

                # Verify middleware configuration
                assert middleware.auth_key == "test-auth-key"
                assert middleware.header_name == "X-Test-Auth"
                assert "/faiss-data" in middleware.exempt_paths

    def test_settings_centralized_configuration(self):
        """Test that all configuration comes from centralized settings."""
        test_env = {
            "HUBSPOT_API_KEY": "test-hubspot-key",
            "MCP_AUTH_KEY": "test-mcp-key",
            "MCP_AUTH_HEADER": "X-Custom-Header",
            "FAISS_DATA_SECURE": "false",
            "LOG_LEVEL": "DEBUG",
            "HOST": "0.0.0.0",
            "PORT": "9000",
        }

        with patch.dict(os.environ, test_env, clear=True):
            test_settings = Settings()

            # Verify all settings are loaded correctly
            assert test_settings.hubspot_api_key == "test-hubspot-key"
            assert test_settings.mcp_auth_key == "test-mcp-key"
            assert test_settings.mcp_auth_header == "X-Custom-Header"
            assert test_settings.faiss_data_secure is False
            assert test_settings.log_level == "DEBUG"
            assert test_settings.host == "0.0.0.0"
            assert test_settings.port == 9000

            # Test that the configuration methods work
            hubspot_config = test_settings.get_hubspot_config()
            auth_config = test_settings.get_auth_config()
            server_config = test_settings.get_server_config()

            assert hubspot_config["api_key"] == "test-hubspot-key"
            assert auth_config["auth_key"] == "test-mcp-key"
            assert auth_config["auth_header"] == "X-Custom-Header"
            assert auth_config["enabled"] is True
            assert server_config["host"] == "0.0.0.0"
            assert server_config["port"] == 9000
