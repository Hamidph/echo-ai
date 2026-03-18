"""Tests for security headers middleware."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.types import ASGIApp

from backend.app.middleware.security_headers import SecurityHeadersMiddleware


class _TestSecurityHeadersMiddleware(SecurityHeadersMiddleware):
    """Subclass that accepts settings directly to avoid get_settings() lru_cache."""

    def __init__(self, app: ASGIApp, environment: str = "development") -> None:
        super().__init__(app)
        mock_settings = MagicMock()
        mock_settings.environment = environment
        self.settings = mock_settings


def _make_app(environment: str) -> FastAPI:
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    app.add_middleware(_TestSecurityHeadersMiddleware, environment=environment)
    return app


@pytest.fixture
def dev_client() -> TestClient:
    return TestClient(_make_app("development"))


@pytest.fixture
def prod_client() -> TestClient:
    return TestClient(_make_app("production"))


class TestSecurityHeaders:
    def test_x_frame_options_present(self, dev_client):
        response = dev_client.get("/test")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_x_content_type_options(self, dev_client):
        response = dev_client.get("/test")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_referrer_policy(self, dev_client):
        response = dev_client.get("/test")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_csp_present(self, dev_client):
        response = dev_client.get("/test")
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "unsafe-eval" not in csp

    def test_permissions_policy(self, dev_client):
        response = dev_client.get("/test")
        pp = response.headers["Permissions-Policy"]
        assert "camera=()" in pp
        assert "microphone=()" in pp

    def test_no_hsts_in_development(self, dev_client):
        response = dev_client.get("/test")
        assert "Strict-Transport-Security" not in response.headers

    def test_hsts_in_production(self, prod_client):
        response = prod_client.get("/test")
        hsts = response.headers.get("Strict-Transport-Security", "")
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_headers_on_error_response(self, dev_client):
        response = dev_client.get("/nonexistent")
        assert response.headers.get("X-Frame-Options") == "DENY"
