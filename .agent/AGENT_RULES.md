# Echo AI - Agent Collaboration Rules

> **🚨 ALL AI AGENTS MUST READ THIS FILE BEFORE MAKING ANY CHANGES 🚨**
> 
> **Last Updated:** January 15, 2026  
> **Version:** 2.0  
> **Status:** Production Deployed

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Critical Rules](#2-critical-rules)
3. [Documentation Standards](#3-documentation-standards)
4. [Code Standards](#4-code-standards)
5. [Deployment Information](#5-deployment-information)
6. [Session End Protocol](#6-session-end-protocol)
7. [Common Tasks](#7-common-tasks)
8. [File Locations](#8-file-locations)

---

## 1. Project Overview

### What is Echo AI?
Echo AI is a **Visibility Intelligence Platform** that tracks brand presence across AI search engines (ChatGPT, Claude, Perplexity) using Monte Carlo simulations (50-100 iterations per query) to provide statistically valid visibility metrics.

### Production Status
- **Deployed:** ✅ Yes (Railway)
- **Domain:** https://echoai.uk
- **Environment:** Production
- **Version:** 0.1.0
- **Last Deploy:** January 15, 2026

### Architecture
```
/backend/          # Python 3.11 + FastAPI + SQLAlchemy (Async)
/frontend/         # Next.js 14 (App Router) + TypeScript
/alembic/          # Database migrations
/.agent/           # Agent collaboration docs (YOU ARE HERE)
  /audits/         # Production audits and reports (dated)
  AGENT_RULES.md   # THIS FILE - Central source of truth
  HANDOFF.md       # Session-to-session handoff
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Pydantic V2, Celery + Redis
- **Frontend**: Next.js 14, TanStack Query, Tailwind CSS, TypeScript
- **Database**: PostgreSQL 15 (Railway managed)
- **Cache/Queue**: Redis 7 (Railway managed)
- **Deployment**: Railway (monolithic: API + Worker + Frontend)
- **Server**: Hypercorn (ASGI)
- **Domain**: echoai.uk (Railway custom domain)

---

## 2. Critical Rules

### 🚨 2.1 Documentation is Sacred
**EVERY agent MUST follow these documentation rules:**

#### Central Documentation Files (DO NOT CREATE NEW ONES)
1. **`.agent/AGENT_RULES.md`** (THIS FILE) - Central source of truth
   - Project overview, deployment info, tech stack
   - Rules, standards, protocols
   - Update when: Architecture changes, new deployment info, new rules
   
2. **`.agent/HANDOFF.md`** - Session-to-session handoff
   - What you did this session
   - Files modified
   - Next steps for future agent
   - Update: EVERY session end (MANDATORY)
   
3. **`AI_HANDOFF_CONTEXT.md`** - Historical context
   - Major features/changes log
   - Known issues
   - Update: When adding significant features

4. **`README.md`** - Public-facing documentation
   - Installation, usage, API docs
   - Update: When user-facing features change

#### Audit Reports & Analysis (DATED FORMAT)
- **Location:** `.agent/audits/YYYY-MM-DD_description.md`
- **Format:** `2026-01-15_production_readiness.md`
- **When to create:** Security audits, production readiness checks, major analysis
- **Never create:** Random markdown files in root directory

#### ❌ FORBIDDEN
- **DO NOT** create random markdown files in project root
- **DO NOT** create duplicate documentation
- **DO NOT** create files without consulting existing structure
- **DO NOT** skip updating HANDOFF.md at session end

### 2.2 Frontend/Backend Separation
- **NEVER** mix frontend and backend code
- Backend API: `/backend/app/routers/` → defines endpoints
- Frontend API: `/frontend/src/lib/api.ts` → calls endpoints
- Keep business logic in `/backend/app/services/`

### 2.3 No Dummy Data in Production
- NEVER commit placeholder or test data to main branch
- Use real tier values from `/backend/app/services/billing.py`
- Test data scripts stay in `/backend/scripts/` (dev only)
- Seed script only runs when `ENVIRONMENT != production`

### 2.4 Logging Standards
- **NEVER** use `print()` statements in backend code
- **ALWAYS** use `logger.info()`, `logger.error()`, etc.
- Import: `import logging; logger = logging.getLogger(__name__)`
- Production logs must be structured for monitoring

---

## 3. Documentation Standards

### 3.1 When to Update Documentation

| Change Type | Update AGENT_RULES.md | Update HANDOFF.md | Update AI_HANDOFF_CONTEXT.md | Update README.md |
|-------------|----------------------|-------------------|------------------------------|------------------|
| New deployment info | ✅ Yes | No | No | No |
| New architecture pattern | ✅ Yes | No | Maybe | No |
| Session work | No | ✅ Yes (MANDATORY) | Maybe | No |
| Major feature | No | ✅ Yes | ✅ Yes | Maybe |
| User-facing change | No | ✅ Yes | No | ✅ Yes |
| Bug fix | No | ✅ Yes | No | No |

### 3.2 Audit Report Format

When creating audit reports in `.agent/audits/`:

```markdown
# [Report Title]
**Date:** YYYY-MM-DD  
**Type:** [Security Audit / Production Readiness / Performance Analysis]  
**Status:** [In Progress / Complete / Action Required]  
**Author:** [Agent Name]

---

## Executive Summary
[2-3 sentences]

## Findings
[Detailed findings]

## Recommendations
[Actionable items]

## Next Steps
[What needs to happen]
```

### 3.3 Commit Message Format

```bash
<type>: <short description>

- Detailed point 1
- Detailed point 2

[Optional: Breaking changes, migration notes]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`

---

## 4. Code Standards

### Backend (Python)
```python
# Imports: stdlib → third-party → local
from datetime import datetime
from fastapi import APIRouter, Depends
from backend.app.core.database import DbSession

# Type hints required
async def get_user(user_id: UUID, session: DbSession) -> User:
    ...

# Docstrings for public functions
"""
Brief description.

Args:
    user_id: The user's UUID.
    
Returns:
    User object.
"""
```

### Frontend (TypeScript)
```typescript
// Component structure
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function ComponentName() {
  // hooks first
  // derived state
  // handlers
  // render
}
```

---

## 8. Key File Locations

| Purpose | Backend | Frontend |
|---------|---------|----------|
| API Routes | `/backend/app/routers/` | - |
| API Client | - | `/frontend/src/lib/api.ts` |
| Pages | - | `/frontend/src/app/` |
| Components | - | `/frontend/src/components/` |
| Database Models | `/backend/app/models/` | - |
| Schemas | `/backend/app/schemas/` | - |
| Config | `/backend/app/core/config.py` | `/frontend/.env.local` |

---

## 5. Session End Protocol (MANDATORY)

> **EVERY agent session MUST end with documentation updates**

### Step 1: Update `.agent/HANDOFF.md`

Replace the content with current session info:

```markdown
# Echo AI - Agent Handoff Context

> **Last Updated**: [DATE]
> **Session**: [Brief description of what you worked on]

---

## Current System State: [✅ WORKING / ⚠️ PARTIAL / ❌ BROKEN]

[One sentence about overall status]

---

## What I Did This Session

- [Change 1]
- [Change 2]
- [Change 3]

---

## Files Modified

| File | Change |
|------|--------|
| `path/to/file1.py` | [Brief description] |
| `path/to/file2.tsx` | [Brief description] |

---

## Next Steps for Future Agent

1. [First thing to do]
2. [Second thing to do]
3. [Third thing to do]

---

## Known Issues

[List any bugs or issues, or "None currently"]

---

## Warnings / Gotchas

[Any critical context the next agent needs to know]
```

### Step 2: Update `AI_HANDOFF_CONTEXT.md`

Add a new section at the top of "Latest Updates":

```markdown
### ✅ [Feature/Task Name] (January XX, 2026)
- **What**: Brief description of what was done
- **Files**: List key files modified
- **Status**: Working/Testing/Needs attention
- **Notes**: Any important context
```

### Step 3: Commit Your Changes

```bash
git add -A
git commit -m "feat: [description of changes]

- [bullet point 1]
- [bullet point 2]

Co-authored-by: [Agent Name]"
```

---

## 7. Common Tasks

### Adding a New API Endpoint
1. Create/modify router in `/backend/app/routers/`
2. Add schema in `/backend/app/schemas/`
3. Register router in `/backend/app/main.py`
4. Add client method in `/frontend/src/lib/api.ts`

### Adding a New Page
1. Create page in `/frontend/src/app/[route]/page.tsx`
2. Add navigation link if needed in `/frontend/src/components/Navbar.tsx`

### Database Changes
1. Modify model in `/backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

---

## 9. Testing

```bash
# Backend
uv run pytest tests/

# Frontend
cd frontend && npm test
```

---

## 10. Quick Reference

### Health Checks
```bash
# Production
curl https://echoai.uk/health

# Local
curl http://localhost:8000/health
```

### Railway Commands
```bash
railway logs --tail 100          # View logs
railway restart                  # Restart service
railway variables list           # List env vars
railway run alembic upgrade head # Run migrations
railway rollback                 # Rollback deployment
```

### Git Workflow
```bash
git status                       # Check status
git add .                        # Stage changes
git commit -m "type: message"    # Commit
git push origin main             # Deploy to production
```

---

## 11. Emergency Procedures

### Site is Down
1. Check Railway status: https://railway.app/status
2. Check logs: `railway logs --tail 100`
3. Check health: `curl https://echoai.uk/health`
4. Restart: `railway restart`
5. Rollback if needed: `railway rollback`

### Database Issues
1. Check connections: `railway run psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"`
2. Check slow queries in Railway dashboard
3. Run migrations if needed: `railway run alembic upgrade head`

### Worker Issues
1. Check Celery logs in Railway
2. Restart service: `railway restart`
3. Check Redis: `railway run redis-cli ping`
4. Reduce concurrency if OOM: Set `CELERY_CONCURRENCY=2`

---

## 12. Contact & Support

- **Railway Support:** https://railway.app/help
- **Sentry (Errors):** https://sentry.io (when configured)
- **Repository:** https://github.com/Hamidph/echo-ai
- **Domain:** https://echoai.uk

---

**🚨 REMEMBER: Update `.agent/HANDOFF.md` at the end of EVERY session! 🚨**

---

---

## 5. Deployment Information

### Production Environment
- **Platform:** Railway
- **Domain:** https://echoai.uk
- **Service Name:** echo-ai
- **Branch:** main (auto-deploy enabled)
- **Health Check:** https://echoai.uk/health
- **API Docs:** https://echoai.uk/api/v1/docs

### Railway Configuration
```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Environment Variables (Production)
**Required:**
- `ENVIRONMENT=production`
- `SECRET_KEY` (32+ chars)
- `DATABASE_URL` (auto-provided by Railway)
- `REDIS_URL` (auto-provided by Railway)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `FRONTEND_URL=https://echoai.uk`

**Optional:**
- `SENTRY_DSN` (error tracking)
- `STRIPE_API_KEY` (billing)
- `SMTP_*` (email)
- `CELERY_CONCURRENCY=4` (worker threads)

### Deployment Process
1. **Commit changes:** `git commit -m "feat: description"`
2. **Push to main:** `git push origin main`
3. **Railway auto-deploys** (2-5 minutes)
4. **Verify health:** `curl https://echoai.uk/health`
5. **Check logs:** `railway logs --tail 100`

### Rollback Procedure
```bash
# If deployment breaks:
railway rollback

# Or deploy specific commit:
git revert HEAD
git push origin main
```

### Database Migrations
```bash
# Migrations run automatically on deploy via start.sh
# Manual run if needed:
railway run alembic upgrade head
```

---

## 6. Session End Protocol (MANDATORY)

> **🚨 EVERY agent session MUST end with documentation updates 🚨**

### Step 1: Update `.agent/HANDOFF.md` (REQUIRED)

Replace the entire content with:

```markdown
# Echo AI - Agent Handoff Context

> **Last Updated**: January XX, 2026  
> **Session**: [Brief description of what you worked on]

---

## Current System State: [✅ WORKING / ⚠️ PARTIAL / ❌ BROKEN]

[One sentence about overall status]

---

## What I Did This Session

- [Change 1]
- [Change 2]
- [Change 3]

---

## Files Modified

| File | Change |
|------|--------|
| `path/to/file1.py` | [Brief description] |
| `path/to/file2.tsx` | [Brief description] |

---

## Next Steps for Future Agent

1. [First thing to do]
2. [Second thing to do]
3. [Third thing to do]

---

## Known Issues

[List any bugs or issues, or "None currently"]

---

## Warnings / Gotchas

[Any critical context the next agent needs to know]
```

### Step 2: Update `AI_HANDOFF_CONTEXT.md` (If Significant)

Add a new section at the top of "Latest Updates" if you made significant changes:

```markdown
### ✅ [Feature/Task Name] (January XX, 2026)
- **What**: Brief description of what was done
- **Files**: List key files modified
- **Status**: Working/Testing/Needs attention
- **Notes**: Any important context
```

### Step 3: Update This File (If Needed)

Update `.agent/AGENT_RULES.md` if you:
- Changed deployment configuration
- Added new architecture patterns
- Discovered new rules that should be followed
- Updated environment variables

### Step 4: Commit Your Changes

```bash
git add -A
git commit -m "feat: [description of changes]

- [bullet point 1]
- [bullet point 2]

Updated: HANDOFF.md with session notes"
```

---

## 7. Common Tasks
