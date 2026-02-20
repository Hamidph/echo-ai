# Echo AI Codebase Audit - AI SEO & AI Visibility
**Date:** 2026-02-20  
**Type:** Codebase + Product Readiness Audit  
**Status:** Action Required  
**Author:** GPT-5.3 Codex (Cursor Cloud Agent)

---

## Executive Summary

Echo AI has a strong core concept (Monte Carlo-based AI visibility analytics), but the current codebase has multiple regressions in auth flows, billing/UI contract alignment, and experiment lifecycle reliability.  
For an AI SEO startup, these issues are high risk because they directly affect onboarding conversion, trust in reported metrics, and platform reliability.

**Overall readiness score:** **58/100**  
**Primary concern:** Product-market narrative is strong, but core execution paths are currently brittle.

---

## Scope

- Backend: FastAPI, Celery worker, repositories, schemas, security, billing, demo
- Frontend: Next.js app routing, auth/session handling, experiment/billing/API-key UX
- DevOps: Docker/startup workflow, CI gates
- AI SEO posture: crawlability/discoverability metadata and machine-readable presence

---

## Findings (Prioritized)

### P0 - Critical

#### 1) Email verification and password reset flows are functionally broken
**Evidence**
- `backend/app/core/security.py:106` sets token type to `"access"` inside `create_access_token`.
- `backend/app/services/email.py:139-142` and `173-176` attempt to create `"email_verification"` / `"password_reset"` tokens via `create_access_token`.
- `backend/app/routers/auth.py:295-299` and `408-412` expect token types `"email_verification"` / `"password_reset"`.

**Impact**
- Verification/reset links are invalid by design.
- New-user trust and account recovery are compromised.

---

#### 2) Failure-path quota refund and status update logic can break on missing repository module
**Evidence**
- `backend/app/worker.py:358` imports `backend.app.repositories.user_repo.UserRepository`, but `backend/app/repositories/user_repo.py` does not exist.
- `_refund_user_quota` is called by `_mark_experiment_failed_internal` (`worker.py:401-403`).

**Impact**
- On worker failure, experiment status updates/refunds can fail unpredictably.
- Users may lose quota and see stale "running" experiments.

---

#### 3) Frontend/backend auth and billing contracts are inconsistent in production paths
**Evidence**
- Token key mismatch:
  - `frontend/src/hooks/useAuth.ts:22` stores `localStorage["token"]`
  - `frontend/src/app/dashboard/billing/page.tsx:103` reads `localStorage["access_token"]`
  - `frontend/src/app/dashboard/api-keys/page.tsx:29` reads `localStorage["access_token"]`
- Billing response mismatch:
  - Frontend expects `checkout_url` / `portal_url` (`billing/page.tsx:157`, `182`)
  - Backend returns `url` (`backend/app/routers/billing.py:45-53`, `122`)
- API key payload mismatch:
  - Frontend expects `data.api_key` and `key_prefix` (`api-keys/page.tsx:65`, `215`)
  - Backend returns `key` and `prefix` (`backend/app/schemas/auth.py:77-80`, `94`)

**Impact**
- Core account/billing/API-key workflows degrade or fail.
- Revenue path and developer adoption are directly affected.

---

### P1 - High

#### 4) Build quality gates are disabled for frontend production builds
**Evidence**
- `frontend/next.config.js:11-16`
  - `typescript.ignoreBuildErrors = true`
  - `eslint.ignoreDuringBuilds = true`

**Impact**
- Broken type/lint states can deploy to production silently.
- High risk of runtime regressions under rapid startup iteration.

---

#### 5) Demo endpoint likely returns misleading zero-value metrics
**Evidence**
- Demo reads metrics using `analysis_result.raw_metrics.get(demo_req.target_brand, {})` (`backend/app/routers/demo.py:101`).
- Analyzer outputs metrics under keys like `target_visibility`, `share_of_voice`, `consistency` (`backend/app/builders/analysis.py:632+`), not brand-name root keys.

