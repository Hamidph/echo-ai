# Echo AI - Prioritized Technical Backlog
**Last Updated:** January 15, 2026
**Total Items:** 12 actionable improvements
**Estimated Total Effort:** 8-10 weeks

---

## Priority Legend

- **P0 (Critical):** Must fix before production launch / enterprise sales. Blocks revenue or poses significant risk.
- **P1 (High):** Should fix in next sprint. Impacts user experience, security, or scalability.
- **P2 (Medium):** Nice-to-have improvements. Schedule based on capacity.

**Effort Scale:**
- 🟢 Small (< 1 day)
- 🟡 Medium (1-3 days)
- 🔴 Large (1-2 weeks)

---

## P0: Critical Issues (Must Fix Immediately)

### **[P0-001] Fix API Key Authentication Timing Attack**
**Severity:** HIGH | **Effort:** 🟡 Medium (2 days) | **Impact:** Security + Performance

**Problem:**
The `get_current_user_from_api_key()` function in `backend/app/core/deps.py:93-101` fetches ALL active API keys and performs bcrypt comparisons on each one. This creates:
1. **Performance issue:** O(n) complexity with number of users (1000 users = 1000 bcrypt ops per request = ~100ms+ latency)
2. **Security issue:** Timing attack vulnerability leaks information about valid key prefixes
3. **Scalability issue:** Does not scale beyond 10K users

**Files to Change:**
- `backend/app/core/deps.py` (auth dependency)
- `backend/app/models/user.py` (add `key_prefix_hash` column)
- `backend/app/routers/auth.py` (API key creation logic)
- `alembic/versions/XXX_add_api_key_prefix_index.py` (new migration)

**Proposed Solution:**

**Option A: Indexed Prefix Lookup (Recommended)**
```python
# Migration: Add indexed prefix column
class APIKey(Base):
    key_prefix_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,  # Fast lookup
        comment="SHA256 hash of first 12 chars for fast lookup"
    )

# Auth logic change
async def get_current_user_from_api_key(api_key: str, db: AsyncSession):
    # Extract prefix (first 12 chars: "sk_live_abc1")
    prefix = api_key[:12]
    prefix_hash = hashlib.sha256(prefix.encode()).hexdigest()

    # Query only matching prefix (single DB query)
    result = await db.execute(
        select(APIKey)
        .where(APIKey.key_prefix_hash == prefix_hash)
        .where(APIKey.is_active == True)
        .limit(10)  # Prevent collision DOS
    )
    api_keys = result.scalars().all()

    # Verify full key (constant-time comparison)
    for key_record in api_keys:
        if verify_api_key(api_key, key_record.key):
            # ... authenticated
```

**Option B: Redis Cache**
```python
# Cache API key -> user_id mapping (30min TTL)
async def get_current_user_from_api_key(api_key: str, db: AsyncSession):
    cache_key = f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()}"

    # Check cache first
    user_id = await redis.get(cache_key)
    if user_id:
        return await get_user_by_id(user_id, db)

    # Fallback to DB (with prefix lookup)
    # ... then cache result
    await redis.setex(cache_key, 1800, str(user.id))
```

**Testing Plan:**
```python
# tests/test_api_key_auth.py
async def test_api_key_performance():
    """Verify auth completes in <10ms with 10K users."""
    # Create 10,000 API keys
    for i in range(10000):
        await create_api_key(user_id=uuid4())

    # Measure auth time
    start = time.time()
    user = await get_current_user_from_api_key("sk_live_test123...", db)
    elapsed = time.time() - start

    assert elapsed < 0.01  # 10ms SLA

async def test_timing_attack_resistance():
    """Verify constant-time verification."""
    valid_key = "sk_live_valid..."
    invalid_key = "sk_live_invalid..."

    # Time should be similar for valid/invalid keys
    valid_time = measure_time(authenticate(valid_key))
    invalid_time = measure_time(authenticate(invalid_key))

    assert abs(valid_time - invalid_time) < 0.001  # <1ms variance
```

**Acceptance Criteria:**
- [ ] API key auth completes in <10ms for 10K users
- [ ] Timing variance <1ms between valid/invalid keys
- [ ] Migration runs successfully on production data
- [ ] Existing API keys continue to work
- [ ] Performance tests added to CI

