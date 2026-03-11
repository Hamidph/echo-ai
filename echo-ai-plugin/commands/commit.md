---
description: Stage and commit changes using conventional commits
argument-hint: "[type(scope): message]"
---

# /commit

1. Show status: `git status` and `git diff --staged`
2. If nothing staged, ask user which files to stage
3. Write commit message:
   - Format: `type(scope): description`
   - Types: feat, fix, chore, docs, refactor, perf, test, style
   - Scopes: api, frontend, db, auth, billing, experiments, workers, infra, skills
   - Example: `feat(experiments): add Monte Carlo confidence intervals`
   - If $ARGUMENTS provided, use as commit message
4. Commit: `git commit -m "<message>"`
5. Push: `git push -u origin claude/startup-improvement-plan-WOC5X`
6. Confirm: `git log --oneline -3`

NEVER commit: .env, secrets, node_modules, __pycache__, *.pyc, .DS_Store
