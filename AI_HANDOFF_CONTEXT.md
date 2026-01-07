# Echo AI - Handoff Context (January 6, 2026)

## Project Overview
**Echo AI** is a "Visibility Intelligence Platform" that tracks brand presence across LLM search engines (Perplexity, ChatGPT, Claude) using Monte Carlo simulations (50-100 iterations per prompt).

## Architecture Stack
- **Backend**: Python 3.14, FastAPI, SQLAlchemy (Async), Pydantic.
- **Async Worker**: Celery + Redis (for handling long-running experiments).
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, TypeScript.
- **Database**: PostgreSQL (Railway).
- **Deployment**: Railway (Service `echo-ai`, linked to `main` branch).

## Recent Work (Completed)
### 1. Audit Fixes (Security & Reliability)
- **CRIT-1**: Fixed authorization gap in `get_experiment`.
- **CRIT-2**: Implemented quota refunds on task failure.
- **CRIT-3**: Fixed DB connection leaks in `worker.py` (engine disposal).
- **Compliance**: Enforced secure `SECRET_KEY` usage.

### 2. UI/UX Polish
- **Mobile Menu**: Added "Settings" link.
- **Dashboard**: Fixed hydration issues and implemented lazy loading for charts.
- **Bug Fix**: `RecommendedPrompts` now correctly auto-fills the prompt on the "New Experiment" page (using URL query params).

### 3. Productization Features (Implemented but Disabled)
We recently implemented the following features to enable a public demo and health monitoring:
- **Public Demo Endpoint**: `POST /api/v1/demo/quick-analysis` (5 iter limit, rate-limited).
- **Detailed Health Check**: `GET /api/v1/health/detailed` (DB/Redis status).
- **Analytics**: `DemoUsage` model created `backend/app/models/demo.py`.
- **Documentation**: `docs/PRODUCT.md`.

**⚠️ Important State Note**:
The routers for these features (`backend/app/routers/demo.py` and `backend/app/routers/health.py`) exist and are verified by tests (`backend/tests/test_productization.py`). However, **they are currently NOT registered** in `backend/app/main.py`. The wiring was reverted in the last step.

## Next Steps for Incoming Agent
1.  **Re-enable Routers**: Uncomment/add the `demo_router` and `health_router` inclusions in `backend/app/main.py` when ready to go live with Phase 2.
2.  **Verify Deployment**: Ensure `railway.json` is configured (if needed) or rely on the `Procfile`/`railway.toml` equivalent. (Note: `railway.json` was deleted by the user).
3.  **Frontend Integration**: The backend demo endpoint is ready, but the Frontend "Try Demo" button needs to be connected to `POST /api/v1/demo/quick-analysis`.

## Key Files
- `backend/app/main.py`: Entry point (needs router wiring).
- `backend/app/worker.py`: Core experiment logic.
- `backend/app/routers/demo.py`: New demo logic (sync execution).
- `backend/tests/test_productization.py`: Verification tests for new features.
