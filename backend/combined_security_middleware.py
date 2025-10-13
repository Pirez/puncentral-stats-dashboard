"""
Combined Security Middleware

This module provides a unified security middleware that combines:
- API token authentication
- IP geolocation verification
- Centralized configuration and error handling

This makes the security implementation more robust and easier to manage.
"""

import os
import time
import secrets
from typing import Optional, List
import httpx
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class IPGeolocationCache:
    """Simple in-memory cache for IP geolocation lookups"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl_seconds = ttl_seconds

    def get(self, ip: str) -> Optional[str]:
        if ip in self.cache:
            country_code, timestamp = self.cache[ip]
            if time.time() - timestamp < self.ttl_seconds:
                return country_code
            else:
                del self.cache[ip]
        return None

    def set(self, ip: str, country_code: str):
        self.cache[ip] = (country_code, time.time())

    def clear_expired(self):
        current_time = time.time()
        expired_keys = [
            ip for ip, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]


class CombinedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Combined security middleware that handles both:
    1. API token authentication (Bearer tokens)
    2. IP geolocation verification

    This provides a single, unified security layer that's more robust
    and easier to configure than separate middlewares.
    """

    def __init__(
        self,
        app,
        # Token authentication settings
        token_auth_enabled: bool = True,
        api_token: Optional[str] = None,
        # Geolocation settings
        geolocation_enabled: bool = True,
        allowed_countries: List[str] = None,
        cache_ttl: int = 3600,
        # Common settings
        exempt_paths: List[str] = None,
        # CORS settings
        cors_origins: List[str] = None,
    ):
        """
        Initialize the combined security middleware

        Args:
            app: FastAPI application
            token_auth_enabled: Enable token authentication (default: True)
            api_token: API token for authentication (required if token_auth_enabled)
            geolocation_enabled: Enable IP geolocation verification (default: True)
            allowed_countries: List of allowed country codes (default: ["NO"])
            cache_ttl: Cache TTL for geolocation lookups in seconds (default: 3600)
            exempt_paths: Paths that bypass all security checks
        """
        super().__init__(app)

        # Token authentication settings
        self.token_auth_enabled = token_auth_enabled
        self.api_token = api_token

        if self.token_auth_enabled and not self.api_token:
            raise ValueError(
                "API token is required when token authentication is enabled. "
                "Set API_TOKEN environment variable or pass api_token parameter."
            )

        # Geolocation settings
        self.geolocation_enabled = geolocation_enabled
        self.allowed_countries = allowed_countries or ["NO"]
        self.geo_cache = IPGeolocationCache(ttl_seconds=cache_ttl)

        # Exempt paths (bypass all security checks)
        self.exempt_paths = exempt_paths or [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        # CORS origins for error responses
        self.cors_origins = cors_origins or ["*"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process each request through security checks

        Order of operations:
        1. Check if path is exempt
        2. Verify API token (if enabled)
        3. Verify IP geolocation (if enabled)
        4. Proceed to next middleware/handler

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response from next middleware or error response
        """
        # Skip all security checks for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # 1. API Token Authentication
        if self.token_auth_enabled:
            try:
                await self._verify_token(request)
            except HTTPException as e:
                # Return proper JSON error response with CORS headers
                return self._create_error_response(e, request)

        # 2. IP Geolocation Verification
        if self.geolocation_enabled:
            client_ip = self._get_client_ip(request)

            # Skip geolocation check for local/private IPs
            if not self._is_local_ip(client_ip):
                try:
                    await self._verify_geolocation(client_ip)
                except HTTPException as e:
                    return self._create_error_response(e, request)

        # All security checks passed
        return await call_next(request)

    def _create_error_response(self, exception: HTTPException, request: Request):
        """
        Create error response with CORS headers

        Args:
            exception: HTTPException to convert to response
            request: Original request (for CORS origin check)

        Returns:
            JSONResponse with CORS headers
        """
        from starlette.responses import JSONResponse

        # Get origin from request
        origin = request.headers.get("origin")

        # Build CORS headers
        cors_headers = {}
        if origin:
            # Check if origin is allowed
            if "*" in self.cors_origins or origin in self.cors_origins:
                cors_headers["Access-Control-Allow-Origin"] = origin
                cors_headers["Access-Control-Allow-Credentials"] = "true"
                cors_headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                cors_headers["Access-Control-Allow-Headers"] = "*"

        # Merge with exception headers
        response_headers = {**cors_headers, **(exception.headers or {})}

        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": exception.detail},
            headers=response_headers,
        )

    async def _verify_token(self, request: Request):
        """
        Verify API token from Authorization header

        Args:
            request: Incoming request

        Raises:
            HTTPException: If token is missing, invalid, or doesn't match
        """
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

        # Verify token matches (constant-time comparison)
        if not secrets.compare_digest(token, self.api_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def _verify_geolocation(self, client_ip: str):
        """
        Verify client IP is from an allowed country

        Args:
            client_ip: Client IP address

        Raises:
            HTTPException: If IP is not from an allowed country
        """
        # Check cache first
        country_code = self.geo_cache.get(client_ip)

        # If not in cache, perform API lookup
        if country_code is None:
            country_code = await self._lookup_country(client_ip)
            if country_code:
                self.geo_cache.set(client_ip, country_code)

        # Verify country is allowed
        if country_code not in self.allowed_countries:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: API only accessible from {', '.join(self.allowed_countries)}",
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies"""
        # Check X-Forwarded-For header (from proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client address
        return request.client.host if request.client else "127.0.0.1"

    def _is_local_ip(self, ip: str) -> bool:
        """Check if IP is localhost or private network"""
        local_patterns = ["127.", "localhost", "::1", "192.168.", "10.", "172."]
        return any(ip.startswith(pattern) for pattern in local_patterns)

    async def _lookup_country(self, ip: str) -> Optional[str]:
        """
        Lookup country code for IP address using ip-api.com

        Args:
            ip: IP address to look up

        Returns:
            Two-letter country code or None if lookup fails
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={"fields": "status,countryCode"}
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        return data.get("countryCode")
        except Exception as e:
            # Log error but fail-open (allow request if API is down)
            print(f"Geolocation API error for IP {ip}: {e}")
            # Return allowed country to prevent blocking legitimate users
            return self.allowed_countries[0] if self.allowed_countries else "NO"

        return None


def create_security_middleware(app):
    """
    Factory function to create security middleware from environment variables

    Reads configuration from:
    - API_TOKEN: Token for authentication
    - API_TOKEN_ENABLED: Enable token auth (default: true)
    - GEOLOCATION_ENABLED: Enable geolocation (default: true)
    - ALLOWED_COUNTRIES: Comma-separated country codes (default: NO)
    - GEO_CACHE_TTL: Cache TTL in seconds (default: 3600)

    Args:
        app: FastAPI application

    Returns:
        Configured CombinedSecurityMiddleware instance
    """
    # Read configuration from environment
    token_auth_enabled = os.getenv("API_TOKEN_ENABLED", "true").lower() == "true"
    geolocation_enabled = os.getenv("GEOLOCATION_ENABLED", "true").lower() == "true"

    api_token = os.getenv("API_TOKEN") if token_auth_enabled else None
    allowed_countries = os.getenv("ALLOWED_COUNTRIES", "NO").split(",")
    cache_ttl = int(os.getenv("GEO_CACHE_TTL", "3600"))

    return CombinedSecurityMiddleware(
        app,
        token_auth_enabled=token_auth_enabled,
        api_token=api_token,
        geolocation_enabled=geolocation_enabled,
        allowed_countries=allowed_countries,
        cache_ttl=cache_ttl,
    )


# Utility function for generating secure tokens
def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    # Generate a new token when run directly
    print("=" * 60)
    print("Combined Security Middleware - Token Generator")
    print("=" * 60)
    print("\nGenerated secure API token:")
    print(generate_token())
    print("\nSet this as your API_TOKEN environment variable:")
    print("  export API_TOKEN='<generated-token>'")
    print("\nConfiguration options:")
    print("  API_TOKEN_ENABLED=true|false")
    print("  GEOLOCATION_ENABLED=true|false")
    print("  ALLOWED_COUNTRIES=NO,SE,DK (comma-separated)")
    print("  GEO_CACHE_TTL=3600 (seconds)")
    print("=" * 60)
