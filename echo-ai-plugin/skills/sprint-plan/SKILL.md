---
name: sprint-plan
description: Plan a development sprint for Echo AI. Use when user says "plan the sprint", "create sprint tasks", "prioritize backlog", "what should we build next", "sprint planning", or "what's P0 this week".
allowed-tools: Read, Bash
---

# Sprint Planning

Read CLAUDE.md for current priorities and known issues first.
Check open GitHub issues: `gh issue list --state open --limit 30`

For "$ARGUMENTS" (sprint goal, or leave blank):

### Sprint structure (1 week, 1 developer + Claude Code)
Capacity: ~40 focused engineering hours

### Priority framework
- **P0**: Revenue blocked, users broken, data loss risk — fix today
- **P1**: Directly adds revenue or removes key friction — this sprint
- **P2**: Quality, performance, tech debt — next sprint
- **P3**: Nice to have — backlog

### Task format
For each item:
- [ ] **Title** — [P0/P1/P2/P3] [S=2h / M=4h / L=8h]
  - What: clear description
  - Done when: specific acceptance criteria
  - Depends on: (if any)

### This sprint (fits in 40h)
[P0 + highest P1 items]

### Next sprint
[Remaining P1 + key P2 items]

### Backlog
[P2 + P3 items]

Focus on: things that close sales, reduce churn, or reduce support load.
