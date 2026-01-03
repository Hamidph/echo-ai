# Multi-stage Dockerfile for production deployment
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files (including README.md required by pyproject.toml)
COPY pyproject.toml ./
COPY uv.lock* ./
COPY README.md ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --frozen

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Railway uses PORT env variable)
EXPOSE 8080

# Run application with dynamic port support
# Railway sets PORT environment variable, defaults to 8080 for local
CMD sh -c "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
