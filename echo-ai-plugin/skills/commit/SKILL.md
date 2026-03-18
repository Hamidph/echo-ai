---
name: commit
description: >
  This skill provides Echo AI's commit conventions and git workflow standards.
  It should be used when the user mentions "commit", "save my work", "git commit",
  "push my changes", or discusses version control practices.
---

# Echo AI Git Conventions

## Commit Format
`type(scope): description`

## Types
feat, fix, chore, docs, refactor, perf, test, style

## Scopes
api, frontend, db, auth, billing, experiments, workers, infra, skills

## Examples
- `feat(experiments): add Monte Carlo confidence intervals`
- `fix(auth): handle JWT expiry edge case`
- `chore(infra): update Railway config`

## Branch
Active branch: `claude/startup-improvement-plan-WOC5X`
Never push to main directly — always use PRs.

## Never Commit
.env, secrets, node_modules, __pycache__, *.pyc, .DS_Store
