---
name: release
description: >
  This skill provides Echo AI's release process and versioning conventions.
  It should be used when the user discusses "releases", "versioning", "tagging",
  or needs context on the release workflow.
---

# Echo AI Release Process

## Versioning
- Format: MAJOR.MINOR.PATCH (semver)
- Version tracked in: `backend/pyproject.toml` and `frontend/package.json`

## Release Steps
1. Confirm tests pass
2. Update version in both backend and frontend
3. Update CHANGELOG.md
4. Commit: `chore(release): vX.Y.Z`
5. Tag: `git tag vX.Y.Z`
6. Push with tags
7. Create GitHub release via `gh release create`
8. Draft announcement for ~~chat

## Rules
- Never release without passing tests
- Always confirm version with user
- Do not publish to npm or PyPI — Railway handles deployment
