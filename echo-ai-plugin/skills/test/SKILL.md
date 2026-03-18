---
name: test
description: >
  This skill provides Echo AI's testing conventions and test infrastructure knowledge.
  It should be used when the user discusses "testing", "test coverage", "test strategy",
  or needs context on how tests are organized in the project.
---

# Echo AI Testing Knowledge

## Test Infrastructure
- Backend: pytest (`backend/tests/`)
- Frontend: Jest + TypeScript type-check (`frontend/`)

## Running Tests
- Full backend: `cd backend && python -m pytest tests/ -v --tb=short`
- Full frontend: `cd frontend && npm run type-check && npm test -- --watchAll=false`
- Specific file: `cd backend && python -m pytest tests/test_file.py -v --tb=long`

## Test Standards
- Add tests alongside every new feature
- Test coverage is thin — improve as you go
- Always run tests before deploy
- Report: total passed / failed / skipped