**Migration/Rollout Plan:**
1. **Phase 1:** Add `key_prefix_hash` column (nullable, no default)
2. **Phase 2:** Backfill existing keys: `UPDATE api_keys SET key_prefix_hash = SHA256(prefix)`
3. **Phase 3:** Deploy new auth logic (falls back to old logic if `key_prefix_hash` NULL)
4. **Phase 4:** Make column non-nullable after verification
5. **Phase 5:** Remove old auth code path

---

### **[P0-002] Implement Data Retention Policy & GDPR Compliance**
**Severity:** HIGH (Legal Risk) | **Effort:** 🟡 Medium (3 days) | **Impact:** Compliance

**Problem:**
1. Raw LLM responses stored indefinitely in `iterations.raw_response` (GDPR violation)
2. Responses may contain PII (names, emails, phone numbers in brand recommendations)
3. No data export/deletion endpoints (GDPR Article 17 - Right to be Forgotten)
4. No user consent tracking for data processing

**Files to Change:**
- `backend/app/models/experiment.py` (add anonymization fields)
- `backend/app/tasks/data_retention.py` (NEW - cleanup task)
- `backend/app/routers/user_data.py` (NEW - GDPR endpoints)
- `backend/app/models/user.py` (add consent fields)
- `alembic/versions/XXX_add_data_retention_fields.py` (migration)

**Proposed Solution:**

```python
# Model changes
class Iteration(Base):
    raw_response: Mapped[str | None]  # Will be set to NULL after retention period
    is_anonymized: Mapped[bool] = mapped_column(default=False)
    anonymized_at: Mapped[datetime | None]

class User(Base):
    privacy_policy_accepted_at: Mapped[datetime | None]
    privacy_policy_version: Mapped[str | None] = mapped_column(default="1.0")
    data_processing_consent: Mapped[bool] = mapped_column(default=False)
    marketing_consent: Mapped[bool] = mapped_column(default=False)

# Scheduled cleanup task
@celery_app.task(name="anonymize_old_iterations")
def anonymize_old_iterations():
    """
    Daily task: Anonymize iteration responses older than 90 days.
    Retains extracted_brands for analytics, removes PII.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

    result = await db.execute(
        update(Iteration)
        .where(Iteration.created_at < cutoff_date)
        .where(Iteration.is_anonymized == False)
        .values(
            raw_response=None,  # Remove PII
            is_anonymized=True,
            anonymized_at=datetime.now(timezone.utc)
        )
    )

    logger.info(f"Anonymized {result.rowcount} old iterations")

# GDPR endpoints
@router.get("/user/data-export")
async def export_user_data(current_user: User, db: DbSession):
    """Export all user data in JSON format (GDPR Article 20)."""
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at,
            "brand_profile": {...},
        },
        "experiments": [...],
        "batch_runs": [...],
        # Exclude raw_response if anonymized
    }

@router.delete("/user/account")
async def delete_user_account(current_user: User, db: DbSession):
    """Delete user account and all associated data (GDPR Article 17)."""
    # Soft delete with 30-day grace period
    current_user.is_active = False
    current_user.scheduled_deletion_at = datetime.now(timezone.utc) + timedelta(days=30)

    # Send confirmation email
    await send_deletion_confirmation_email(current_user.email)

    return {"message": "Account scheduled for deletion in 30 days"}
```

**Retention Policy:**
- **Iterations (raw_response):** 90 days → Anonymize (set to NULL)
- **Extracted brands:** Indefinite (anonymized, no PII)
- **Aggregated metrics:** Indefinite (no PII)
- **User accounts:** Until deletion request + 30 days grace period
- **Audit logs:** 2 years (compliance requirement)

**Testing Plan:**
```python
async def test_data_anonymization():
    """Verify old iterations are anonymized."""
    # Create iteration 91 days old
    old_iteration = await create_iteration(
        raw_response="Contact John Doe at john@example.com",
        created_at=datetime.now(timezone.utc) - timedelta(days=91)
    )

    # Run cleanup task
    await anonymize_old_iterations()

    # Verify anonymization
    await db.refresh(old_iteration)
    assert old_iteration.raw_response is None
    assert old_iteration.is_anonymized == True
    assert old_iteration.extracted_brands is not None  # Preserved

async def test_user_data_export():
    """Verify complete data export."""
    export = await export_user_data(user)
    assert "experiments" in export
    assert "user" in export
    assert export["user"]["email"] == user.email

async def test_account_deletion():
    """Verify account deletion flow."""
    await delete_user_account(user)
    assert user.scheduled_deletion_at is not None
    assert user.is_active == False
```

