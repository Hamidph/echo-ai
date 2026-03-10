---
name: bug-report
description: Create a structured bug report from a user complaint or error description. Use when user says "log this bug", "create a bug report", "user reported an issue", "something is broken", or pastes a user complaint.
allowed-tools: Bash, Read
---

# Bug Report Creator

From "$ARGUMENTS" or the described issue, create a structured bug report:

```markdown
## Bug: [Short descriptive title]

**Severity**: Critical / High / Medium / Low
**Area**: API / Frontend / Experiments / Billing / Auth / Workers

### Description
[What is broken, in plain English]

### Steps to Reproduce
1.
2.
3.

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Error Output
```
[Stack trace or error message if available]
```

### Environment
- Plan: [user plan if known]
- Browser/Client: [if frontend]
- Reported: [date]

### Possible Cause
[Your hypothesis based on the codebase]

### Fix Estimate
[S / M / L]
```

Then: create a GitHub issue using `gh issue create --title "Bug: [title]" --body "[report]" --label bug`
