"""
Security Headers Middleware for Echo AI.

This module implements security best practices by adding HTTP security headers
to all responses. These headers protect against common web vulnerabilities:

- HSTS (Strict-Transport-Security): Enforces HTTPS
- CSP (Content-Security-Policy): Prevents XSS attacks
- X-Frame-Options: Prevents clickjacking
- X-Content-Type-Options: Prevents MIME sniffing
- X-XSS-Protection: Legacy XSS protection for older browsers
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.app.core.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    This implements OWASP security best practices for web applications.

    Headers added:
    - Strict-Transport-Security: Force HTTPS for 1 year
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Legacy XSS protection
    - Content-Security-Policy: Restrict resource loading
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware."""
        super().__init__(app)
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year (including subdomains)
        # Only add in production to avoid issues with local development
        if self.settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Prevent MIME type sniffing
        # Forces browsers to respect the Content-Type header
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Clickjacking protection
        # Prevents the site from being embedded in iframes
        response.headers["X-Frame-Options"] = "DENY"

        # Legacy XSS protection (for older browsers)
        # Modern browsers use CSP instead, but this provides defense-in-depth
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy: Don't leak referrer to external sites
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy: Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=()"
        )

        # Content Security Policy (CSP)
        # This is strict - may need adjustment based on frontend needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts for Next.js
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles for Tailwind
            "img-src 'self' data: https:",  # Allow images from anywhere (charts, etc.)
            "font-src 'self' data:",  # Allow fonts
            "connect-src 'self'",  # API calls only to same origin
            "frame-ancestors 'none'",  # Equivalent to X-Frame-Options: DENY
            "base-uri 'self'",  # Prevent base tag injection
            "form-action 'self'",  # Forms can only submit to same origin
        ]

        # In development, allow connections to localhost:3000 (Next.js dev server)
        if self.settings.environment == "development":
            csp_directives[5] = "connect-src 'self' http://localhost:3000 ws://localhost:3000"

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response
