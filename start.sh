#!/bin/bash
# Monolithic startup script for Echo AI with resource optimization
# Runs database migrations, starts background worker, and launches the web server

set -e

echo "[STARTUP] Current Time: $(date)"
echo "[STARTUP] Running database migrations..."
alembic upgrade head

echo "[STARTUP] Seeding test data..."
python backend/scripts/seed_test_data.py || echo "[STARTUP] Warning: Failed to seed test data (may already exist)"

echo "[STARTUP] Starting Celery worker with auto-scaling..."

# Dynamic concurrency based on CPU cores
# Default: use number of CPU cores available
# Can be overridden with WORKER_CONCURRENCY environment variable
if [ -z "$WORKER_CONCURRENCY" ]; then
    WORKER_CONCURRENCY=$(nproc)
    echo "[STARTUP] Auto-detected $WORKER_CONCURRENCY CPU cores"
fi

# Max concurrency for autoscaling (default: 2x base concurrency)
WORKER_MAX_CONCURRENCY=${WORKER_MAX_CONCURRENCY:-$((WORKER_CONCURRENCY * 2))}

# Log configuration
echo "[STARTUP] Worker concurrency: $WORKER_CONCURRENCY (autoscale up to $WORKER_MAX_CONCURRENCY)"

# Start Celery worker with auto-scaling and Beat scheduler
# --autoscale: Dynamically adjust workers based on queue depth
# --max-tasks-per-child: Restart workers after N tasks (prevents memory leaks)
# -B: Include Beat scheduler for periodic tasks
celery -A backend.app.worker worker -B \
  --loglevel=info \
  --concurrency=$WORKER_CONCURRENCY \
  --autoscale=$WORKER_MAX_CONCURRENCY,$WORKER_CONCURRENCY \
  --max-tasks-per-child=100 \
  --time-limit=3600 \
  --soft-time-limit=3300 &

WORKER_PID=$!
echo "[STARTUP] Celery worker started with PID $WORKER_PID"
echo "[STARTUP] Concurrency: $WORKER_CONCURRENCY (scales to $WORKER_MAX_CONCURRENCY)"

# Wait a moment
sleep 2

echo "[STARTUP] Starting Hypercorn server on port 8080..."
exec hypercorn backend.app.main:app --bind 0.0.0.0:8080
