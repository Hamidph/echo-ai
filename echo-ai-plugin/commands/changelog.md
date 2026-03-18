---
description: Generate changelog from recent git commits
argument-hint: "[version]"
---

# /changelog

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline --pretty=format:"%s"
```

Group commits by type and write in Keep a Changelog format:

```markdown
## [$ARGUMENTS] - YYYY-MM-DD

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
