# Local Development Guide - Fast Iteration

**Purpose:** Run the entire stack locally for instant feedback (1-2 second changes, not 5+ minute Railway deploys)

---

## Why Local Development?

### **Current Problem:**
- Make a change → Commit → Push → Railway deploy → Wait 5+ minutes → Test
- If there's a bug, repeat the entire cycle
- **Total time per iteration: 5-10 minutes**

### **With Local Development:**
- Make a change → Save file → Auto-reload → Test
- **Total time per iteration: 1-2 seconds**

### **How Big Companies Do It:**

**Stripe:**
- Developers run entire stack locally
- Hot reload on every save
- Deploy to staging first, then production
- **Never deploy directly to production without local testing**

**Shopify:**
- Local development environment with Docker
- Automated tests run locally
- CI/CD pipeline: Local → Staging → Production
- **Production deploys happen 50+ times per day**

**Your Setup (After this guide):**
- ✅ Local development with hot reload
- ✅ Test changes in 1-2 seconds
- ✅ Only deploy to Railway when features are complete
- ✅ Professional workflow

---

## Quick Start (5 minutes)

### **Step 1: Install Dependencies**

You already have:
- ✅ Homebrew
- ✅ Docker Desktop
- ✅ uv (Python package manager)
- ✅ pnpm (Node package manager)

### **Step 2: Start Local Database & Redis**

```bash
# Start PostgreSQL and Redis in Docker
docker-compose up -d

# Verify they're running
docker ps
```

### **Step 3: Set Up Backend**

```bash
# Copy environment file
cp env.example .env

# Add your API keys to .env (optional for now)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-...
# PERPLEXITY_API_KEY=pplx-...

# Install dependencies (if not already done)
cd /Users/hamid/Documents/ai-visibility
uv sync

# Run database migrations
uv run alembic upgrade head

# Seed test data
uv run python backend/scripts/seed_test_data.py

# Start backend server (with hot reload)
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend now running at: `http://localhost:8000`

### **Step 4: Start Frontend (New Terminal)**

```bash
cd /Users/hamid/Documents/ai-visibility/frontend

# Install dependencies (if not already done)
pnpm install

# Start dev server (with hot reload)
pnpm dev
```

Frontend now running at: `http://localhost:3000`

### **Step 5: Start Celery Worker (New Terminal, Optional)**

```bash
cd /Users/hamid/Documents/ai-visibility

# Start Celery worker for background tasks
uv run celery -A backend.app.worker worker --loglevel=info
```

---

## Your New Workflow

### **Before (Slow):**
```
1. Edit code
2. git add -A && git commit -m "fix"
3. git push origin main
4. railway up
5. Wait 5+ minutes
6. Test on production URL
7. Find bug, repeat steps 1-6
```

### **After (Fast):**
```
1. Edit code
2. Save file (Cmd+S)
3. Browser auto-refreshes in 1-2 seconds
4. Test immediately
5. Iterate rapidly until feature works
6. THEN deploy to Railway once
```

---

## Hot Reload Explained

### **Backend (FastAPI):**
- `--reload` flag watches for file changes
- When you save a `.py` file, server restarts automatically
- **Time: 1-2 seconds**

### **Frontend (Next.js):**
- `pnpm dev` enables Fast Refresh
- When you save a `.tsx` file, page updates without full reload
- **Time: <1 second**

### **Database:**
- PostgreSQL runs in Docker
- Data persists between restarts
- Can reset with: `docker-compose down -v` (deletes data)

---

## Common Commands

### **Start Everything:**
```bash
# Terminal 1: Database & Redis
docker-compose up -d

# Terminal 2: Backend
uv run uvicorn backend.app.main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend && pnpm dev

# Terminal 4: Celery (optional)
uv run celery -A backend.app.worker worker --loglevel=info
```

### **Stop Everything:**
```bash
# Stop Docker services
docker-compose down

# Stop servers: Ctrl+C in each terminal
```

### **Reset Database:**
```bash
# Delete all data and start fresh
docker-compose down -v
docker-compose up -d
uv run alembic upgrade head
uv run python backend/scripts/seed_test_data.py
```

### **View Logs:**
```bash
# Docker logs
docker-compose logs -f

# Backend logs: visible in terminal
# Frontend logs: visible in terminal
```

---

## Environment Variables

### **Backend (.env):**
```bash
# Database (Docker)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ai_visibility
POSTGRES_PASSWORD=ai_visibility_secret
POSTGRES_DB=ai_visibility_db

# Redis (Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_secret

# API Keys (add yours)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...

# Security
SECRET_KEY=local-dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
```

