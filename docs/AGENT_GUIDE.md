# AGENT_GUIDE.md

## Overview
This document serves as a comprehensive guide for AI agents and developers working on the **Echo AI** codebase. It covers the project structure, development workflows, and deployment instructions.

## 🏗 Project Structure
The project is a monorepo containing both the backend and frontend.

```
ai-visibility/
├── backend/                 # FastAPI (Python 3.11)
│   ├── app/
│   │   ├── main.py          # Entry point & CORS config
│   │   ├── core/config.py   # Settings & Env Vars (CRITICAL)
│   │   ├── models/          # SQLAlchemy Models
│   │   └── routers/         # API Endpoints
│   └── scripts/             # Utility scripts (create_test_user.py)
├── frontend/                # Next.js 14 (TypeScript)
│   ├── src/app/             # App Router pages
│   │   ├── page.tsx         # Landing Page
│   │   └── dashboard/       # Dashboard routes
│   └── next.config.js       # Next.js config (Strict TS checks disabled)
├── migrations/              # Alembic migrations (Python)
└── Dockerfile               # Production Dockerfile for Backend
```

## 🛠 Tech Stack
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL, Redis, Celery.
- **Frontend**: Next.js 14, Tailwind CSS, TypeScript, TanStack Query.
- **Package Manager**: `uv` (Python), `npm` (Node.js).
- **Deployment**: Railway (Backend + DB), Vercel (Frontend).

## 💻 Development Workflow

### Backend
The backend uses `uv` for fast dependency management.
```bash
cd backend
# Run server
uv run uvicorn app.main:app --reload
```
**Key Configuration**: `backend/app/core/config.py` handles all environment variables. Warning: `database_url_sync` has custom logic to fix Railway connection strings.

### Frontend
The frontend is a standard Next.js app.
```bash
cd frontend
npm run dev
```
**Note**: TypeScript strict mode is currently disabled in `next.config.js` (`ignoreBuildErrors: true`) to facilitate rapid deployment. Future agents should aim to fix type errors in `src/app/experiments/*`.

## 🚀 Deployment Instructions

### Backend (Railway)
The backend is deployed on Railway.
```bash
# Deploy changes
railway up --service echo-ai

# View logs
railway logs --service echo-ai
```
**Important**: 
- `UV_LINK_MODE=copy` is set in the Dockerfile to prevent symlink issues.
- `FRONTEND_URL` env var must be set in Railway to allow CORS from Vercel.

### Frontend (Vercel)
The frontend is deployed on Vercel.
```bash
cd frontend
# Deploy to production
vercel --prod
```

## ⚠️ Known Gotchas & "To-Dos"
1.  **Strict Type Checking**: Currently disabled in frontend build.
2.  **Root Redirect**: Backend redirects root `/` to `/api/v1/docs`. Defined in `backend/app/main.py`.
3.  **Redis Health**: Health check might warn about Redis if connection is flaky, but app defaults to degraded mode safely.
4.  **Test User**: `test@echoai.com` / `password123`.

## 📝 Common Tasks

### How to Edit the Website Text
1.  Open `frontend/src/app/page.tsx` (Landing Page).
2.  Modify the text inside the JSX.
3.  Run `npm run dev` to preview.
4.  Deploy with `vercel --prod`.

### How to Add a New API Endpoint
1.  Create a new router file in `backend/app/routers/`.
2.  Register the router in `backend/app/main.py`.
3.  Use `alembic` for any DB schema changes.