**Impact**
- Public demo can under-report visibility and misrepresent product value.
- Damages trust during acquisition/sales demos.

---

#### 6) DemoUsage model has no Alembic migration
**Evidence**
- Model exists: `backend/app/models/demo.py`
- No `demo_usage` references found in `alembic/versions/*.py`.

**Impact**
- Demo write path may fail in environments relying strictly on migrations.

---

#### 7) Auth router error logging references undefined logger
**Evidence**
- `backend/app/routers/auth.py:91`, `332`, `390` use `logger.error(...)`
- No `logger = logging.getLogger(__name__)` in file.

**Impact**
- Error paths can throw secondary exceptions, masking root cause.

---

### P2 - Medium

#### 8) Refresh token endpoint contract is inconsistent with frontend usage
**Evidence**
- Backend refresh handler expects a bare `refresh_token: str` parameter (`backend/app/routers/auth.py:143`), interpreted as query/form unless explicit body model.
- Frontend sends JSON `{ refresh_token: ... }` (`frontend/src/lib/api.ts:98`).

**Impact**
- Refresh flow is unreliable/not wired end-to-end.

---

#### 9) Recurring experiments are marketed in UI but not captured in create schema
**Evidence**
- Frontend sends `is_recurring` and `frequency` (`frontend/src/app/experiments/new/page.tsx:106-108`).
- `backend/app/schemas/experiment.py` has no such fields in `ExperimentRequest`.

**Impact**
- Product promise mismatch ("recurring monitoring") vs persisted execution behavior.

---

#### 10) AI SEO technical posture is weak for a visibility-first brand
**Evidence**
- No `robots.ts`, no `sitemap.ts`, no `frontend/public/robots.txt`.
- Only one basic metadata declaration in `frontend/src/app/layout.tsx:16-20`.
- No JSON-LD structured data discovered in frontend app.

**Impact**
- Lower crawl clarity and weaker AI/citation discoverability footprint.
- Strategic contradiction for an AI visibility company.

---

#### 11) CI does not enforce reliability gates
**Evidence**
- `pytest` and `mypy` are `continue-on-error: true` in `.github/workflows/ci-cd.yml:46` and `50`.
- No frontend lint/test/typecheck job in CI workflow.

**Impact**
- Regressions can merge undetected.

---

#### 12) Documentation drift creates operational confusion
**Evidence**
- Root `README.md` references GCP/Vercel deployment while runtime/rules indicate Railway monolith.
- `AI_HANDOFF_CONTEXT.md` contains stale architecture and pricing statements.

**Impact**
- Slower onboarding, inconsistent execution across team/agents.

---

## Recommendations

### 0-72 Hours (Stabilization)
1. Fix token type handling for verification/reset flows.
2. Repair worker refund path (add user repository or inline safe update logic).
3. Standardize frontend auth token storage keys and API response parsing.
4. Re-enable frontend build gates (TS + ESLint) in production builds.

### Week 1 (Revenue + Trust)
1. Fix billing/API-key page contracts (payload and response field alignment).
2. Correct demo metrics mapping + add migration for `demo_usage`.
3. Add end-to-end auth tests: register -> verify -> login -> refresh -> reset-password.

### Week 2 (AI SEO & Visibility Credibility)
1. Add `robots.ts` and `sitemap.ts` in Next.js app.
2. Add route-level metadata (title/description/openGraph/twitter/canonical).
3. Publish structured data (`SoftwareApplication`, `Organization`, `FAQ`) on marketing pages.
4. Add machine-readable discovery files (`llms.txt` / `ai.txt` style policy page) and citation guidance pages.

### Ongoing (Engineering Hygiene)
1. Make CI fail on mypy/pytest/lint regressions.
2. Add frontend CI jobs (lint, typecheck, test).
3. Keep handoff/docs synchronized with actual deployment target and product behavior.

---

## Next Steps

1. Execute P0 fixes in a single stabilization sprint branch.
2. Add smoke tests for billing + API-key + experiment create/detail flows.
3. Run a follow-up audit after fixes and publish a "v2 readiness score".

