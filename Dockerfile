# Multi-stage Dockerfile for production deployment

# Stage 1: Frontend Builder
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend

# Copy frontend source
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .

# Build frontend (static export)
RUN npm run build

# Stage 2: Backend Builder
FROM python:3.11-slim as backend-builder

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./
COPY README.md ./

# Install dependencies to a virtual environment
# uv sync creates .venv by default in the current directory (/app/.venv)
RUN uv sync

# Stage 3: Runtime - Minimal production image
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from backend-builder
# Copy uv's default .venv into /app/.venv (matching creation path)
COPY --from=backend-builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY start.sh ./

# Copy compiled frontend from frontend-builder
# Note: copying to the location expected by main.py
COPY --from=frontend-builder /app/frontend/out/ ./frontend/out/

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run application
CMD ["bash", "start.sh"]
