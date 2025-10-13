"""
API Token Authentication Middleware

This module provides secure token-based authentication for the API.
Tokens are verified via a Bearer token in the Authorization header.
"""

import os
import secrets
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class APITokenAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify API tokens via Bearer authentication

    Tokens should be provided in the Authorization header:
    Authorization: Bearer <token>
    """

    def __init__(self, app, enabled: bool = True, exempt_paths: list = None):
        """
        Initialize the middleware

        Args:
            app: FastAPI application
            enabled: Whether token authentication is enabled (default: True)
            exempt_paths: List of paths that don't require authentication
        """
        super().__init__(app)
        self.enabled = enabled

        # Load API token from environment variable
        self.api_token = os.getenv("API_TOKEN")

        if self.enabled and not self.api_token:
            raise ValueError(
                "API_TOKEN environment variable is required when token authentication is enabled. "
                "Generate a secure token using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # Paths that don't require authentication
        self.exempt_paths = exempt_paths or [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process each request and verify API token

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response from next middleware or error response
        """
        # Skip authentication if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip authentication for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Get Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify Bearer token format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token matches the configured API token
        # Use secrets.compare_digest to prevent timing attacks
        if not secrets.compare_digest(token, self.api_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Token is valid, proceed to next middleware
        return await call_next(request)


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token

    Args:
        length: Number of bytes for the token (default: 32)

    Returns:
        URL-safe base64-encoded token string
    """
    return secrets.token_urlsafe(length)


def verify_token(provided_token: str, expected_token: str) -> bool:
    """
    Verify a token using constant-time comparison to prevent timing attacks

    Args:
        provided_token: Token provided by the client
        expected_token: Expected token from configuration

    Returns:
        True if tokens match, False otherwise
    """
    return secrets.compare_digest(provided_token, expected_token)


if __name__ == "__main__":
    # Generate a new token when run directly
    print("=" * 60)
    print("API Token Generator")
    print("=" * 60)
    print("\nGenerated secure API token:")
    print(generate_token())
    print("\nSet this as your API_TOKEN environment variable:")
    print("  export API_TOKEN='<generated-token>'")
    print("\nOr in Railway:")
    print("  railway variables set API_TOKEN='<generated-token>'")
    print("\nFor the dashboard .env file:")
    print("  VITE_API_TOKEN='<generated-token>'")
    print("=" * 60)
