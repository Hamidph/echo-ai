---
description: Create a structured bug report
allowed-tools: Bash, Read
argument-hint: "<error description or user complaint>"
---

# /bug-report

From: $ARGUMENTS

Create a structured bug report:

## Bug: [Short descriptive title]

**Severity**: Critical / High / Medium / Low
**Area**: API / Frontend / Experiments / Billing / Auth / Workers

### Description
[What is broken, in plain English]

### Steps to Reproduce
1. ...

### Expected Behavior
### Actual Behavior
### Error Output

### Environment
- Plan: [user plan if known]
- Browser/Client: [if frontend]
- Reported: [date]

### Possible Cause
[Hypothesis based on the codebase]

### Fix Estimate
[S / M / L]

Then: create a GitHub issue via ~~project tracker using `gh issue create --title "Bug: [title]" --body "[report]" --label bug`
