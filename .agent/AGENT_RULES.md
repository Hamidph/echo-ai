# Echo AI - Agent Collaboration Rules

> **ALL AI AGENTS MUST READ THIS FILE BEFORE MAKING ANY CHANGES**

## 1. Project Overview

Echo AI is a **Visibility Intelligence Platform** that tracks brand presence across AI search engines (OpenAI, Anthropic Claude, Perplexity) using Monte Carlo simulations.

### Architecture
```
/backend/          # Python 3.14 + FastAPI + SQLAlchemy (Async)
/frontend/         # Next.js 14 (App Router) + TypeScript
/alembic/          # Database migrations
/.agent/           # Agent collaboration docs (YOU ARE HERE)
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Pydantic, Celery + Redis
- **Frontend**: Next.js 14, React Query, Tailwind CSS
- **Database**: PostgreSQL (Railway)
- **Deployment**: Railway (monolithic deployment)

---

## 2. Critical Rules

### 2.1 Frontend/Backend Separation
- **NEVER** mix frontend and backend code
- Backend API: `/backend/app/routers/` → defines endpoints
- Frontend API: `/frontend/src/lib/api.ts` → calls endpoints
- Keep business logic in `/backend/app/services/`

### 2.2 No Dummy Data
- NEVER commit placeholder or test data to main branch
- Use real tier values from `/backend/app/services/billing.py`
- Test data scripts stay in `/backend/scripts/` (dev only)

### 2.3 Documentation Updates
When modifying code, you MUST update:
- `AI_HANDOFF_CONTEXT.md` - Session handoff notes
- Route changes → update backend router or frontend page

---

## 3. Code Standards

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

## 4. Key File Locations

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


## 6. Common Tasks

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

## 7. Environment Variables

### Backend (Required)
```bash
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
PERPLEXITY_API_KEY=...
STRIPE_API_KEY=...
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Local only
```

---

## 8. Testing

```bash
# Backend
uv run pytest tests/

# Frontend
cd frontend && npm test
```

---

## 9. Deployment

Single Railway service deployment:
1. Push to `main` branch
2. Railway auto-deploys
3. Verify: `curl https://echo-ai-production.up.railway.app/health`
