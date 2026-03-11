---
description: Create a new versioned release
argument-hint: "<version e.g. 1.2.0>"
---

# /release

STOP — confirm exact version number with user before proceeding.

Version: $ARGUMENTS (format: MAJOR.MINOR.PATCH)

1. Confirm tests pass: run /test first
2. Update `backend/pyproject.toml` → version = "$ARGUMENTS"
3. Update `frontend/package.json` → "version": "$ARGUMENTS"
4. Ask user for changelog entries for this version
5. Update CHANGELOG.md with date and entries
6. Commit: `git commit -m "chore(release): v$ARGUMENTS"`
7. Tag: `git tag v$ARGUMENTS`
8. Push: `git push origin claude/startup-improvement-plan-WOC5X --tags`
9. Create GitHub release via ~~project tracker: `gh release create v$ARGUMENTS --generate-notes`
10. Draft #deployments announcement (ask user to send via ~~chat)

Do not publish to npm or PyPI — Railway handles deployment.