### **Frontend (.env.local):**
```bash
# Points to local backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Testing Your Changes

### **1. Make a Change:**
```typescript
// frontend/src/app/dashboard/page.tsx
<h1>Dashboard</h1>  // Change this
```

### **2. Save File (Cmd+S)**

### **3. Browser Auto-Refreshes**
- Open `http://localhost:3000/dashboard`
- See change immediately
- **No commit, no deploy, no waiting**

### **4. Iterate Rapidly:**
- Try different approaches
- Test edge cases
- Fix bugs instantly
- **Get feedback in seconds, not minutes**

---

## When to Deploy to Railway

### **Only deploy when:**
- ✅ Feature is complete and tested locally
- ✅ All tests pass
- ✅ No obvious bugs
- ✅ Ready for users to see

### **Deployment workflow:**
```bash
# 1. Test locally first
# 2. Commit changes
git add -A
git commit -m "feat: add new feature (tested locally)"

# 3. Push to GitHub
git push origin main

# 4. Deploy to Railway
railway up --service echo-ai

# 5. Verify on production
# Visit https://echo-ai-production.up.railway.app
```

---

## Troubleshooting

### **Port already in use:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 3000
lsof -ti:3000 | xargs kill -9
```

### **Database connection error:**
```bash
# Restart Docker services
docker-compose restart

# Check if containers are running
docker ps
```

### **Module not found:**
```bash
# Backend
uv sync

# Frontend
cd frontend && pnpm install
```

### **Alembic migration error:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
uv run alembic upgrade head
```

---

## Development Tools

### **API Documentation:**
- Local: `http://localhost:8000/api/v1/docs`
- Interactive Swagger UI
- Test endpoints directly

### **Database GUI:**
```bash
# Install pgAdmin or use TablePlus
# Connect to: localhost:5432
# User: ai_visibility
# Password: ai_visibility_secret
# Database: ai_visibility_db
```

### **Redis GUI:**
```bash
# Install RedisInsight
# Connect to: localhost:6379
# Password: redis_secret
```

---

## Performance Comparison

### **Railway Deployment:**
| Step | Time |
|------|------|
| Code change | 1 min |
| Commit & push | 30 sec |
| Railway build | 3-5 min |
| Test | 1 min |
| **Total** | **5-7 min** |

### **Local Development:**
| Step | Time |
|------|------|
| Code change | 1 min |
| Save & auto-reload | 1-2 sec |
| Test | 1 min |
| **Total** | **~2 min** |

**Speed improvement: 3-4x faster iteration**

---

## Best Practices

### **1. Always Test Locally First**
- Never push untested code to production
- Catch bugs early
- Iterate quickly

### **2. Use Git Branches**
```bash
# Create feature branch
git checkout -b feature/new-dashboard

# Make changes, test locally
# Commit when ready
git add -A
git commit -m "feat: new dashboard"

# Push to GitHub
git push origin feature/new-dashboard

# Merge to main when complete
git checkout main
git merge feature/new-dashboard
git push origin main
```

### **3. Keep Local and Production in Sync**
```bash
# Pull latest changes before starting work
git pull origin main

# Start fresh if needed
docker-compose down -v
docker-compose up -d
uv run alembic upgrade head
```

### **4. Use Environment-Specific Configs**
- `.env` for local backend
- `.env.local` for local frontend
- Railway environment variables for production

---

## Advanced: Hot Reload for Backend Models

When you change database models, you need to create a migration:

```bash
# 1. Change model in backend/app/models/

# 2. Create migration
uv run alembic revision --autogenerate -m "add new field"

# 3. Apply migration
uv run alembic upgrade head

# 4. Backend auto-reloads with new schema
```

---

## Summary

### **What You Get:**
- ✅ **Instant feedback** (1-2 seconds vs 5+ minutes)
- ✅ **Rapid iteration** (test 10+ changes in the time of 1 Railway deploy)
- ✅ **Professional workflow** (same as Stripe, Shopify, etc.)
- ✅ **Catch bugs early** (before they reach production)
- ✅ **Save money** (fewer Railway builds)

### **Next Steps:**
1. Run `docker-compose up -d` to start database
2. Run `uv run uvicorn backend.app.main:app --reload --port 8000` for backend
3. Run `cd frontend && pnpm dev` for frontend
4. Open `http://localhost:3000` and start coding!

---

**You're now set up like a professional engineering team at a fast-moving startup!** 🚀
