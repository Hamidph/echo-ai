---
name: standup
description: >
  This skill provides Echo AI's standup format and progress reporting conventions.
  It should be used when the user discusses "standup", "daily update", "progress",
  or "blockers".
---

# Echo AI Standup Format

## Structure
**Yesterday** — plain English summary of work done (not raw commit messages)
**Today** — planned work
**Blockers** — failing tests, stuck PRs, production issues, anything waiting on someone

## Data Sources
- Recent commits: `git log --since="24 hours ago" --oneline`
- Open PRs: `gh pr list --state open`
- Test status: `cd backend && python -m pytest tests/ -q`

## Rules
- Keep it under 12 lines
- Async-friendly — no fluff
- Surface blockers prominently
