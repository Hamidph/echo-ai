---
name: deploy
description: Deploy Echo AI to Railway production. Use when user says "deploy", "ship to prod", "release to production", "push live", or "go live". Runs tests, builds Docker images, deploys backend and frontend, runs migrations, verifies health.
disable-model-invocation: true
---

# Deploy to Production

STOP — confirm with user before each phase.

### Phase 1: Pre-flight
1. Check for uncommitted changes: `git status`
2. Confirm on correct branch: `git branch --show-current`
3. Pull latest: `git pull origin claude/startup-improvement-plan-WOC5X`
4. Run backend tests: `cd backend && python -m pytest tests/ -q`
5. Run frontend build: `cd frontend && npm run build`

STOP if tests fail. Do not deploy broken code.

### Phase 2: Deploy
6. Deploy backend: `railway up --service backend`
7. Deploy frontend: `railway up --service frontend`
8. Run DB migrations: `railway run python -m alembic upgrade head`

### Phase 3: Verify
9. Health check: `curl -s https://api.echo-ai.com/health | python3 -m json.tool`
10. Check Railway logs: `railway logs --tail 30 --service backend`
11. Confirm Stripe webhooks active in Stripe dashboard

STOP if health check fails. Roll back: `railway rollback`.

Report status clearly after each phase.
