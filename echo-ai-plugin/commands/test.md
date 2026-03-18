---
description: Run Echo AI test suites
argument-hint: "[backend|frontend|file-path]"
---

# /test

Run tests for: $ARGUMENTS (default: full suite)

### Full suite
```bash
cd backend && python -m pytest tests/ -v --tb=short 2>&1 | tail -60
cd ../frontend && npm run type-check && npm test -- --watchAll=false
```

### Backend only
```bash
cd backend && python -m pytest tests/ -v --tb=short
```

### Specific test file
```bash
cd backend && python -m pytest $ARGUMENTS -v --tb=long
```

### Type check only
```bash
cd frontend && npm run type-check
```

Report: total passed / failed / skipped. Show full output for failures.
