# Echo AI — Project Brain

> Read this file at the start of every session.

## What We Build

AI Search Analytics Platform that measures brand visibility across LLM-powered
search engines (ChatGPT, Perplexity, Claude) using Monte Carlo simulations
(10–100 iterations per prompt).

## Load the Plugin Every Session

```bash
claude --plugin-dir ./echo-ai-plugin
```

Skills: `/echo-ai-tools:deploy` `/echo-ai-tools:commit` `/echo-ai-tools:review-pr`
`/echo-ai-tools:debug` `/echo-ai-tools:test` `/echo-ai-tools:release`
`/echo-ai-tools:db-query` `/echo-ai-tools:experiment-report`
`/echo-ai-tools:content-brief` `/echo-ai-tools:launch-post`
`/echo-ai-tools:customer-email` `/echo-ai-tools:competitor-analysis`
`/echo-ai-tools:sprint-plan` `/echo-ai-tools:standup`
`/echo-ai-tools:pricing-review` `/echo-ai-tools:onboarding-doc`
`/echo-ai-tools:api-docs` `/echo-ai-tools:bug-report` `/echo-ai-tools:changelog`

## Quick Start

| Task | Command |
|---|---|
| Start backend | `cd backend && uvicorn main:app --reload` |
| Start frontend | `cd frontend && npm run dev` |
| Run all tests | `cd backend && python -m pytest tests/ -v` |
| DB migrate | `railway run python -m alembic upgrade head` |
| Deploy | `/echo-ai-tools:deploy` — NEVER deploy manually |
| View Railway logs | `railway logs --tail 50` |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + SQLAlchemy 2.0 + Alembic |
| Background Jobs | Celery + Redis |
| Database | PostgreSQL (Railway) |
| Frontend | Next.js 14 App Router + TypeScript + TanStack Query |
| Styling | Tailwind CSS + Recharts |
| Payments | Stripe (subscriptions + webhooks) |
| LLM Providers | OpenAI GPT-4, Anthropic Claude 4.5, Perplexity Sonar |
| Infra | Railway (all services) |
| Auth | JWT (web) + API keys (API consumers) |
| CI/CD | GitHub Actions (lint + build) |

## Metrics We Track

| Metric | Definition |
|---|---|
| Visibility Rate | % of LLM responses mentioning the brand |
| Share of Voice | Brand mentions ÷ (brand + competitor mentions) |
| Average Position | Ordinal position of first brand mention |
| Consistency Score | Std deviation across Monte Carlo iterations |
| Sentiment | Positive / neutral / negative classification |
| Hallucination Rate | % of mentions with factual errors |
| First Mention Rate | % of responses where brand appears first |

## Pricing

| Plan | Price | Prompts/mo |
|---|---|---|
| FREE | £0 | 3 |
| STARTER | £35 | 10 |
| PRO | £55 | 15 |
| ENTERPRISE | £169 | 50 |
| ENTERPRISE+ | £599 | 200 |

## Target Customers

- SEO agencies selling AIO (AI Optimization) services to clients
- Brand managers at mid-market companies
- PR professionals tracking brand narrative in AI responses
- SaaS founders monitoring product visibility in AI search

## Competitors

Profound · Peec.ai · Otterly.ai · Goodie.ai · Share of Model

## Repository Structure

```
backend/
  api/          FastAPI routers
  models/       SQLAlchemy 2.0 models
  services/     Business logic
  workers/      Celery tasks (experiment execution)
  db/           Migrations and session management
frontend/
  app/          Next.js App Router pages
  components/   React components
  lib/          API client, auth helpers
echo-ai-plugin/ Claude Code plugin (skills, agents, hooks, MCP)
```

## Coding Standards

- **Python**: ruff formatting, type hints everywhere, SQLAlchemy 2.0 style
- **TypeScript**: working toward strict mode — enable file by file
- **API responses**: always `{success: bool, data?: any, error?: string}`
- **HTTP status**: 200 success · 400 validation · 401 auth · 402 quota · 500 error
- **DB queries**: parameterized only, always paginate (default 20, max 100)
- **Commits**: conventional format `type(scope): description`
- **Never commit**: .env · secrets · __pycache__ · node_modules · .DS_Store

## Commit Scopes

`api` · `frontend` · `db` · `auth` · `billing` · `experiments` · `workers` · `infra` · `skills`

## Git Workflow

- Active branch: `claude/startup-improvement-plan-WOC5X`
- Never push to main directly — always use PRs
- Deploy only via `/echo-ai-tools:deploy` skill

## Known Issues (fix as you go)

- CSV exports timeout for large result sets (>10k rows)
- TypeScript strict mode disabled — enable file by file when touching components
- Test coverage is thin — add tests alongside every new feature
- Email verification slow in staging (Mailgun rate limiting)

## Current Sprint

> Update this section every Monday

- [ ] (fill in current sprint goals)

## MCP Servers Connected

- GitHub (`claude mcp auth github` if not authenticated)
- Notion (`claude mcp auth notion`)
- Sentry (`claude mcp auth sentry`)
- Stripe (`claude mcp auth stripe`)
- PostgreSQL (via Railway DATABASE_URL)
