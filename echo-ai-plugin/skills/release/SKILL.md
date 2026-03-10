---
name: release
description: Create a new versioned release of Echo AI. Use when user says "create a release", "tag a release", "bump version", "ship v1.x", or "prepare release". Requires explicit version number.
disable-model-invocation: true
---

# Release Process

STOP — confirm exact version number with user before proceeding.

Version format: MAJOR.MINOR.PATCH (e.g. 1.2.0)

1. Confirm tests pass: run test skill first
2. Update `backend/pyproject.toml` → version = "$ARGUMENTS"
3. Update `frontend/package.json` → "version": "$ARGUMENTS"
4. Ask user for changelog entries for this version
5. Update CHANGELOG.md with date and entries
6. Commit: `git commit -m "chore(release): v$ARGUMENTS"`
7. Tag: `git tag v$ARGUMENTS`
8. Push: `git push origin claude/startup-improvement-plan-WOC5X --tags`
9. Create GitHub release using: `gh release create v$ARGUMENTS --generate-notes`
10. Draft #deployments Slack announcement (ask user to send it)

Do not publish to npm or PyPI — Railway handles deployment.
