# Echo AI - Handoff Context (January 7, 2026)

## Project Overview
**Echo AI** is a "Visibility Intelligence Platform" that tracks brand presence across LLM search engines (Perplexity, ChatGPT, Claude) using Monte Carlo simulations (50-100 iterations per prompt).

## Architecture Stack
- **Backend**: Python 3.14, FastAPI, SQLAlchemy (Async), Pydantic.
- **Async Worker**: Celery + Redis (for handling long-running experiments).
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, TypeScript.
- **Database**: PostgreSQL (Railway).
- **Deployment**: Railway (Service `echo-ai`, linked to `main` branch).
- **Server**: Hypercorn (ASGI server) on port 8080.

## Current System Status (January 7, 2026)

### ✅ WORKING SYSTEMS
1. **Railway Deployment**: 
   - URL: https://echo-ai-production.up.railway.app
   - Health endpoint: `/health` returns `{"status":"healthy","version":"1.0.0","environment":"production","services":{"redis":"healthy","database":"healthy"}}`
   - API docs available at: `/api/v1/docs`
   - Frontend serving: Static Next.js export is being served correctly from backend
   - Landing page, dashboard, and all routes are accessible

2. **Database & Redis**:
   - PostgreSQL: ✅ Healthy
   - Redis: ✅ Healthy
   - Environment variables properly configured on Railway

3. **Frontend Static Export**:
   - Successfully built and exported to `frontend/out/`
   - Being served by FastAPI backend
   - All pages (landing, login, register, dashboard, experiments, settings) are accessible

4. **Routers Enabled**:
   - ✅ Demo router (`/api/v1/demo/*`) is REGISTERED in `backend/app/main.py`
   - ✅ Health router (`/api/v1/health/*`) is REGISTERED in `backend/app/main.py`
   - ✅ Auth, Billing, Experiments routers all working

### ⚠️ KNOWN ISSUES

#### Issue #1: Scheduler Task Error (Non-Critical)
**Status**: Fixed in code, but NOT YET DEPLOYED to Railway

**Error in Production Logs**:
```
[2026-01-06 23:37:05,231: ERROR/ForkPoolWorker-2] Error checking scheduled experiments: name 'selectinload' is not defined
```

**Root Cause**: 
- The deployed code on Railway is from commit `dd4f57d` or earlier
- The fix was committed in `68436a1` (fix(scheduler): fix NameError by importing selectinload and restoring logic)
- Railway auto-deploys from `main` branch, but the latest commits haven't been deployed yet

**Fix Applied Locally** (commit 68436a1):
- File: `backend/app/tasks/scheduler.py`
- Added import: `from sqlalchemy.orm import selectinload`
- Import already exists on line 10 of the local file

**Impact**: 
- Low priority - only affects recurring experiments (hourly scheduled task)
- Experiments triggered manually work perfectly
- The error is caught and logged, doesn't crash the worker

**Action Required**: 
- Railway needs to redeploy from latest `main` branch to pick up the fix
- Command: `railway up` or trigger redeploy via Railway dashboard
- The fix is already committed and pushed to GitHub

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

### 3. Productization Features (NOW ENABLED)
- **Public Demo Endpoint**: `POST /api/v1/demo/quick-analysis` (5 iter limit, rate-limited) - ✅ REGISTERED
- **Detailed Health Check**: `GET /api/v1/health/detailed` (DB/Redis status) - ✅ REGISTERED
- **Analytics**: `DemoUsage` model created `backend/app/models/demo.py`.
- **Documentation**: `docs/PRODUCT.md`.

**Status Update**: The routers are NOW REGISTERED in `backend/app/main.py` (lines 215-225).

## Deployment Configuration

### Railway Service: `echo-ai`
- **Project**: refreshing-exploration
- **Environment**: production
- **Domain**: https://echo-ai-production.up.railway.app
- **Startup Script**: `start.sh`
- **Server**: Hypercorn (not Uvicorn)
- **Port**: 8080
- **Auto-deploy**: Enabled from `main` branch

### Environment Variables (Verified on Railway):
- `DATABASE_URL`: ✅ Configured
- `REDIS_URL`: ✅ Configured
- `SECRET_KEY`: ✅ Configured (secure)
- `JWT_SECRET`: ✅ Configured
- `FRONTEND_URL`: ✅ Set to https://echo-ai-production.up.railway.app
- `STRIPE_SECRET_KEY`: ✅ Configured (test mode)
- `STRIPE_WEBHOOK_SECRET`: ✅ Configured

### Startup Process (from `start.sh`):
1. Run Alembic migrations: `alembic upgrade head`
2. Start Celery worker with Beat scheduler (concurrency=2)
3. Start Hypercorn server on port 8080

## Git Status
- **Current Branch**: `main`
- **Status**: Clean working tree, up to date with `origin/main`
- **Latest Commits**:
  - `32bf47b` - chore(docs): enforce strict documentation/handoff rules
  - `68436a1` - fix(scheduler): fix NameError by importing selectinload ⚠️ NOT YET DEPLOYED
  - `dd4f57d` - feat(product): enable public demo, analytics, and detailed health check

## Next Steps for Incoming Agent

### Immediate Actions:
1. **Deploy Latest Code to Railway**: 
   - The scheduler fix (commit `68436a1`) needs to be deployed
   - Trigger redeploy via Railway CLI: `railway up` or via Railway dashboard
   - This will eliminate the hourly `NameError` in logs

### Phase 2 (Optional Enhancements):
1. **Frontend Integration**: Connect "Try Demo" button to `POST /api/v1/demo/quick-analysis`
2. **Monitoring**: Set up Sentry for production error tracking (DSN configured)
3. **Documentation**: Update `WEBSITE_SITEMAP.md` if any routes change

## Key Files
- `backend/app/main.py`: Entry point, all routers registered
- `backend/app/worker.py`: Core experiment logic (Celery tasks)
- `backend/app/tasks/scheduler.py`: Recurring experiment scheduler (has fix pending deployment)
- `backend/app/routers/demo.py`: Public demo endpoint
- `backend/app/routers/health.py`: Detailed health check endpoint
- `start.sh`: Monolithic startup script for Railway
- `Dockerfile`: Multi-stage build for production

## Testing Credentials
- **Demo User**: test@echoai.com / password123
- **Health Check**: `curl https://echo-ai-production.up.railway.app/health`
- **API Docs**: https://echo-ai-production.up.railway.app/api/v1/docs

## Important Notes
- ⚠️ TypeScript strict mode is disabled in `next.config.js` (`ignoreBuildErrors: true`)
- ⚠️ The project uses `npm` for frontend (not `pnpm` as per dotfiles preference)
- ✅ All critical systems are operational and healthy
- ✅ The only issue is a non-critical scheduler error that's already fixed in code