**Acceptance Criteria:**
- [ ] Iterations anonymized after 90 days automatically
- [ ] Data export endpoint returns complete user data in JSON
- [ ] Account deletion endpoint schedules deletion + sends email
- [ ] Privacy policy acceptance tracked with version
- [ ] Consent fields added to user model
- [ ] Daily cleanup task scheduled in Celery Beat
- [ ] Tests verify anonymization + export + deletion

**Privacy Note:**
This implementation balances data retention for business analytics (aggregated metrics, extracted brands) with user privacy (removing raw PII after 90 days). Users can request full deletion at any time.

---

### **[P0-003] Add Comprehensive Test Suite (80%+ Coverage)**
**Severity:** HIGH | **Effort:** 🔴 Large (2 weeks) | **Impact:** Quality + Confidence

**Problem:**
- Current test coverage: <20% (estimated)
- CI marked as `continue-on-error: true` (tests don't block deployment)
- No integration tests, no E2E tests
- Missing critical flow coverage (experiment execution, LLM provider mocking, Celery tasks)

**Files to Change:**
- `.github/workflows/ci-cd.yml` (enforce test passing)
- `tests/unit/` (NEW - unit tests organized by module)
- `tests/integration/` (NEW - API integration tests)
- `tests/e2e/` (NEW - end-to-end scenarios)
- `conftest.py` (enhance fixtures)

**Test Structure:**

```
tests/
├── unit/                   # Fast, isolated tests
│   ├── test_auth.py       # JWT, password hashing
│   ├── test_models.py     # SQLAlchemy models
│   ├── test_schemas.py    # Pydantic validation
│   ├── test_security.py   # Security utilities
│   └── test_analysis.py   # Analytics calculations
├── integration/            # API tests with test DB
│   ├── test_experiments_api.py
│   ├── test_auth_api.py
│   ├── test_billing_api.py
│   └── test_dashboard_api.py
├── e2e/                    # End-to-end scenarios
│   ├── test_experiment_flow.py
│   ├── test_recurring_experiments.py
│   └── test_quota_enforcement.py
├── fixtures/               # Test data
│   ├── users.py
│   ├── experiments.py
│   └── mock_llm_responses.py
└── conftest.py             # Shared fixtures

```

**Key Tests to Add:**

**1. End-to-End Experiment Flow:**
```python
# tests/e2e/test_experiment_flow.py
@pytest.mark.e2e
async def test_complete_experiment_lifecycle(client, test_user, mock_openai):
    """Test: Create experiment → Execute → Analyze → View results."""

    # Step 1: Create experiment
    response = await client.post(
        "/api/v1/experiments",
        json={
            "prompt": "Best CRM for startups",
            "target_brand": "TestBrand",
            "competitor_brands": ["Salesforce", "HubSpot"],
            "iterations": 10,
            "config": {"providers": ["openai"], "model": "gpt-4o"}
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 202
    experiment_id = response.json()["experiment_id"]
    job_id = response.json()["job_id"]

    # Step 2: Wait for execution (mock Celery task)
    await wait_for_experiment_completion(experiment_id, timeout=30)

    # Step 3: Verify results
    response = await client.get(
        f"/api/v1/experiments/{experiment_id}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["batch_runs"]) == 1
    assert data["batch_runs"][0]["metrics"]["visibility_rate"] > 0

    # Step 4: Verify dashboard update
    response = await client.get(
        "/api/v1/dashboard/stats",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    assert response.json()["total_experiments"] >= 1
```

**2. Security Tests:**
```python
# tests/integration/test_security.py
async def test_jwt_expiration():
    """Verify expired tokens are rejected."""
    expired_token = create_access_token(
        {"user_id": str(uuid4())},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    response = await client.get(
        "/api/v1/experiments",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

async def test_api_key_rate_limiting():
    """Verify rate limits enforced per API key."""
    # Make 11 requests (limit is 10/minute)
    for i in range(11):
        response = await client.post(
            "/api/v1/experiments",
            json={...},
            headers={"X-API-Key": test_api_key}
        )

    # 11th request should be rate limited
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

async def test_authorization_prevents_cross_user_access():
    """Verify users cannot access other users' data."""
    # User A creates experiment
    exp_id = await create_experiment(user_a)

    # User B tries to access it
    response = await client.get(
        f"/api/v1/experiments/{exp_id}",
        headers={"Authorization": f"Bearer {user_b.token}"}
    )
    assert response.status_code == 403
```

**3. Celery Task Tests:**
```python
# tests/unit/test_worker.py
@pytest.mark.celery
async def test_experiment_execution_task(mock_openai):
    """Test execute_experiment_task with mocked LLM."""
    experiment_id = await create_test_experiment()

    # Execute task synchronously (test mode)
    result = execute_experiment_task.apply(
        args=[str(experiment_id), "openai"],
        kwargs={"model": "gpt-4o"}
    )

    assert result.successful()
    assert result.result["status"] == "completed"
    assert result.result["total_iterations"] == 10

async def test_quota_refund_on_failure():
    """Verify quota refunded when experiment fails."""
    user = await create_user(prompts_used_this_month=5)
    experiment_id = await create_experiment(user_id=user.id)

    # Simulate task failure
    with pytest.raises(OpenAIError):
        await execute_experiment_task(str(experiment_id), "openai")

    # Verify quota refunded
    await db.refresh(user)
    assert user.prompts_used_this_month == 5  # Restored
```

**4. Performance Tests:**
```python
# tests/performance/test_api_latency.py
@pytest.mark.performance
async def test_api_latency_requirements():
    """Verify p95 latency <200ms for CRUD operations."""
    latencies = []

    for i in range(100):
        start = time.time()
        response = await client.get("/api/v1/experiments")
        latencies.append(time.time() - start)

    p95 = np.percentile(latencies, 95)
    assert p95 < 0.2  # 200ms SLA
```

**CI Configuration Changes:**
```yaml
# .github/workflows/ci-cd.yml
- name: Run pytest
  run: |
    uv run pytest tests/ \
      -v \
      --cov=backend \
      --cov-report=xml \
      --cov-report=term \
      --cov-fail-under=80  # FAIL if coverage <80%
  # Remove: continue-on-error: true

- name: Run integration tests
  run: |
    docker-compose -f docker-compose.test.yml up -d
    uv run pytest tests/integration/ -v
    docker-compose -f docker-compose.test.yml down

- name: Run E2E tests
  run: |
    uv run pytest tests/e2e/ -v --headed=false
```

**Acceptance Criteria:**
- [ ] Test coverage ≥80% (measured by pytest-cov)
- [ ] CI enforces test passing (no continue-on-error)
- [ ] Unit tests cover all models, schemas, security utils
- [ ] Integration tests cover all API endpoints
- [ ] E2E test covers full experiment lifecycle
- [ ] Security tests verify auth, authz, rate limiting
- [ ] Performance tests verify <200ms p95 latency
- [ ] Tests run in <5 minutes locally

---

### **[P0-004] Add Critical Database Indexes**
**Severity:** HIGH | **Effort:** 🟢 Small (1 day) | **Impact:** Performance

**Problem:**
- Slow queries on experiment listing (`user_id + status + created_at`)
- Dashboard aggregations missing covering indexes
- Missing indexes on frequently-filtered fields

**Files to Change:**
- `alembic/versions/XXX_add_performance_indexes.py` (NEW migration)

**Proposed Indexes:**

```sql
-- Migration: 005_add_performance_indexes.py

-- Experiment listing (user's experiments sorted by date)
CREATE INDEX CONCURRENTLY idx_experiments_user_status_created
ON experiments(user_id, status, created_at DESC);

-- Dashboard aggregations (experiment metrics by provider)
CREATE INDEX CONCURRENTLY idx_batch_runs_experiment_provider_status
ON batch_runs(experiment_id, provider, status)
INCLUDE (metrics, total_tokens, completed_at);

-- Iteration analysis (brand extraction queries)
CREATE INDEX CONCURRENTLY idx_iterations_batch_success_brands
ON iterations(batch_run_id, is_success)
WHERE extracted_brands IS NOT NULL;

-- API key lookup (prefix-based auth)
CREATE INDEX CONCURRENTLY idx_api_keys_prefix_active
ON api_keys(key_prefix_hash, is_active)
WHERE is_active = true;

-- User quota queries (billing)
CREATE INDEX CONCURRENTLY idx_users_tier_quota_reset
ON users(pricing_tier, quota_reset_date);

-- Scheduled experiments (Celery Beat)
CREATE INDEX CONCURRENTLY idx_experiments_next_run_recurring
ON experiments(next_run_at)
WHERE is_recurring = true AND status != 'cancelled';
```

**Testing Plan:**
```sql
-- Before: Verify slow queries
EXPLAIN ANALYZE
SELECT * FROM experiments
WHERE user_id = '...' AND status = 'completed'
ORDER BY created_at DESC
LIMIT 10;
-- Expected: Seq Scan (slow)

-- After: Verify index usage
EXPLAIN ANALYZE ...
-- Expected: Index Scan using idx_experiments_user_status_created
```

**Acceptance Criteria:**
- [ ] All 6 indexes created with `CONCURRENTLY` (no downtime)
- [ ] `EXPLAIN ANALYZE` shows index usage on critical queries
- [ ] Experiment listing query <10ms for 10K experiments
- [ ] Dashboard aggregation query <50ms
- [ ] Migration tested on production snapshot

**Migration/Rollout Plan:**
1. Test migration on production DB snapshot
2. Run `CREATE INDEX CONCURRENTLY` during low-traffic window
3. Monitor query performance via pg_stat_statements
4. Verify index usage with EXPLAIN ANALYZE

---

## P1: High Priority (Next Sprint)

### **[P1-001] Add CSRF Protection**
**Severity:** MEDIUM-HIGH | **Effort:** 🟡 Medium (2 days) | **Impact:** Security

**Problem:**
State-changing endpoints lack CSRF protection. While JWT auth provides some protection, API key authentication is vulnerable if keys stored in localStorage and accessed by malicious scripts.

**Affected Endpoints:**
- `POST /api/v1/experiments` (create experiment)
- `POST /api/v1/billing/checkout` (initiate payment)
- `DELETE /api/v1/auth/api-keys/{id}` (revoke API key)
- `PUT /api/v1/brand/profile` (update brand profile)

**Files to Change:**
- `backend/app/middleware/csrf.py` (NEW - CSRF middleware)
- `backend/app/main.py` (register middleware)
- `frontend/src/lib/api.ts` (add CSRF token handling)

**Proposed Solution:**

```python
# backend/app/middleware/csrf.py
from fastapi import Request, HTTPException
import secrets

class CSRFMiddleware:
    """Double-submit cookie pattern for CSRF protection."""

    async def __call__(self, request: Request, call_next):
        # Skip CSRF for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Skip CSRF for API key auth (not cookie-based)
        if request.headers.get("X-API-Key"):
            return await call_next(request)

        # Verify CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        csrf_cookie = request.cookies.get("csrf_token")

        if not csrf_token or csrf_token != csrf_cookie:
            raise HTTPException(status_code=403, detail="CSRF validation failed")

        return await call_next(request)

# backend/app/main.py
app.add_middleware(CSRFMiddleware)

@app.get("/api/v1/csrf-token")
async def get_csrf_token(response: Response):
    """Issue CSRF token for frontend."""
    token = secrets.token_urlsafe(32)
    response.set_cookie("csrf_token", token, httponly=True, samesite="strict")
    return {"csrf_token": token}

# frontend/src/lib/api.ts
let csrfToken: string | null = null;

async function initCSRF() {
    const response = await fetch('/api/v1/csrf-token');
    const data = await response.json();
    csrfToken = data.csrf_token;
}

// Add CSRF token to all state-changing requests
axios.interceptors.request.use(config => {
    if (['POST', 'PUT', 'DELETE'].includes(config.method.toUpperCase())) {
        config.headers['X-CSRF-Token'] = csrfToken;
    }
    return config;
});
```

**Testing:**
```python
async def test_csrf_protection():
    """Verify CSRF tokens required for state-changing operations."""
    # Request without CSRF token should fail
    response = await client.post("/api/v1/experiments", json={...})
    assert response.status_code == 403

    # Request with valid CSRF token should succeed
    csrf_token = (await client.get("/api/v1/csrf-token")).json()["csrf_token"]
    response = await client.post(
        "/api/v1/experiments",
        json={...},
        headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 202
```

**Acceptance Criteria:**
- [ ] CSRF middleware implemented and registered
- [ ] CSRF token endpoint added
- [ ] Frontend fetches and includes CSRF token in requests
- [ ] State-changing endpoints require CSRF token
- [ ] API key auth bypasses CSRF (not cookie-based)
- [ ] Tests verify CSRF enforcement

---

### **[P1-002] Fix Celery Worker Concurrency**
**Severity:** HIGH | **Effort:** 🟢 Small (1 day) | **Impact:** Scalability

**Problem:**
- Hardcoded `concurrency=2` in `start.sh`
- Only 2 concurrent experiments can run, even if server has 16 cores
- No auto-scaling based on queue depth

**Files to Change:**
- `start.sh` (update Celery worker command)
- `backend/app/core/config.py` (add worker config)

**Proposed Solution:**

```bash
# start.sh
# Dynamic concurrency based on CPU cores
WORKER_CONCURRENCY=${WORKER_CONCURRENCY:-$(nproc)}
WORKER_MAX_CONCURRENCY=${WORKER_MAX_CONCURRENCY:-$((WORKER_CONCURRENCY * 2))}

celery -A backend.app.worker worker \
  --concurrency=$WORKER_CONCURRENCY \
  --autoscale=$WORKER_MAX_CONCURRENCY,$WORKER_CONCURRENCY \
  --max-tasks-per-child=100 \
  --loglevel=info \
  --time-limit=3600 \
  --soft-time-limit=3300 &

CELERY_WORKER_PID=$!
```

**Configuration:**
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    celery_worker_concurrency: int = Field(
        default=0,  # 0 = auto-detect CPU cores
        description="Celery worker concurrency (0 = auto)"
    )
    celery_max_tasks_per_child: int = Field(
        default=100,
        description="Restart worker after N tasks (prevent memory leaks)"
    )
```

**Testing:**
```python
async def test_concurrent_experiments():
    """Verify multiple experiments run concurrently."""
    # Queue 5 experiments
    experiment_ids = []
    for i in range(5):
        exp = await create_experiment()
        experiment_ids.append(exp.id)

    # Wait for all to complete
    await wait_for_experiments(experiment_ids, timeout=60)

    # Verify all completed (not queued serially)
    for exp_id in experiment_ids:
        exp = await get_experiment(exp_id)
        assert exp.status == "completed"
```

**Acceptance Criteria:**
- [ ] Worker concurrency auto-detects CPU cores
- [ ] Environment variable override works (`WORKER_CONCURRENCY`)
- [ ] Autoscaling enabled (scale up/down based on queue)
- [ ] Max tasks per child prevents memory leaks
- [ ] 5+ experiments can run concurrently on 4-core machine

---

### **[P1-003] Add Structured Logging**
**Severity:** MEDIUM | **Effort:** 🟡 Medium (3 days) | **Impact:** Observability

**Problem:**
- Plain text logging (hard to parse/query)
- No request ID tracking
- No correlation between API requests and Celery tasks
- Missing business metrics logging

**Files to Change:**
- `backend/app/core/logging.py` (NEW - logging config)
- `backend/app/main.py` (configure logging)
- `backend/app/middleware/request_id.py` (NEW - request ID middleware)

**Proposed Solution:**

```python
# backend/app/core/logging.py
import structlog

def configure_logging():
    """Configure structured logging with JSON output."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

# backend/app/middleware/request_id.py
import uuid
from fastapi import Request
from structlog import contextvars

class RequestIDMiddleware:
    async def __call__(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Usage in routers
logger = structlog.get_logger()

@router.post("/experiments")
async def create_experiment(...):
    logger.info(
        "experiment_created",
        experiment_id=str(experiment.id),
        user_id=str(current_user.id),
        target_brand=experiment.target_brand,
        iterations=experiment.config["iterations"],
        provider=experiment.config["provider"],
    )
```

**Log Examples:**

**Before:**
```
INFO:     User test@example.com creating experiment for brand 'TestBrand'
```

**After:**
```json
{
  "event": "experiment_created",
  "level": "info",
  "timestamp": "2026-01-15T10:30:45.123Z",
  "request_id": "a1b2c3d4-...",
  "user_id": "550e8400-...",
  "experiment_id": "7c9e6679-...",
  "target_brand": "TestBrand",
  "iterations": 10,
  "provider": "openai",
  "user_tier": "pro"
}
```

**Acceptance Criteria:**
- [ ] All logs output as JSON
- [ ] Request ID tracked across API + Celery
- [ ] Business events logged (experiments, quotas, errors)
- [ ] Logs parseable by log aggregation tools
- [ ] Context variables preserved across async boundaries

---

### **[P1-004] Implement Audit Logs**
**Severity:** MEDIUM | **Effort:** 🟡 Medium (3 days) | **Impact:** Compliance + Security

**Problem:**
- No tracking of administrative actions
- No visibility into who accessed what data when
- Required for GDPR Article 30 (Records of Processing Activities)
- Required for SOC 2 compliance

**Files to Change:**
- `backend/app/models/audit_log.py` (NEW)
- `backend/app/middleware/audit.py` (NEW)
- `backend/app/routers/admin.py` (add audit log viewing)
- `alembic/versions/XXX_add_audit_logs.py` (migration)

**Proposed Solution:**

```python
# backend/app/models/audit_log.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(index=True)  # 'view_experiment', 'update_user', 'delete_data'
    resource_type: Mapped[str | None]  # 'experiment', 'user', 'api_key'
    resource_id: Mapped[UUID | None]
    ip_address: Mapped[str]
    user_agent: Mapped[str]
    request_id: Mapped[str | None]
    details: Mapped[dict | None] = mapped_column(JSONB)  # Additional context
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), index=True)

# backend/app/middleware/audit.py
@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: UUID, request: Request, current_user: User):
    # Log access
    await create_audit_log(
        user_id=current_user.id,
        action="view_experiment",
        resource_type="experiment",
        resource_id=experiment_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return experiment

# Admin endpoint to view audit logs
@router.get("/admin/audit-logs")
async def get_audit_logs(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    user_id: UUID | None = None,
    action: str | None = None,
    start_date: datetime | None = None,
    limit: int = 100
):
    """View audit logs (admin only)."""
    query = select(AuditLog)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)

    query = query.order_by(AuditLog.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
```

**Actions to Audit:**
- `view_experiment` (when user views experiment details)
- `create_experiment` (when experiment created)
- `delete_experiment` (when experiment deleted)
- `update_user` (when user profile updated)
- `create_api_key` (when API key generated)
- `revoke_api_key` (when API key revoked)
- `export_user_data` (GDPR data export)
- `delete_user_account` (GDPR deletion request)
- `admin_view_user` (admin accessing user data)

**Retention:**
Audit logs retained for 2 years (compliance requirement), then archived.

**Acceptance Criteria:**
- [ ] Audit log model created with migration
- [ ] Middleware logs all sensitive actions
- [ ] Admin endpoint for viewing audit logs
- [ ] Retention policy implemented (2 year archival)
- [ ] Tests verify audit logging

---

## P2: Medium Priority (Schedule Based on Capacity)

### **[P2-001] Add Security Headers**
**Severity:** MEDIUM | **Effort:** 🟢 Small (1 day) | **Impact:** Security

**Problem:**
Missing security headers: HSTS, CSP, X-Frame-Options, X-Content-Type-Options

**Solution:**
```python
# backend/app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # HTTPS enforcement
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content type sniffing protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )

        return response

# main.py
app.add_middleware(SecurityHeadersMiddleware)
```

**Acceptance Criteria:**
- [ ] All security headers added
- [ ] CSP policy tested with frontend
- [ ] No browser console warnings

---

### **[P2-002] Configure Database Connection Pooling**
**Severity:** MEDIUM | **Effort:** 🟢 Small (1 day) | **Impact:** Performance

**Problem:**
No explicit connection pool configuration.

**Solution:**
```python
# backend/app/core/database.py
engine = create_async_engine(
    str(settings.database_url),
    pool_size=20,  # Maintain 20 connections
    max_overflow=10,  # Allow 10 additional under load
    pool_pre_ping=True,  # Verify connection health
    pool_recycle=3600,  # Recycle every hour
    pool_timeout=30,  # Wait 30s for connection
    echo=settings.debug,  # Log SQL in debug mode
)
```

**Monitoring:**
```python
@app.get("/metrics/database")
async def database_metrics():
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid(),
    }
```

**Acceptance Criteria:**
- [ ] Connection pool configured with optimal settings
- [ ] Pool metrics exposed via endpoint
- [ ] No connection leaks under load

---

### **[P2-003] Frontend Code Splitting**
**Severity:** LOW | **Effort:** 🟡 Medium (2 days) | **Impact:** Performance

**Problem:**
Single JS bundle for all routes, causing slow initial load.

**Solution:**
```javascript
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['recharts', '@tanstack/react-query']
  },
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name(module) {
            const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
            return `vendor-${packageName.replace('@', '')}`;
          },
        },
      },
    };
    return config;
  },
}

// Dynamic imports for heavy components
const ExperimentChart = dynamic(() => import('@/components/ExperimentChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false
});
```

**Acceptance Criteria:**
- [ ] Initial bundle size <200KB
- [ ] Route-based code splitting
- [ ] Heavy libraries lazy-loaded
- [ ] Lighthouse score >90

---

### **[P2-004] Create Staging Environment**
**Severity:** MEDIUM | **Effort:** 🟡 Medium (1 week) | **Impact:** Risk Reduction

**Problem:**
All changes deploy directly to production. No staging environment for testing.

**Solution:**
1. Create Railway staging service
2. Duplicate environment variables
3. Use separate database (staging_db)
4. Update CI to deploy `develop` branch to staging
5. Add manual promotion to production

**CI Changes:**
```yaml
# .github/workflows/ci-cd.yml
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to Staging
      run: |
        railway up --environment=staging

deploy-production:
  if: github.ref == 'refs/heads/main'
  needs: [test, build]
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to Production
      run: |
        railway up --environment=production
```

**Acceptance Criteria:**
- [ ] Staging environment created on Railway
- [ ] Separate staging database
- [ ] `develop` branch deploys to staging
- [ ] Manual promotion gate to production
- [ ] Staging URL documented

---

## Summary of Priorities

| Priority | Item | Effort | Impact | Risk |
|----------|------|--------|--------|------|
| **P0** | **Critical (Must Fix)** | **9 days** | **HIGH** | **HIGH** |
| P0-001 | Fix API Key Auth Timing Attack | 2 days | HIGH | HIGH |
| P0-002 | Data Retention & GDPR Compliance | 3 days | HIGH | HIGH |
| P0-003 | Comprehensive Test Suite (80%+) | 2 weeks | HIGH | MEDIUM |
| P0-004 | Add Critical Database Indexes | 1 day | HIGH | LOW |
| **P1** | **High Priority (Next Sprint)** | **9 days** | **MEDIUM-HIGH** | **MEDIUM** |
| P1-001 | Add CSRF Protection | 2 days | MEDIUM | HIGH |
| P1-002 | Fix Celery Worker Concurrency | 1 day | HIGH | LOW |
| P1-003 | Add Structured Logging | 3 days | MEDIUM | LOW |
| P1-004 | Implement Audit Logs | 3 days | MEDIUM | MEDIUM |
| **P2** | **Medium Priority (Capacity-Based)** | **5 days** | **LOW-MEDIUM** | **LOW** |
| P2-001 | Add Security Headers | 1 day | MEDIUM | LOW |
| P2-002 | Configure Connection Pooling | 1 day | MEDIUM | LOW |
| P2-003 | Frontend Code Splitting | 2 days | LOW | LOW |
| P2-004 | Create Staging Environment | 1 week | MEDIUM | MEDIUM |

**Total Estimated Effort:** 8-10 weeks (with parallel work on multiple items)

---

## Recommended Execution Plan

**Sprint 1 (Week 1-2): Security Hardening**
- P0-001: Fix API key auth timing attack
- P0-002: Implement data retention policy
- P0-004: Add critical database indexes
- P1-001: Add CSRF protection

**Sprint 2 (Week 3-4): Testing & Observability**
- P0-003: Build comprehensive test suite (ongoing)
- P1-003: Add structured logging
- P2-001: Add security headers

**Sprint 3 (Week 5-6): Performance & Scalability**
- P1-002: Fix Celery concurrency
- P2-002: Configure connection pooling
- P2-003: Frontend code splitting

**Sprint 4 (Week 7-8): Compliance & Infrastructure**
- P1-004: Implement audit logs
- P2-004: Create staging environment
- Final testing & documentation

---

**End of Prioritized Backlog**
