# Multi-stage Dockerfile for monolithic deployment
# Stage 1: Frontend Builder
FROM node:20-slim AS frontend_builder
WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ .

# Build frontend (static export)
# We set the API URL to the production Railway URL
# This enables the frontend to talk to the backend on the same domain
# (Functionally, since we are serving static files, we could use relative paths,
# but the current api.ts implementation relies on this env var)
# ENV NEXT_PUBLIC_API_URL=https://echo-ai-production.up.railway.app
# We rely on build args or default behavior now
RUN npm run build

# Stage 2: Backend Builder
FROM python:3.11-slim as backend_builder

WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./
COPY README.md ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV UV_LINK_MODE=copy
RUN uv sync --frozen

# Stage 3: Runtime
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy virtual environment
COPY --from=backend_builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy built frontend assets
COPY --from=frontend_builder /app/frontend/out /app/static

# Copy startup script
COPY start.sh ./
RUN chmod +x ./start.sh

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8080

# Run startup script (migrations + server + worker)
CMD ["./start.sh"]

