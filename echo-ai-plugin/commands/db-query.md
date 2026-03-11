---
description: Query Echo AI PostgreSQL database (read-only)
allowed-tools: Bash
argument-hint: "<sql query or question>"
---

# /db-query

CRITICAL: Only SELECT queries. Never run INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.

Always add LIMIT. Maximum 1000 rows unless aggregating.

Query or question: $ARGUMENTS

Key tables:
- `users` — id, email, plan_name, created_at, stripe_customer_id
- `experiments` — id, user_id, brand_name, prompt_count, status, created_at
- `experiment_results` — id, experiment_id, llm_provider, visibility_rate, sentiment, avg_position
- `subscriptions` — id, user_id, plan_name, status, amount_cents, billing_cycle
- `api_keys` — id, user_id, key_hash, last_used_at, requests_today

Run via: `railway run python -c "from backend.db import engine; import pandas as pd; print(pd.read_sql('<QUERY>', engine).to_string())"`
