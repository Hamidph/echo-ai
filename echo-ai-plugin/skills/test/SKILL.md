---
name: test
description: Run Echo AI test suites. Use when user says "run tests", "are tests passing", "check tests", "run the test suite", or before any deploy.
disable-model-invocation: true
---

# Run Tests

### Full suite
```bash
cd backend && python -m pytest tests/ -v --tb=short 2>&1 | tail -60
cd ../frontend && npm run type-check && npm test -- --watchAll=false
```

### Backend only
```bash
cd backend && python -m pytest tests/ -v --tb=short
```

### Specific test file (use $ARGUMENTS)
```bash
cd backend && python -m pytest $ARGUMENTS -v --tb=long
```

### Type check only
```bash
cd frontend && npm run type-check
```

Report: total passed / failed / skipped. Show full output for failures.
Flag any new failures compared to what user expected.
