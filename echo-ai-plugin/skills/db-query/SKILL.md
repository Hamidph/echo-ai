---
name: db-query
description: >
  This skill provides Echo AI's database schema and common query patterns.
  It should be used when the user asks about "users", "revenue", "experiments",
  "database", "metrics", or needs any data from the system.
---

# Database Query (Read-Only)

CRITICAL: Only SELECT queries. Never run INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.

Always add LIMIT. Maximum 1000 rows unless aggregating.

Key tables:
- `users` — id, email, plan_name, created_at, stripe_customer_id
- `experiments` — id, user_id, brand_name, prompt_count, status, created_at
- `experiment_results` — id, experiment_id, llm_provider, visibility_rate, sentiment, avg_position
- `subscriptions` — id, user_id, plan_name, status, amount_cents, billing_cycle
- `api_keys` — id, user_id, key_hash, last_used_at, requests_today

Useful queries:
```sql
-- Active users this week
SELECT COUNT(DISTINCT user_id) FROM experiments
WHERE created_at > NOW() - INTERVAL '7 days';

-- MRR by plan
SELECT plan_name, COUNT(*) as customers, SUM(amount_cents)/100.0 as mrr
FROM subscriptions WHERE status='active' GROUP BY plan_name ORDER BY mrr DESC;

-- Top tracked brands
SELECT brand_name, COUNT(*) as experiments
FROM experiments GROUP BY brand_name ORDER BY 2 DESC LIMIT 20;

-- Recent experiment results
SELECT e.brand_name, e.prompt_count, r.llm_provider, r.visibility_rate, e.created_at
FROM experiments e JOIN experiment_results r ON r.experiment_id = e.id
ORDER BY e.created_at DESC LIMIT 20;

-- Free users who ran experiments (conversion candidates)
SELECT u.email, COUNT(e.id) as experiments, u.created_at
FROM users u JOIN experiments e ON e.user_id = u.id
WHERE u.plan_name = 'free' GROUP BY u.email, u.created_at
ORDER BY experiments DESC LIMIT 50;
```

Run via: `railway run python -c "from backend.db import engine; import pandas as pd; print(pd.read_sql('<QUERY>', engine).to_string())"`
