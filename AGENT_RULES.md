# Agent Rules & Standards

This document defines the rules for all AI agents (Claude, Cursor, Gemini, etc.) interacting with this repository. 
**ALL AGENTS MUST READ AND FOLLOW THESE RULES.**

## 1. Documentation Standards
- **Single Source of Truth**: Do not create generic `DEPLOY.md` or `SETUP.md` files in the root if a specific guide already exists.
- **Location**: All documentation should live in the `docs/` directory, or specific workflow guides in `.agent/workflows/`.
- **No Empty Files**: Do not create placeholders. If a document is empty, delete it.
- **Update, Don't Duplicate**: If a guide is outdated, update the existing file instead of creating `NEW_GUIDE.md`.

## 2. Deployment
- **Method**: The application is deployed as a single Railway service (Monolithic Deployment). 
    - Frontend is statically exported and served by the Backend (`FastAPI`).
    - There is NO separate Vercel deployment.
- **Script**: Always refer to `complete_deployment.sh` as the executable source of truth for deployment commands.

## 3. Code Quality
- **Redundancy**: detailed audit of code redundancy is required. Do not duplicate logic between `frontend/lib` and `backend/core` if not necessary (though language separation exists).
- **Configuration**: `NEXT_PUBLIC_API_URL` should be used for build-time configuration in `Dockerfile`. Runtime configuration is handled via relative paths (`/api/v1`) since the frontend is served from the same origin.

## 4. Workflows
- Check `.agent/workflows` before inventing new procedures.
