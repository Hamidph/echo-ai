---
name: changelog
description: Generate or update the CHANGELOG for Echo AI based on recent git commits. Use when user says "update changelog", "generate changelog", "what changed", or "write release notes".
disable-model-invocation: true
---

# Changelog Generator

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline --pretty=format:"%s"
```

Group commits by type and write in Keep a Changelog format:

```markdown
## [VERSION] - YYYY-MM-DD

### Added
- (feat commits)

### Fixed
- (fix commits)

### Changed
- (refactor, perf commits)

### Security
- (security-related fixes)
```

Write plain English descriptions, not raw commit messages.
Audience: technical users and customers reading release notes.
Prepend to existing CHANGELOG.md, do not overwrite it.
