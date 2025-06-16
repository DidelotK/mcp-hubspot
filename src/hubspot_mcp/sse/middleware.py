"""Authentication middleware for SSE server."""

import os
from typing import Optional

from ..config.settings import settings


class AuthenticationMiddleware:
    """Authentication middleware for SSE server."""

    def __init__(
        self, app, auth_key: Optional[str] = None, header_name: str = "X-API-Key"
    ):
        """
        Initialize authentication middleware.

        Args:
            app: ASGI application to wrap
            auth_key: API key for authentication (None disables auth)
            header_name: Header name to check for auth key
        """
        self.app = app
        self.auth_key = auth_key
        self.header_name = header_name

        # Base exempt paths (always unsecured)
        self.exempt_paths = {"/health", "/ready"}

        # Add /faiss-data to exempt paths if FAISS_DATA_SECURE is set to false
        # By default, /faiss-data is secured (FAISS_DATA_SECURE=true)
        if not settings.faiss_data_secure:
            self.exempt_paths.add("/faiss-data")

        # Add /force-reindex to exempt paths if DATA_PROTECTION_DISABLED is set to true
        # By default, /force-reindex is secured (DATA_PROTECTION_DISABLED=false)
        if settings.data_protection_disabled:
            self.exempt_paths.add("/force-reindex")

    async def __call__(self, scope, receive, send):
        """
        ASGI middleware call method.

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        # Skip authentication if no auth key is configured
        if not self.auth_key:
            await self.app(scope, receive, send)
            return

        # Skip authentication for exempt paths
        path = scope.get("path", "")
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        # Check for authentication header
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(self.header_name.lower().encode(), b"").decode()

        # Verify authentication
        if auth_header != self.auth_key:
            # Send 401 Unauthorized response
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        [b"content-type", b"text/plain"],
                        [b"content-length", b"12"],
                    ],
                }
            )
            await send({"type": "http.response.body", "body": b"Unauthorized"})
            return

        # Authentication successful, proceed with request
        await self.app(scope, receive, send)
