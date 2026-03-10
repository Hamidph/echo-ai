---
name: debug
description: Debug errors, exceptions, test failures, and unexpected behavior in Echo AI. Use when user shares a stack trace, error message, says "it's broken", "fix this error", "tests are failing", or "why is X not working".
allowed-tools: Read, Edit, Bash, Grep, Glob
---

# Debug Workflow

1. Read the complete error message and stack trace
2. Identify the exact file and line number
3. Read the relevant source files with context
4. Check: recent git changes (`git log --oneline -10`), env vars, DB state
5. Form a root cause hypothesis — do not guess, reason from evidence
6. Implement the minimal fix (do not refactor while debugging)
7. Verify: run the specific failing test
8. Regression check: run full test suite
9. Report: root cause, fix applied, how to prevent recurrence

Common Echo AI failure points:
- Celery workers losing Redis connection → check REDIS_URL env var
- Alembic migration conflicts → check migration chain
- OpenAI/Anthropic rate limits → check experiment worker retry logic
- Stripe webhook failures → check webhook secret and endpoint URL
- JWT expiry edge cases → check token refresh logic in frontend
- Perplexity Sonar timeouts → check provider timeout settings
