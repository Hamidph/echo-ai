# Echo AI - Operations Runbook
**Last Updated:** January 15, 2026
**Version:** 1.0
**For:** Production Operations Team

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Deployment Procedures](#deployment-procedures)
3. [Rollback Procedures](#rollback-procedures)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Incident Response](#incident-response)
6. [Common Issues](#common-issues)
7. [Database Operations](#database-operations)
8. [Scaling Procedures](#scaling-procedures)
9. [Maintenance Windows](#maintenance-windows)
10. [On-Call Procedures](#on-call-procedures)

---

## System Overview

### Architecture
- **Platform:** Railway (production)
- **Runtime:** Docker containers (FastAPI + Celery + Beat)
- **Database:** PostgreSQL 15 (Railway managed)
- **Cache/Broker:** Redis 7 (Railway managed)
- **Frontend:** Next.js static export (served by FastAPI)
- **Monitoring:** Prometheus metrics, Sentry error tracking

### Key Services
| Service | Port | Health Check | Purpose |
|---------|------|--------------|---------|
| FastAPI | 8080 | `/health` | Web API + Frontend |
| Celery Worker | N/A | Redis connection | Background tasks |
| Celery Beat | N/A | Redis connection | Scheduled tasks |
| PostgreSQL | 5432 | `SELECT 1` | Data persistence |
| Redis | 6379 | `PING` | Cache + task queue |

### External Dependencies
- **OpenAI API:** LLM provider (GPT-4o)
- **Anthropic API:** LLM provider (Claude)
- **Perplexity API:** LLM provider (Sonar)
- **Stripe API:** Payment processing
- **Sentry:** Error tracking
- **GitHub:** Source code + CI/CD

---

## Deployment Procedures

### Standard Deployment (main branch)

**Prerequisites:**
- [ ] All tests passing in CI (`main` branch)
- [ ] PR approved by at least 1 reviewer
- [ ] Database migrations reviewed (if any)
- [ ] No active incidents

**Steps:**

1. **Merge PR to main branch**
   ```bash
   # Via GitHub UI or CLI
   gh pr merge <PR_NUMBER> --merge --delete-branch
   ```

2. **Monitor CI/CD Pipeline**
   - Go to: https://github.com/Hamidph/echo-ai/actions
   - Wait for all jobs to complete:
     - ✅ Test and Lint
     - ✅ Build Docker Images
     - ✅ Deploy to Railway (auto-triggered)

3. **Verify Railway Deployment**
   ```bash
   # Check deployment status
   railway status --environment production

   # View recent logs
   railway logs --environment production --tail
   ```

4. **Run Health Check**
   ```bash
   curl https://echo-ai-production.up.railway.app/health

   # Expected response:
   {
     "status": "healthy",
     "version": "1.0.0",
     "environment": "production",
     "services": {
       "redis": "healthy",
       "database": "healthy"
     }
   }
   ```

5. **Run Smoke Tests**
   ```bash
   # Test authentication
   curl -X POST https://echo-ai-production.up.railway.app/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@echoai.com&password=password123"

   # Test experiment creation (with auth token)
   curl -X POST https://echo-ai-production.up.railway.app/api/v1/experiments \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Test smoke test",
       "target_brand": "TestBrand",
       "iterations": 1
     }'
   ```

6. **Monitor Error Rates**
   - Check Sentry: https://sentry.io/organizations/echo-ai/issues/
   - Check Prometheus metrics: `/metrics` endpoint
   - Monitor Railway logs for errors: `railway logs --tail --environment production`

7. **Update Deployment Notes**
   ```bash
   # Document deployment in #deployments Slack channel
   - Deployment timestamp: <TIME>
   - Commit SHA: <SHA>
   - Changes: <SUMMARY>
   - Health check: PASS ✅
   ```

**Rollback Trigger:**
- Error rate spike (>5% of requests)
- Critical functionality broken
- Database connectivity issues
- Memory/CPU over 90% sustained for >5 minutes

---

### Emergency Hotfix Deployment

For critical production issues requiring immediate fix:

1. **Create hotfix branch from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/description-of-issue
   ```

2. **Implement minimal fix**
   - Focus only on the critical issue
   - Avoid scope creep
   - Add tests if possible

3. **Fast-track review**
   - Create PR with `[HOTFIX]` prefix
   - Tag on-call engineer for immediate review
   - Document issue and fix in PR description

4. **Deploy via Railway CLI (bypass CI if needed)**
   ```bash
   # Build and push directly to Railway
   railway up --environment production --service echo-ai

   # Monitor deployment
   railway logs --tail --environment production
   ```

5. **Verify fix**
   - Test the specific issue that was fixed
   - Monitor error rates for 15 minutes

6. **Post-Incident Review**
   - Document incident in `docs/incidents/YYYY-MM-DD.md`
   - Schedule retrospective within 24 hours

---

## Rollback Procedures

### Automated Rollback (Railway UI)

**When to Use:**
- New deployment causes immediate errors
- Health checks failing
- Database connection issues

**Steps:**

1. **Access Railway Dashboard**
   - Go to: https://railway.app/project/<PROJECT_ID>
   - Navigate to "echo-ai" service
   - Click "Deployments" tab

2. **Identify Last Known Good Deployment**
   - Find previous deployment (before failed one)
   - Note the commit SHA and timestamp

3. **Rollback**
   - Click "..." menu on previous deployment
   - Select "Redeploy"
   - Confirm rollback

4. **Verify Rollback**
   ```bash
   # Check health
   curl https://echo-ai-production.up.railway.app/health

   # Verify commit SHA
   curl https://echo-ai-production.up.railway.app/api/v1/health/detailed
   ```

5. **Notify Team**
   - Post in #incidents Slack channel
   - Document rollback reason
   - Create issue to track fix

### Manual Rollback (Git)

**When to Use:**
- Database migration issues
- Need to revert multiple deployments

**Steps:**

1. **Revert Commits on main Branch**
   ```bash
   git checkout main
   git pull origin main

   # Revert last commit
   git revert HEAD

   # Or revert specific commit
   git revert <BAD_COMMIT_SHA>

   # Push revert
   git push origin main
   ```

2. **Handle Database Migrations**
   ```bash
   # SSH into Railway container (if possible) or use Railway CLI
   railway run bash --environment production

   # Downgrade migrations
   alembic downgrade -1  # Downgrade 1 version

   # Or downgrade to specific version
   alembic downgrade <REVISION_ID>
   ```

3. **Verify System State**
   - Check application logs
   - Run smoke tests
   - Monitor error rates for 30 minutes

**CRITICAL:** Database downgrades can cause data loss. Always backup before downgrading.

---

## Monitoring & Alerting

### Key Metrics to Monitor

**Application Health:**
```prometheus
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Worker Health:**
```bash
# Check Celery worker status
celery -A backend.app.worker inspect active

# Check queue depth
celery -A backend.app.worker inspect stats
```

**Database Health:**
```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = 'ai_visibility_db';

-- Long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 minute';

-- Database size
SELECT pg_database_size('ai_visibility_db');
```

### Alerting Rules (Configure in Prometheus/Railway)

**Critical Alerts (Page On-Call):**
- Error rate > 5% for 5 minutes
- p95 latency > 2 seconds for 5 minutes
- Health check failing for 2 minutes
- Database connections > 95% of pool
- Disk usage > 90%
- Memory usage > 90% for 10 minutes

**Warning Alerts (Slack Notification):**
- Error rate > 1% for 10 minutes
- p95 latency > 500ms for 10 minutes
- Queue depth > 100 tasks
- Celery worker down
- LLM API errors > 10%

### Log Locations

**Railway Logs:**
```bash
# Real-time logs
railway logs --tail --environment production

# Filter by service
railway logs --tail --environment production --service echo-ai

# Search logs
railway logs --environment production | grep "ERROR"
```

**Sentry Errors:**
- Dashboard: https://sentry.io/organizations/echo-ai/issues/
- Filter by environment: `environment:production`
- Search: `level:error`

---

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| **SEV1** | Complete outage, data loss, security breach | 5 minutes | All hands |
| **SEV2** | Major feature broken, high error rate | 15 minutes | On-call + manager |
| **SEV3** | Minor feature broken, elevated errors | 1 hour | On-call engineer |
| **SEV4** | Low-impact issue, no user impact | Next business day | Normal process |

### Incident Response Playbook

**1. Acknowledge Incident (< 5 minutes)**
```bash
# Post in #incidents channel
"🚨 INCIDENT: [SEV1] Production API down
- Impact: All users unable to create experiments
- Started: 2026-01-15 10:30 UTC
- Assigned: @john
- Status: Investigating"
```

**2. Investigate (< 15 minutes for SEV1)**
```bash
# Check service health
railway logs --tail --environment production | grep "ERROR"

# Check database
railway run "psql $DATABASE_URL -c 'SELECT 1'"

# Check Redis
railway run "redis-cli -u $REDIS_URL ping"

# Check external APIs
curl https://api.openai.com/v1/health
curl https://api.anthropic.com/v1/health
```

**3. Mitigate (< 30 minutes for SEV1)**
- Rollback to last known good deployment
- Scale up resources if capacity issue
- Disable problematic feature if isolated
- Switch to degraded mode if external dependency down

**4. Resolve**
- Deploy fix
- Verify all systems healthy
- Monitor for 30 minutes

**5. Post-Incident**
- Document incident in `docs/incidents/YYYY-MM-DD.md`
- Schedule retrospective within 24 hours
- Create follow-up issues for preventive measures
- Update runbook with learnings

---

## Common Issues

### Issue: High Error Rate

**Symptoms:**
- 5xx errors in logs
- Sentry error spike
- User reports of failures

**Diagnosis:**
```bash
# Check error logs
railway logs --environment production | grep "ERROR" | head -50

# Check Sentry for common patterns
# Look for stack traces, error messages

# Check database connectivity
railway run "psql $DATABASE_URL -c 'SELECT 1'"
```

**Solutions:**
1. **Database connection exhaustion:**
   ```bash
   # Check pool status
   curl https://echo-ai-production.up.railway.app/metrics | grep db_pool

   # Restart service to reset pool
   railway restart --service echo-ai --environment production
   ```

2. **External API failures:**
   ```bash
   # Check OpenAI status
   curl https://status.openai.com/api/v2/status.json

   # Disable problematic provider temporarily
   # Set env var: DISABLE_OPENAI=true
   ```

3. **Memory leak:**
   ```bash
   # Check memory usage
   railway metrics --environment production

   # Restart worker if memory high
   railway restart --service echo-ai --environment production
   ```

---

### Issue: Slow API Response Times

**Symptoms:**
- p95 latency > 2 seconds
- User reports of slowness
- Timeout errors

**Diagnosis:**
```bash
# Check database query performance
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

# Check slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds';
```

**Solutions:**
1. **Missing indexes:**
   ```bash
   # Run index migration
   railway run "alembic upgrade head" --environment production
   ```

2. **High database load:**
   ```bash
   # Check connection count
   SELECT count(*) FROM pg_stat_activity WHERE datname = 'ai_visibility_db';

   # Scale up database (Railway dashboard)
   ```

3. **Cache not working:**
   ```bash
   # Check Redis connectivity
   railway run "redis-cli -u $REDIS_URL ping"

   # Restart Redis
   railway restart --service redis --environment production
   ```

---

### Issue: Celery Worker Not Processing Tasks

**Symptoms:**
- Experiments stuck in "pending" status
- Queue depth growing
- No worker logs

**Diagnosis:**
```bash
# Check worker status
railway logs --tail --environment production | grep "celery"

# Check queue depth
railway run "celery -A backend.app.worker inspect stats" --environment production
```

**Solutions:**
1. **Worker crashed:**
   ```bash
   # Restart service
   railway restart --service echo-ai --environment production
   ```

2. **Task timeout:**
   ```bash
   # Check for stuck tasks
   railway run "celery -A backend.app.worker inspect active" --environment production

   # Revoke stuck tasks
   railway run "celery -A backend.app.worker control revoke <TASK_ID>" --environment production
   ```

3. **Redis connection lost:**
   ```bash
   # Check Redis health
   railway run "redis-cli -u $REDIS_URL ping"

   # Restart Redis and worker
   railway restart --service redis --environment production
   railway restart --service echo-ai --environment production
   ```

---

## Database Operations

### Creating a Backup

**Automated Backups:**
- Railway creates daily automated backups
- Retention: 7 days (check Railway settings)

**Manual Backup:**
```bash
# Create backup
railway run "pg_dump $DATABASE_URL -Fc" --environment production > backup_$(date +%Y%m%d_%H%M%S).dump

# Verify backup
pg_restore --list backup_*.dump | head -20
```

### Restoring from Backup

**⚠️ CRITICAL: This will overwrite production data. Only use in emergencies.**

```bash
# 1. Download backup
railway backups download <BACKUP_ID> --environment production

# 2. Create test database to verify
createdb test_restore
pg_restore -d test_restore backup.dump

# 3. If verified, restore to production
# WARNING: This drops all data
railway run "pg_restore -d $DATABASE_URL --clean --if-exists backup.dump" --environment production

# 4. Verify restore
railway run "psql $DATABASE_URL -c 'SELECT COUNT(*) FROM users'" --environment production
```

### Running Migrations

**Standard Migration (during deployment):**
```bash
# Migrations run automatically via start.sh
# Monitor logs:
railway logs --tail --environment production | grep "alembic"
```

**Manual Migration:**
```bash
# Apply all pending migrations
railway run "alembic upgrade head" --environment production

# Apply specific migration
railway run "alembic upgrade <REVISION_ID>" --environment production

# Check current version
railway run "alembic current" --environment production
```

**Downgrade Migration (⚠️ DANGEROUS):**
```bash
# Downgrade 1 version
railway run "alembic downgrade -1" --environment production

# Downgrade to specific version
railway run "alembic downgrade <REVISION_ID>" --environment production
```

---

## Scaling Procedures

### Horizontal Scaling (Add More Containers)

**When to Scale Up:**
- CPU > 80% sustained for 10 minutes
- Memory > 80% sustained for 10 minutes
- Request queue growing

**Steps:**
1. **Via Railway Dashboard:**
   - Go to echo-ai service settings
   - Increase "Instances" count
   - Click "Save Changes"

2. **Verify Scaling:**
   ```bash
   railway ps --environment production
   ```

### Vertical Scaling (Increase Resources)

**When to Scale Up:**
- Individual requests timing out
- Memory leaks suspected
- Database queries slow

**Steps:**
1. **Via Railway Dashboard:**
   - Go to echo-ai service settings
   - Increase RAM/CPU limits
   - Click "Save Changes"
   - Service will restart automatically

### Worker Scaling

**Increase Celery Concurrency:**
```bash
# Set environment variable
railway variables set WORKER_CONCURRENCY=10 --environment production

# Restart service to apply
railway restart --service echo-ai --environment production
```

---

## Maintenance Windows

### Scheduled Maintenance Best Practices

**Recommended Time:** Sundays 2:00 AM - 4:00 AM UTC (lowest traffic)

**Pre-Maintenance Checklist:**
- [ ] Announce maintenance 48 hours in advance (website banner + email)
- [ ] Create maintenance page
- [ ] Backup database
- [ ] Test maintenance steps in staging
- [ ] Prepare rollback plan
- [ ] Have 2 engineers on call

**During Maintenance:**
1. **Enable Maintenance Mode**
   ```bash
   # Set maintenance flag
   railway variables set MAINTENANCE_MODE=true --environment production
   ```

2. **Perform Maintenance Tasks**
   - Database migrations
   - Infrastructure upgrades
   - Data cleanup

3. **Disable Maintenance Mode**
   ```bash
   railway variables set MAINTENANCE_MODE=false --environment production
   ```

4. **Verify System**
   - Run smoke tests
   - Monitor error rates for 30 minutes

---

## On-Call Procedures

### On-Call Schedule

- **Primary:** Rotates weekly (Monday 9 AM UTC)
- **Secondary:** Backup if primary unreachable
- **Escalation:** Engineering Manager after 30 minutes

### On-Call Responsibilities

**During On-Call Shift:**
- [ ] Respond to pages within 5 minutes
- [ ] Acknowledge incidents in Slack
- [ ] Follow incident response playbook
- [ ] Update status page
- [ ] Escalate if needed

**Handoff Checklist:**
- [ ] Review open incidents
- [ ] Share context on ongoing issues
- [ ] Update runbook with any learnings
- [ ] Confirm contact details current

### Contact List

| Role | Primary | Secondary |
|------|---------|-----------|
| On-Call Engineer | PagerDuty | Slack DM |
| Engineering Manager | Slack DM | Phone |
| Infrastructure Team | #infrastructure | PagerDuty |
| Database Admin | #database | PagerDuty |

---

## Useful Commands Cheat Sheet

```bash
# Health check
curl https://echo-ai-production.up.railway.app/health

# View logs (real-time)
railway logs --tail --environment production

# Restart service
railway restart --service echo-ai --environment production

# Check deployment status
railway status --environment production

# Set environment variable
railway variables set KEY=value --environment production

# Run one-off command
railway run "python script.py" --environment production

# Database shell
railway run "psql $DATABASE_URL" --environment production

# Redis shell
railway run "redis-cli -u $REDIS_URL" --environment production

# Check Celery workers
railway run "celery -A backend.app.worker inspect stats" --environment production

# Run migrations
railway run "alembic upgrade head" --environment production

# Create database backup
railway run "pg_dump $DATABASE_URL -Fc" > backup.dump --environment production
```

---

## Emergency Contacts

**Critical Issues (SEV1):**
- PagerDuty: https://echoai.pagerduty.com
- Slack: #incidents
- Phone: +1-XXX-XXX-XXXX (On-call)

**Railway Support:**
- Discord: https://discord.gg/railway
- Email: support@railway.app
- Status: https://railway.statuspage.io

**External Services:**
- OpenAI Status: https://status.openai.com
- Anthropic Status: https://status.anthropic.com
- Stripe Status: https://status.stripe.com

---

**End of Runbook**

*This runbook should be updated after every major incident or infrastructure change.*
