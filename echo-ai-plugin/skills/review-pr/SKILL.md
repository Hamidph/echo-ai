---
name: review-pr
description: Review code changes or a pull request for quality, security, and correctness. Use when user says "review PR", "code review", "review my changes", "check this PR", or "is this code good". Checks security, performance, tests, types, and architecture consistency.
allowed-tools: Read, Grep, Glob, Bash
---

# PR Code Review

Review the provided diff or changed files. Output grouped by severity.

### 🔴 Critical (block merge)
- Hardcoded secrets, API keys, passwords
- Missing auth checks on protected routes
- SQL injection risk (non-parameterized queries)
- PII logged to console or files
- Breaking API contract changes

### 🟡 Warning (should fix)
- N+1 query problems
- Missing error handling
- No pagination on list endpoints
- TypeScript `any` usage
- Missing input validation
- No tests for new logic

### 🟢 Suggestion (optional)
- Performance improvements
- Readability
- Better variable names
- Missing docstrings on public functions

### Architecture check
- Consistent with FastAPI routers pattern
- SQLAlchemy 2.0 style (not legacy)
- Next.js App Router conventions
- API response format: `{success: bool, data?: any, error?: string}`

Output: list each issue with file:line reference and a concrete fix suggestion.
