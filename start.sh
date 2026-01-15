#!/bin/bash
# Monolithic startup script for Echo AI with resource optimization
# Runs database migrations, starts background worker, and launches the web server

set -e

echo "[STARTUP] Current Time: $(date)"
echo "[STARTUP] Running database migrations..."
alembic upgrade head

echo "[STARTUP] Seeding test data..."
python backend/scripts/seed_test_data.py || echo "[STARTUP] Warning: Failed to seed test data (may already exist)"

echo "[STARTUP] Starting Celery worker with low concurrency..."
# Optimized concurrency based on environment (default 4)
celery -A backend.app.worker worker -B --loglevel=info --concurrency=${CELERY_CONCURRENCY:-4} &
WORKER_PID=$!
echo "[STARTUP] Celery worker started with PID $WORKER_PID (concurrency=${CELERY_CONCURRENCY:-4})"

# Wait a moment
sleep 2

echo "[STARTUP] Starting Hypercorn server on port 8080..."
exec hypercorn backend.app.main:app --bind 0.0.0.0:8080
