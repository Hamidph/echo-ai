---
name: api-docs
description: Generate or update API documentation for Echo AI endpoints. Use when user says "document this endpoint", "write API docs", "generate OpenAPI spec", "update the docs", or "how does this API work".
allowed-tools: Read, Glob, Write
---

# API Documentation Generator

Read the FastAPI route files first to understand current endpoints.

For "$ARGUMENTS" (endpoint or router file):

1. Read the route handler and its request/response models
2. Document in this format:

### `POST /api/v1/experiments`

**Description**: Creates a new brand visibility experiment using Monte Carlo simulation.

**Auth**: Bearer token required

**Request body**:
```json
{
  "brand_name": "string",
  "prompts": ["string"],
  "iterations": 10,
  "providers": ["openai", "anthropic", "perplexity"]
}
```

**Response** `200`:
```json
{
  "success": true,
  "data": {
    "experiment_id": "uuid",
    "status": "queued",
    "estimated_completion": "ISO8601"
  }
}
```

**Errors**: 400 (validation), 401 (auth), 402 (quota exceeded), 500

3. Add OpenAPI docstring to the FastAPI handler
4. Update any existing docs files

Keep language precise and developer-friendly.
