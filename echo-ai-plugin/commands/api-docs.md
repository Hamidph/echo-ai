---
description: Generate or update API documentation
allowed-tools: Read, Glob, Write
argument-hint: "<endpoint or router file>"
---

# /api-docs

Document: $ARGUMENTS

Read the FastAPI route files first to understand current endpoints.

For each endpoint, document in this format:

### `METHOD /api/v1/path`

**Description**: What it does
**Auth**: Bearer token required / API key / None

**Request body**:
```json
{ "field": "type" }
```

**Response** `200`:
```json
{
  "success": true,
  "data": { }
}
```

**Errors**: 400 (validation), 401 (auth), 402 (quota exceeded), 500

Add OpenAPI docstring to the FastAPI handler. Update any existing docs files.
Keep language precise and developer-friendly.
