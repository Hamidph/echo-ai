---
name: standup
description: Generate a daily standup summary for Echo AI. Use when user says "standup", "daily update", "what did we do yesterday", "progress report", or "morning summary". Reads recent commits and surfaces blockers.
disable-model-invocation: true
---

# Daily Standup

```bash
echo "=== COMMITS (last 24h) ===" && \
git log --since="24 hours ago" --oneline && \
echo "" && \
echo "=== OPEN PRs ===" && \
gh pr list --state open 2>/dev/null || echo "(gh not configured)" && \
echo "" && \
echo "=== TEST STATUS ===" && \
cd backend && python -m pytest tests/ -q 2>&1 | tail -3
```

Format output as:

**Yesterday**
- [plain English summary of each commit — not raw commit messages]

**Today**
- [ask user what they're planning]

**Blockers**
- [failing tests, stuck PRs, production issues, anything waiting on someone else]

Keep it under 12 lines. Async-friendly. No fluff.
