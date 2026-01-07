#!/bin/bash
# Monolithic startup script for Echo AI with resource optimization
# Runs database migrations, starts background worker, and launches the web server

set -e

echo "[STARTUP] Current Time: $(date)"
echo "[STARTUP] Running database migrations..."
alembic upgrade head

echo "[STARTUP] Starting Celery worker with low concurrency..."
# Reduced concurrency to 2 to prevent OOM in small containers
celery -A backend.app.worker worker -B --loglevel=info --concurrency=2 &
WORKER_PID=$!
echo "[STARTUP] Celery worker started with PID $WORKER_PID (concurrency=2)"

# Wait a moment
sleep 2

echo "[STARTUP] Starting Hypercorn server on port 8080..."
exec hypercorn backend.app.main:app --bind 0.0.0.0:8080
