# 🤖 AI AGENT CONTEXT & HANDOFF GUIDE

**Purpose:** This file provides context for AI agents (Cursor, Claude, ChatGPT, etc.) working on this project  
**Last Updated:** January 3, 2026  
**Project:** Echo AI - AI Search Analytics Platform  
**Owner:** Hamid  
**Current Status:** Production-ready, deployed on Railway

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Architecture & Tech Stack](#architecture--tech-stack)
3. [Development History](#development-history)
4. [Deployment Status](#deployment-status)
5. [Code Conventions](#code-conventions)
6. [Common Tasks](#common-tasks)
7. [Known Issues & Workarounds](#known-issues--workarounds)
8. [Future Roadmap](#future-roadmap)
9. [Quick Reference](#quick-reference)

---

## 📖 PROJECT OVERVIEW

### What This Project Does

**Echo AI** is a SaaS platform that measures brand visibility on AI-powered search engines (ChatGPT, Perplexity, Claude) using Monte Carlo simulation and statistical analysis.

**Core Innovation:** Instead of single queries, we run probabilistic experiments (N iterations) to provide statistically significant metrics on brand mentions, positioning, and sentiment.

### Business Model

- **FREE:** 100 prompts/month
- **STARTER:** $49/mo - 5,000 prompts
- **PRO:** $199/mo - 50,000 prompts
- **ENTERPRISE:** Custom pricing - 1M+ prompts

### Key Differentiators

1. **Monte Carlo simulation** for statistical rigor
2. **Multi-provider support** (OpenAI, Anthropic, Perplexity)
3. **Real-time analysis** with confidence intervals
4. **Production-grade** infrastructure from day 1

---

## 🏗️ ARCHITECTURE & TECH STACK

### Backend (FastAPI + Python 3.11+)

```
backend/
├── app/
│   ├── core/              # Configuration, database, security
│   ├── models/            # SQLAlchemy ORM models
│   ├── routers/           # API endpoints
│   ├── schemas/           # Pydantic request/response models
│   ├── services/          # Business logic (billing, email)
│   ├── builders/          # LLM providers, runner, analysis
│   ├── repositories/      # Data access layer
│   └── worker.py          # Celery background tasks
```

**Key Libraries:**
- FastAPI 0.115+ (async web framework)
- SQLAlchemy 2.0 (async ORM)
- Pydantic V2 (validation)
- Celery (background jobs)
- Stripe (payments)
- OpenAI, Anthropic, httpx (LLM providers)

### Frontend (Next.js 14 + TypeScript)

```
frontend/src/
├── app/                   # Next.js App Router
│   ├── (auth)/           # Login, Register
│   ├── dashboard/        # Main dashboard
│   ├── experiments/      # Experiment management
│   └── settings/         # User settings
├── components/           # React components
├── hooks/               # Custom React hooks
├── lib/                 # API client, utilities
└── types/               # TypeScript definitions
```

**Key Libraries:**
- Next.js 14 (App Router)
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- Zustand (state management)
- Recharts (visualizations)

### Infrastructure

**Production (Railway):**
- PostgreSQL 15 (managed database)
- Redis 7 (caching + Celery broker)
- Docker containers (API + Worker)
- Auto-scaling enabled

**Frontend (Vercel):**
- Next.js 14 deployment
- Global CDN
- Automatic HTTPS

---

## 📚 DEVELOPMENT HISTORY

### Phase 1: Initial Development (Dec 2024)
- Built core probabilistic engine
- Implemented LLM provider adapters
- Created statistical analysis module
- Set up FastAPI backend
- Developed Next.js frontend

### Phase 2: Production Hardening (Dec 2024)
- Added authentication (JWT + API keys)
- Implemented user management
- Created Stripe billing integration
- Added email verification system
- Set up Celery for background jobs

### Phase 3: Security Audit (Jan 2, 2026)
**CRITICAL:** Fixed 25 security issues

Key fixes:
- Event loop recreation in Celery worker
- Semaphore race conditions
- Quota bypass vulnerabilities
- Transaction integrity issues
- Authentication bypass on GET endpoints
- Statistical calculation errors

**Status:** ALL 25 ISSUES FIXED ✅

See `AUDIT_FIXES_SUMMARY.md` for details.

### Phase 4: Railway Deployment Prep (Jan 3, 2026)
**CRITICAL:** Made production-ready for Railway

Changes:
- Added `DATABASE_URL`/`REDIS_URL` env var support
- Updated Dockerfile for dynamic `$PORT`
- Replaced all `print()` with proper logging
- Fixed CORS configuration
- Created `railway.json`
- Committed `uv.lock` for reproducible builds

**Status:** PRODUCTION READY ✅

See `PRODUCTION_READY.md` for details.

---

## 🚀 DEPLOYMENT STATUS

### Current Environment

**Platform:** Railway.app  
**Branch:** `claude/analyze-codebase-A9hr5`  
**Last Deploy:** [To be deployed]  
**Status:** Ready for deployment

### Environment Variables

**Required for Railway:**
```bash
# Auto-set by Railway
DATABASE_URL=postgresql://...     # Railway PostgreSQL
REDIS_URL=redis://...             # Railway Redis
PORT=8080                         # Dynamic port

# Must be set manually
SECRET_KEY=<32-char-hex>          # openssl rand -hex 32
ENVIRONMENT=production
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...       # Optional
FRONTEND_URL=https://your-frontend.vercel.app

# Optional (deferred)
STRIPE_API_KEY=sk_live_...        # For billing
STRIPE_WEBHOOK_SECRET=whsec_...   # For webhooks
SMTP_HOST=smtp.sendgrid.net       # For email
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxx            # SendGrid API key
FROM_EMAIL=noreply@domain.com
SENTRY_DSN=https://...@sentry.io  # For error tracking
```

### Deployment Commands

```bash
# Deploy to Railway
railway up

# Run migrations
railway run alembic upgrade head

# View logs
railway logs --follow

# Get URL
railway domain
```

**Full Guide:** See `RAILWAY_DEPLOYMENT.md`

---

## 💻 CODE CONVENTIONS

### Python Style

**Package Manager:** `uv` (NOT pip, poetry, or conda)

```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Install from lock file
uv sync

# Run commands
uv run python script.py
uv run pytest
```

**Code Style:**
- **Linter:** Ruff (configured in `pyproject.toml`)
- **Type Checker:** mypy (strict mode)
- **Formatter:** Ruff (line length: 100)
- **Docstrings:** Google style with type hints

**Critical Rules:**
1. ✅ Use `logger.*()` NOT `print()`
2. ✅ Always type-hint function signatures
3. ✅ Use async/await for I/O operations
4. ✅ Pydantic models for all API schemas
5. ✅ SQLAlchemy async for database queries

### TypeScript/React Style

**Package Manager:** `pnpm` (NOT npm or yarn)

```bash
# Add dependency
pnpm add package-name

# Add dev dependency
pnpm add -D package-name

# Install from lock file
pnpm install

# Run dev server
pnpm run dev
```

**Code Style:**
- **Framework:** Next.js 14 App Router
- **Styling:** Tailwind CSS (utility-first)
- **State:** TanStack Query + Zustand
- **Types:** Strict TypeScript

### Git Conventions

**Commit Message Format:**
```
<type>: <short description>

<detailed explanation>

<breaking changes if any>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code restructuring
- `perf:` - Performance improvement
- `test:` - Tests
- `chore:` - Build/tooling changes

**Branch Naming:**
- `main` - Production
- `claude/feature-name` - AI agent work
- `feature/feature-name` - Human work
- `fix/bug-name` - Bug fixes

---

## 🛠️ COMMON TASKS

### Task 1: Add a New LLM Provider

**Files to modify:**
1. `backend/app/schemas/llm.py` - Add provider to enum
2. `backend/app/builders/providers.py` - Create new provider class
3. `backend/app/core/config.py` - Add API key field

**Example:**
```python
# In providers.py
class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com"
        
    async def _make_request(self, request: LLMRequest) -> dict[str, Any]:
        # Implementation here
        pass
```

### Task 2: Add a New API Endpoint

**Files to modify:**
1. `backend/app/routers/` - Create/modify router
2. `backend/app/schemas/` - Add request/response models
3. `backend/app/repositories/` - Add database queries if needed

**Example:**
```python
# In routers/experiments.py
@router.get("/experiments/stats")
@limiter.limit("10/minute")
async def get_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: DbSession,
) -> StatsResponse:
    # Implementation
    pass
```

### Task 3: Add a Database Migration

```bash
# Create migration
uv run alembic revision -m "add_new_column"

# Edit the file in alembic/versions/
# Add upgrade() and downgrade() logic

# Test locally
uv run alembic upgrade head

# Deploy to Railway
railway run alembic upgrade head
```

### Task 4: Update Frontend Component

**Location:** `frontend/src/components/`

**Pattern:**
```typescript
"use client"; // For client components

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ["key"],
    queryFn: () => api.getData(),
  });
  
  if (isLoading) return <div>Loading...</div>;
  
  return <div>{data}</div>;
}
```

### Task 5: Debug Production Issues

```bash
# View Railway logs
railway logs --tail 100

# View specific service logs
railway logs --service api --follow

# Check environment variables
railway variables list

# Connect to PostgreSQL
railway run psql $DATABASE_URL

# Test Redis connection
railway run python -c "from backend.app.core.redis import check_redis_health; import asyncio; print(asyncio.run(check_redis_health()))"
```

---

## ⚠️ KNOWN ISSUES & WORKAROUNDS

### Issue 1: Stripe Price IDs are Placeholders

**File:** `backend/app/services/billing.py:24-29`

**Status:** Deferred until after investor feedback

**Workaround:** Currently using placeholder strings. When ready:
1. Create products in Stripe Dashboard
2. Copy real price IDs (format: `price_xxxxx`)
3. Update `PRICE_IDS` dictionary

### Issue 2: Email Service Not Configured

**Status:** Working demo email available, production SendGrid deferred

**Workaround:** 
- For demo: Use existing SMTP credentials
- For production: Sign up for SendGrid, add API key to Railway

### Issue 3: No Sentry Error Tracking

**Status:** SDK integrated, DSN not configured

**Workaround:**
```bash
# When ready, just add:
railway variables set SENTRY_DSN="https://...@sentry.io/..."
railway restart
```

### Issue 4: Frontend TODO on Dashboard

**File:** `frontend/src/app/dashboard/page.tsx:50`

**Status:** FIXED ✅
 
**Impact:** Dashboard now shows real-time aggregated metrics and visualizations.
 
**Fix:** Implemented `dashboardApi.getStats()` and visualization components.

---

## 🗺️ FUTURE ROADMAP

### Immediate (Post-Launch)
- [ ] Configure Stripe products and price IDs
- [ ] Set up SendGrid for production email
- [ ] Add Sentry error tracking
- [x] Implement aggregated dashboard metrics
- [ ] Write integration tests for billing

### Short-Term (1-2 Months)
- [ ] Add more LLM providers (Google Gemini, Mistral)
- [ ] Implement competitor comparison reports
- [ ] Add email alerts for visibility drops
- [ ] Zapier integration
- [ ] API rate limiting per pricing tier

### Medium-Term (3-6 Months)
- [ ] White-label option for agencies
- [ ] Team collaboration features
- [ ] Enterprise SSO (SAML)
- [ ] Custom domain support
- [ ] Advanced analytics dashboard

### Long-Term (6-12 Months)
- [ ] Mobile app (React Native)
- [ ] AI-powered insights and recommendations
- [ ] Predictive analytics
- [ ] Multi-language support
- [ ] Partner API program

---

## 📖 QUICK REFERENCE

### Important Files

**Documentation:**
- `README.md` - Project overview
- `RAILWAY_DEPLOYMENT.md` - Deployment guide
- `PRODUCTION_READY.md` - Current status
- `AUDIT_FIXES_SUMMARY.md` - Security audit results
- `IMPLEMENTATION_REPORT.md` - Technical deep-dive
- `AI_AGENT_CONTEXT.md` - This file

**Configuration:**
- `pyproject.toml` - Python dependencies
- `uv.lock` - Dependency lock file (COMMITTED)
- `alembic.ini` - Database migration config
- `railway.json` - Railway deployment config
- `Dockerfile` - Production container
- `docker-compose.yml` - Local development

**Entry Points:**
- `backend/app/main.py` - FastAPI application
- `backend/app/worker.py` - Celery worker
- `frontend/src/app/layout.tsx` - Next.js root layout

### Key Environment Variables

**Backend:**
- `DATABASE_URL` - PostgreSQL connection (Railway auto-sets)
- `REDIS_URL` - Redis connection (Railway auto-sets)
- `SECRET_KEY` - JWT signing key (MUST SET)
- `ENVIRONMENT` - dev/staging/production
- `OPENAI_API_KEY` - OpenAI API key
- `FRONTEND_URL` - CORS origin

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Stripe public key

### Useful Commands

```bash
# Backend
uv sync                          # Install dependencies
uv run pytest                    # Run tests
uv run alembic upgrade head      # Run migrations
uv run uvicorn backend.app.main:app --reload  # Dev server

# Frontend
pnpm install                     # Install dependencies
pnpm run dev                     # Dev server
pnpm run build                   # Production build

# Database
railway run psql $DATABASE_URL   # Connect to PostgreSQL
railway run alembic upgrade head # Run migrations

# Docker
docker compose up -d             # Start local services
docker compose down              # Stop local services
docker build -t api .            # Build API image

# Git
git status                       # Check status
git add -A                       # Stage all changes
git commit -m "message"          # Commit
git push origin branch-name      # Push to remote
```

### API Endpoints

**Health & Docs:**
- `GET /health` - Health check
- `GET /api/v1/docs` - Swagger UI
- `GET /metrics` - Prometheus metrics

**Authentication:**
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/api-keys` - Create API key

**Experiments:**
- `POST /api/v1/experiments` - Create experiment
- `GET /api/v1/experiments` - List experiments
- `GET /api/v1/experiments/{id}` - Get experiment
- `GET /api/v1/experiments/{id}/detail` - Detailed results
- `GET /api/v1/experiments/{id}/report` - Visibility report

**Billing:**
- `POST /api/v1/billing/checkout` - Create checkout
- `POST /api/v1/billing/portal` - Billing portal
- `GET /api/v1/billing/usage` - Usage stats
- `POST /api/v1/billing/webhook` - Stripe webhook

---

## 🎯 AGENT-SPECIFIC GUIDANCE

### For Railway Management Agent

**Your Role:** Manage Railway deployment and infrastructure

**Key Files:**
- `RAILWAY_DEPLOYMENT.md` - Your primary guide
- `railway.json` - Railway configuration
- `Dockerfile` - Container definition

**Common Tasks:**
1. Deploy: `railway up`
2. Migrations: `railway run alembic upgrade head`
3. Logs: `railway logs --follow`
4. Env vars: `railway variables set KEY=VALUE`
5. Restart: `railway restart`

**Environment Variables You Manage:**
- All variables in "Deployment Status" section above
- Never commit secrets to git
- Use Railway dashboard for sensitive values

### For Frontend Development Agent

**Your Role:** Build and maintain Next.js frontend

**Key Files:**
- `frontend/src/app/` - All pages
- `frontend/src/components/` - Reusable components
- `frontend/src/lib/api.ts` - API client

**Package Manager:** ALWAYS use `pnpm` (not npm or yarn)

**Common Tasks:**
1. Add component: Create in `components/`
2. Add page: Create in `app/`
3. API call: Use TanStack Query
4. Styling: Use Tailwind classes
5. Deploy: Push to Vercel

### For Backend Development Agent

**Your Role:** Build and maintain FastAPI backend

**Key Files:**
- `backend/app/routers/` - API endpoints
- `backend/app/builders/` - Core business logic
- `backend/app/models/` - Database models

**Package Manager:** ALWAYS use `uv` (not pip, poetry, or conda)

**Common Tasks:**
1. Add endpoint: Create in `routers/`
2. Add model: Create in `models/`
3. Migration: `uv run alembic revision -m "name"`
4. Tests: `uv run pytest`
5. Logs: Use `logger.*()` NOT `print()`

### For Testing Agent

**Your Role:** Write and maintain tests

**Key Files:**
- `tests/` - Test suite
- `tests/conftest.py` - Test fixtures

**Test Coverage Goal:** 80%+

**Current Coverage:** ~15% (only auth tests exist)

**Priority Tests Needed:**
1. Billing webhooks
2. Quota enforcement
3. Experiment execution
4. Statistical analysis
5. LLM provider integration

### For Security Audit Agent

**Your Role:** Review code for security issues

**Reference:** `AUDIT_FIXES_SUMMARY.md` - Previous audit results

**Focus Areas:**
1. Authentication bypass
2. Authorization issues
3. SQL injection risks
4. XSS vulnerabilities
5. Rate limiting
6. Input validation
7. Secret management

**All 25 previous issues are FIXED** ✅

### For Documentation Agent

**Your Role:** Maintain and improve documentation

**Key Files:**
- All `.md` files in root directory
- Code docstrings (Google style)
- API documentation (FastAPI auto-generates)

**Documentation Standards:**
- Clear, concise language
- Code examples for complex features
- Keep this file (AI_AGENT_CONTEXT.md) updated
- Update after major changes

---

## 🚨 CRITICAL WARNINGS

### ❌ NEVER DO THESE

1. **Don't use pip/npm/yarn** - Use `uv` and `pnpm` only
2. **Don't hardcode secrets** - Use environment variables
3. **Don't skip migrations** - Always run on deploy
4. **Don't use print()** - Use `logger.*()` instead
5. **Don't commit .env** - It's in `.gitignore`
6. **Don't modify uv.lock manually** - Use `uv` commands
7. **Don't skip tests** - Run before committing
8. **Don't bypass rate limiting** - Security feature
9. **Don't skip security validation** - Always validate input
10. **Don't force push to main** - Use pull requests

### ✅ ALWAYS DO THESE

1. **Read this file first** - Before starting work
2. **Check git status** - Know what changed
3. **Run tests** - Before committing
4. **Check linters** - Fix errors before commit
5. **Update documentation** - Keep in sync with code
6. **Use type hints** - Python and TypeScript
7. **Log errors properly** - With context and exc_info
8. **Test locally** - Before deploying
9. **Review changes** - Use `git diff`
10. **Update this file** - After major changes

---

## 📝 CHANGE LOG FOR AGENTS

### Version 1.0 (Jan 3, 2026)
- Initial creation of AI_AGENT_CONTEXT.md
- Documented entire project history
- Added deployment instructions
- Created agent-specific guidance

### Future Updates

When you make major changes, add them here:

```
### Version X.X (Date)
- What changed
- Why it changed
- Impact on other agents
- New conventions if any
```

---

## 🤝 COLLABORATION GUIDELINES

### Working with Other Agents

1. **Read this file first** - Every time you start a new conversation
2. **Check recent commits** - See what changed
3. **Update this file** - After major changes
4. **Leave clear comments** - For next agent
5. **Document decisions** - Why, not just what

### Handoff Checklist

Before ending your session:
- [ ] Code is committed
- [ ] Tests pass
- [ ] Documentation updated
- [ ] This file updated if needed
- [ ] No uncommitted secrets
- [ ] Railway deployment working (if modified)
- [ ] Clear notes for next agent

### Communication Format

When leaving notes for next agent:

```
## 🔴 URGENT for Next Agent
[Critical items that need immediate attention]

## 📌 Context
[What you were working on]

## ✅ Completed
[What you finished]

## ⏸️ In Progress
[What you started but didn't finish]

## 🐛 Known Issues
[New issues discovered]

## 💡 Recommendations
[Suggestions for next agent]
```

---

## 📞 GETTING HELP

### When Stuck

1. **Read the docs** - Check relevant .md files
2. **Check git history** - `git log --oneline`
3. **View recent changes** - `git diff HEAD~5`
4. **Check Railway logs** - `railway logs`
5. **Review this file** - Look for similar tasks
6. **Check code comments** - Developers left notes

### Resources

**Project Documentation:**
- This file (AI_AGENT_CONTEXT.md)
- RAILWAY_DEPLOYMENT.md
- PRODUCTION_READY.md
- AUDIT_FIXES_SUMMARY.md

**External Documentation:**
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs
- Railway: https://docs.railway.app
- Pydantic: https://docs.pydantic.dev
- SQLAlchemy: https://docs.sqlalchemy.org

**Package Managers:**
- uv: https://github.com/astral-sh/uv
- pnpm: https://pnpm.io

---

## ✅ VERIFICATION CHECKLIST

Before claiming "task complete", verify:

### Code Quality
- [ ] No `print()` statements (use `logger.*()`)
- [ ] All functions have type hints
- [ ] Docstrings for public functions
- [ ] No hardcoded secrets
- [ ] No TODO comments without issues

### Testing
- [ ] Existing tests still pass
- [ ] New features have tests
- [ ] Manual testing completed
- [ ] Edge cases considered

### Documentation
- [ ] Code comments where needed
- [ ] API docs updated (if API changed)
- [ ] README updated (if user-facing)
- [ ] This file updated (if major change)

### Deployment
- [ ] Works locally
- [ ] Railway deployment successful
- [ ] Migrations run successfully
- [ ] No new linter errors
- [ ] Health check passes

### Security
- [ ] Input validation added
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Rate limiting considered
- [ ] No SQL injection risks

---

## 🎓 PROJECT-SPECIFIC KNOWLEDGE

### Why We Use Monte Carlo Simulation

Traditional SEO tools check rankings once. But AI responses are **non-deterministic** - the same query gives different results each time.

Our solution: Run the same query N times (10-100 iterations), then calculate:
- **Visibility Rate:** % of responses mentioning the brand
- **Average Position:** Where the brand appears on average
- **Confidence Intervals:** Statistical confidence (95% level)
- **Consistency Score:** How reliably brand appears

This gives clients **statistically rigorous** insights, not guesswork.

### Why We Support Multiple LLM Providers

Different AI tools give different results:
- ChatGPT (OpenAI) - Most popular
- Perplexity - Citation-focused
- Claude (Anthropic) - Long-form responses

Clients need to know: "Where does my brand appear across ALL AI search engines?"

### Why Railway Over GCP/AWS

**Decision rationale:**
- **Speed:** 15-minute deployment vs 2 hours
- **Cost:** $31/month vs $50-100/month
- **Simplicity:** Single platform vs multi-service orchestration
- **Scaling:** Automatic, built-in
- **Developer UX:** Excellent

**When to migrate:** When revenue > $5K/month or users > 10K

### Why This Tech Stack

**Backend (FastAPI):**
- Async-first (handles concurrent LLM calls)
- Auto-generated OpenAPI docs
- Pydantic validation
- Fast (Rust-based)

**Frontend (Next.js 14):**
- Server-side rendering
- App Router (modern pattern)
- Vercel deployment (free)
- TypeScript (type safety)

**Database (PostgreSQL):**
- JSONB for experiment results
- Full-text search
- Robust transactions
- Industry standard

**Task Queue (Celery + Redis):**
- Async experiment execution
- Retry logic
- Monitoring support
- Battle-tested

---

## 🎯 SUCCESS METRICS

### Technical Metrics
- **Uptime:** 99.9%+ (Railway SLA)
- **Response Time:** <200ms p95 for API
- **Test Coverage:** 80%+ (current: 15%)
- **Deployment Time:** <5 minutes
- **Mean Time to Recovery:** <10 minutes

### Business Metrics
- **Monthly Recurring Revenue:** Target $50K
- **Customer Acquisition Cost:** <$200
- **Lifetime Value:** >$2,000
- **Churn Rate:** <5% monthly
- **Net Promoter Score:** >40

### Product Metrics
- **Daily Active Users:** Target 1,000
- **Experiments per User:** Target 10/month
- **Conversion to Paid:** Target 5%
- **Feature Adoption:** Target 70%
- **Support Tickets:** <2% of users/month

---

## 🏁 FINAL NOTES

### Project Philosophy

1. **Ship fast, iterate faster**
2. **Production-ready from day 1**
3. **Investor-grade quality**
4. **Statistical rigor**
5. **Developer experience matters**

### Owner's Preferences (Hamid)

- **Package Managers:** uv (Python), pnpm (Node.js), Homebrew (system)
- **Code Style:** Clean, well-documented, type-safe
- **Deployment:** Railway (for now)
- **Communication:** Detailed explanations, show reasoning
- **Documentation:** Comprehensive, updated regularly

### This File's Purpose

This document is the **institutional memory** of the project. When context limits are hit or new AI agents join, they should:

1. Read this file **first**
2. Check recent git commits
3. Review relevant documentation
4. Start working

**Keep this file updated!** It's the bridge between AI agent sessions.

---

## 📜 VERSION HISTORY

**v1.0** (Jan 3, 2026) - Initial creation  
- Complete project documentation
- Agent-specific guidance
- Deployment instructions
- Code conventions
- Known issues

**Next Version:** [Your updates here]

---

**🤖 Welcome, AI Agent! You're now fully briefed on the Echo AI project.**

**Current Status:** Production-ready, awaiting Railway deployment  
**Your Mission:** Build features, fix bugs, improve the platform  
**Your Guide:** This file + project documentation

**Good luck! 🚀**

---

*Last updated by: Claude (Anthropic) - Jan 3, 2026*  
*Next agent: Please update this file after major changes*

