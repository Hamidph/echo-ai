---
name: deploy
description: >
  This skill provides context for Echo AI's deployment process to Railway production.
  It should be used when the user mentions "deploy", "ship to prod", "release to production",
  "push live", "go live", or discusses deployment readiness. Covers pre-flight checks,
  Railway deployment, DB migrations, health verification, and rollback procedures.
---

# Echo AI Deployment Knowledge

## Deployment Architecture
- **Platform**: Railway (backend + frontend + PostgreSQL + Redis)
- **Backend**: FastAPI Docker container
- **Frontend**: Next.js Docker container
- **DB migrations**: Alembic via `railway run`

## Pre-flight Requirements
- All tests passing (backend pytest + frontend type-check + build)
- No uncommitted changes
- On correct branch: `claude/startup-improvement-plan-WOC5X`
- Latest code pulled from origin

## Deploy Commands
- Backend: `railway up --service backend`
- Frontend: `railway up --service frontend`
- Migrations: `railway run python -m alembic upgrade head`

## Health Verification
- Endpoint: `https://api.echo-ai.com/health`
- Check Railway logs: `railway logs --tail 30 --service backend`
- Confirm ~~billing webhooks active

## Rollback
- `railway rollback` if health check fails
- Check ~~error monitor for new exceptions post-deploy

## Critical Rules
- NEVER deploy without passing tests
- ALWAYS confirm with user before deploying
- ALWAYS run migrations after backend deploy
- ALWAYS verify health after deploy
