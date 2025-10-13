"""
Tests for API Token Authentication Middleware
"""

import pytest
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api_token_auth import APITokenAuthMiddleware, generate_token, verify_token


def test_generate_token():
    """Test token generation produces unique tokens"""
    token1 = generate_token()
    token2 = generate_token()

    assert isinstance(token1, str)
    assert isinstance(token2, str)
    assert len(token1) > 0
    assert len(token2) > 0
    assert token1 != token2


def test_verify_token():
    """Test token verification"""
    expected = "test-token-123"

    # Valid token should match
    assert verify_token("test-token-123", expected) is True

    # Invalid token should not match
    assert verify_token("wrong-token", expected) is False

    # Empty tokens
    assert verify_token("", expected) is False
    assert verify_token(expected, "") is False


def test_middleware_disabled():
    """Test that middleware passes through when disabled"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    # Middleware disabled, no API_TOKEN required
    app.add_middleware(APITokenAuthMiddleware, enabled=False)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"message": "success"}


def test_middleware_exempt_paths():
    """Test that exempt paths bypass token verification"""
    # Set a test token
    os.environ["API_TOKEN"] = "test-token"

    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "root"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/docs")
    async def docs():
        return {"message": "docs"}

    app.add_middleware(APITokenAuthMiddleware, enabled=True)

    client = TestClient(app)

    # Test exempt paths without token
    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/health")
    assert response.status_code == 200

    response = client.get("/docs")
    assert response.status_code == 200

    # Cleanup
    del os.environ["API_TOKEN"]


def test_middleware_missing_token():
    """Test that requests without token are rejected"""
    os.environ["API_TOKEN"] = "test-token"

    app = FastAPI()

    @app.get("/api/data")
    async def get_data():
        return {"data": "secret"}

    app.add_middleware(APITokenAuthMiddleware, enabled=True)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/data")

    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]

    # Cleanup
    del os.environ["API_TOKEN"]


def test_middleware_invalid_auth_format():
    """Test that invalid Authorization header format is rejected"""
    os.environ["API_TOKEN"] = "test-token"

    app = FastAPI()

    @app.get("/api/data")
    async def get_data():
        return {"data": "secret"}

    app.add_middleware(APITokenAuthMiddleware, enabled=True)

    client = TestClient(app, raise_server_exceptions=False)

    # Test with just token (no Bearer prefix)
    response = client.get(
        "/api/data",
        headers={"Authorization": "test-token"}
    )
    assert response.status_code == 401
    assert "Invalid Authorization header format" in response.json()["detail"]

    # Test with wrong scheme
    response = client.get(
        "/api/data",
        headers={"Authorization": "Basic dGVzdDp0b2tlbg=="}
    )
    assert response.status_code == 401

    # Cleanup
    del os.environ["API_TOKEN"]


def test_middleware_invalid_token():
    """Test that invalid tokens are rejected"""
    os.environ["API_TOKEN"] = "correct-token"

    app = FastAPI()

    @app.get("/api/data")
    async def get_data():
        return {"data": "secret"}

    app.add_middleware(APITokenAuthMiddleware, enabled=True)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/data",
        headers={"Authorization": "Bearer wrong-token"}
    )

    assert response.status_code == 401
    assert "Invalid API token" in response.json()["detail"]

    # Cleanup
    del os.environ["API_TOKEN"]


def test_middleware_valid_token():
    """Test that valid tokens are accepted"""
    os.environ["API_TOKEN"] = "correct-token"

    app = FastAPI()

    @app.get("/api/data")
    async def get_data():
        return {"data": "secret"}

    app.add_middleware(APITokenAuthMiddleware, enabled=True)

    client = TestClient(app)
    response = client.get(
        "/api/data",
        headers={"Authorization": "Bearer correct-token"}
    )

    assert response.status_code == 200
    assert response.json() == {"data": "secret"}

    # Cleanup
    del os.environ["API_TOKEN"]


def test_middleware_requires_token_when_enabled():
    """Test that API_TOKEN env var is required when middleware is enabled"""
    # Ensure API_TOKEN is not set
    if "API_TOKEN" in os.environ:
        del os.environ["API_TOKEN"]

    app = FastAPI()

    # Should raise ValueError when API_TOKEN is not set
    with pytest.raises(ValueError, match="API_TOKEN environment variable is required"):
        app.add_middleware(APITokenAuthMiddleware, enabled=True)


def test_token_length():
    """Test that generated tokens have sufficient length"""
    token = generate_token(32)

    # URL-safe base64 encoding of 32 bytes should be ~43 characters
    assert len(token) >= 40


def test_custom_exempt_paths():
    """Test custom exempt paths configuration"""
    os.environ["API_TOKEN"] = "test-token"

    app = FastAPI()

    @app.get("/custom-public")
    async def custom_public():
        return {"message": "public"}

    @app.get("/protected")
    async def protected():
        return {"message": "protected"}

    app.add_middleware(
        APITokenAuthMiddleware,
        enabled=True,
        exempt_paths=["/custom-public"]
    )

    client = TestClient(app, raise_server_exceptions=False)

    # Custom exempt path should work without token
    response = client.get("/custom-public")
    assert response.status_code == 200

    # Protected path should require token
    response = client.get("/protected")
    assert response.status_code == 401

    # Protected path should work with token
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200

    # Cleanup
    del os.environ["API_TOKEN"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
