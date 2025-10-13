"""
IP Geolocation Verification Middleware

This module provides middleware to verify that API requests come from Norwegian IP addresses.
It includes a simple caching mechanism to avoid repeated lookups for the same IP.
"""

import time
from typing import Optional
import httpx
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class IPGeolocationCache:
    """Simple in-memory cache for IP geolocation lookups"""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize the cache

        Args:
            ttl_seconds: Time to live for cache entries in seconds (default: 1 hour)
        """
        self.cache = {}
        self.ttl_seconds = ttl_seconds

    def get(self, ip: str) -> Optional[str]:
        """
        Get country code from cache

        Args:
            ip: IP address to look up

        Returns:
            Country code if found and not expired, None otherwise
        """
        if ip in self.cache:
            country_code, timestamp = self.cache[ip]
            if time.time() - timestamp < self.ttl_seconds:
                return country_code
            else:
                # Entry expired, remove it
                del self.cache[ip]
        return None

    def set(self, ip: str, country_code: str):
        """
        Store country code in cache

        Args:
            ip: IP address
            country_code: Two-letter country code
        """
        self.cache[ip] = (country_code, time.time())

    def clear_expired(self):
        """Remove all expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            ip for ip, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]


class IPGeolocationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify that requests come from Norwegian IP addresses

    Uses ip-api.com free API for geolocation lookups with caching to minimize API calls.
    """

    def __init__(self, app, cache_ttl: int = 3600, enabled: bool = True,
                 allowed_countries: list = None):
        """
        Initialize the middleware

        Args:
            app: FastAPI application
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            enabled: Whether geolocation checking is enabled (default: True)
            allowed_countries: List of allowed country codes (default: ["NO"])
        """
        super().__init__(app)
        self.cache = IPGeolocationCache(ttl_seconds=cache_ttl)
        self.enabled = enabled
        self.allowed_countries = allowed_countries or ["NO"]

        # Paths that don't require geolocation check
        self.exempt_paths = ["/health", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process each request and verify IP geolocation

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response from next middleware or error response
        """
        # Skip geolocation check if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip geolocation check for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Skip check for localhost/private IPs (development)
        if self._is_local_ip(client_ip):
            return await call_next(request)

        # Check cache first
        country_code = self.cache.get(client_ip)

        # If not in cache, perform API lookup
        if country_code is None:
            country_code = await self._lookup_country(client_ip)
            if country_code:
                self.cache.set(client_ip, country_code)

        # Verify country is allowed
        if country_code not in self.allowed_countries:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: API only accessible from {', '.join(self.allowed_countries)}"
            )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request, considering proxies

        Args:
            request: Incoming request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (from proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client address
        return request.client.host if request.client else "127.0.0.1"

    def _is_local_ip(self, ip: str) -> bool:
        """
        Check if IP is localhost or private network

        Args:
            ip: IP address to check

        Returns:
            True if IP is local/private, False otherwise
        """
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
            # Log error but don't block request if API fails
            print(f"Geolocation API error for IP {ip}: {e}")
            # In production, you might want to fail-closed (deny) or fail-open (allow)
            # For now, we'll fail-open to avoid blocking legitimate users if API is down
            return "NO"  # Allow request if lookup fails

        return None
