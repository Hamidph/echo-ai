# Deployment Guide

The application is deployed as a single consolidated service on **Railway**.

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (Static Export), served by FastAPI at root `/`.
- **Database**: PostgreSQL (Railway)
- **Queue**: Redis + Celery (Railway)

## How to Deploy
Run the automated deployment script:

```bash
./complete_deployment.sh
```

This script will:
1. Link to your Railway project.
2. Set necessary environment variables (including `FRONTEND_URL` and `NEXT_PUBLIC_API_URL` for consistency).
3. Trigger a build from GitHub.
4. Run database migrations (`alembic upgrade head`).

## Manual Steps (if needed)
If you need to deploy manually via CLI:

```bash
railway up
railway run alembic upgrade head
```

## Environment Variables
Ensure the following are set in Railway:
- `JWT_SECRET`, `SECRET_KEY`: Security keys.
- `DATABASE_URL`: Auto-set by Railway Postgres.
- `REDIS_URL`: Auto-set by Railway Redis.
- `FRONTEND_URL`: `https://<your-app>.up.railway.app`
- `NEXT_PUBLIC_API_URL`: `https://<your-app>.up.railway.app` (Baked into Docker image during build, but good to have in env for reference).

## troubleshooting
- **Health Check**: `curl https://<your-app>.up.railway.app/health`
- **Logs**: `railway logs`
