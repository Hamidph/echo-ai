# Echo AI Deployment Guide

## Quick Start: Deploy in 30 Minutes

### Prerequisites
- GitHub account with this repo pushed
- Credit card for cloud services
- Domain name (optional but recommended)

---

## Option A: Railway (Easiest - $5/month to start)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `ai-visibility` repository

### Step 3: Add Database Services
In Railway dashboard:
1. Click "New" → "Database" → "PostgreSQL"
2. Click "New" → "Database" → "Redis"

### Step 4: Add Backend Service
1. Click "New" → "GitHub Repo" → select your repo
2. Configure:
   - **Root Directory:** `/`
   - **Build Command:** `pip install uv && uv sync`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Step 5: Add Worker Service
1. Click "New" → "GitHub Repo" → select your repo again
2. Configure:
   - **Root Directory:** `/`
   - **Build Command:** `pip install uv && uv sync`
   - **Start Command:** `celery -A backend.app.worker worker --loglevel=info`

### Step 6: Set Environment Variables
For BOTH backend and worker services, add these variables:

```env
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate with: openssl rand -hex 32>

# Database (copy from Railway PostgreSQL service)
DATABASE_URL=${{Postgres.DATABASE_URL}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_HOST=${{Postgres.PGHOST}}
POSTGRES_PORT=${{Postgres.PGPORT}}
POSTGRES_DB=${{Postgres.PGDATABASE}}

# Redis (copy from Railway Redis service)
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_HOST=${{Redis.REDISHOST}}
REDIS_PORT=${{Redis.REDISPORT}}
REDIS_PASSWORD=${{Redis.REDISPASSWORD}}

# LLM API Keys
OPENAI_API_KEY=sk-your-key-here

# Stripe (get from Stripe Dashboard)
STRIPE_API_KEY=sk_live_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret

# Frontend URL (update after Vercel deploy)
FRONTEND_URL=https://your-app.vercel.app
```

### Step 7: Run Migrations
In Railway, open the backend service terminal:
```bash
alembic upgrade head
```

### Step 8: Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Configure:
   - **Framework:** Next.js
   - **Root Directory:** `frontend`
4. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
   ```
5. Deploy

### Step 9: Update CORS
Go back to Railway backend and add:
```
FRONTEND_URL=https://your-app.vercel.app
```

---

## Option B: Google Cloud Platform (Production-Grade)

### Prerequisites
```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 1: Enable Required APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Create Cloud SQL (PostgreSQL)
```bash
# Create instance
gcloud sql instances create echo-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create ai_visibility_db --instance=echo-ai-db

# Create user
gcloud sql users create ai_visibility \
  --instance=echo-ai-db \
  --password=YOUR_STRONG_PASSWORD
```

### Step 3: Create Redis (Memorystore)
```bash
gcloud redis instances create echo-ai-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Step 4: Store Secrets
```bash
# Create secrets
echo -n "YOUR_SECRET_KEY" | gcloud secrets create secret-key --data-file=-
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_STRIPE_KEY" | gcloud secrets create stripe-api-key --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-
```

### Step 5: Set GitHub Secrets
In your GitHub repo → Settings → Secrets:
- `GCP_PROJECT_ID`: your-project-id
- `GCP_SA_KEY`: Service account JSON key (create one with Cloud Run Admin + Cloud SQL Client roles)

### Step 6: Deploy
Push to main branch - GitHub Actions will deploy automatically:
```bash
git push origin main
```

### Step 7: Run Migrations
```bash
gcloud run jobs execute ai-visibility-migrate --region=us-central1
```

### Step 8: Deploy Frontend
Same as Option A Step 8, but set:
```
NEXT_PUBLIC_API_URL=https://ai-visibility-api-xxxxx.run.app
```

---

## Post-Deployment Checklist

### 1. Configure Stripe Webhooks
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Add endpoint: `https://YOUR_API_URL/api/v1/billing/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret to your environment

### 2. Create Stripe Products
```bash
# In Stripe Dashboard, create products:
# - Starter: $49/month (5,000 prompts)
# - Pro: $199/month (50,000 prompts)
# - Enterprise: $999/month (1,000,000 prompts)

# Update price IDs in backend/app/services/billing.py
```

### 3. Set Up Monitoring
1. **Sentry**: Create project at sentry.io, add `SENTRY_DSN` to env
2. **Uptime**: Use UptimeRobot or Better Uptime for `/health` endpoint

### 4. Configure Domain (Optional)
```bash
# For Railway
railway domain

# For GCP Cloud Run
gcloud run services update ai-visibility-api \
  --region=us-central1 \
  --add-custom-domain=api.yourdomain.com
```

### 5. SSL Certificates
- Railway: Automatic
- Vercel: Automatic
- GCP Cloud Run: Automatic

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT signing key (32+ chars) |
| `ENVIRONMENT` | Yes | `production` |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `ANTHROPIC_API_KEY` | No | Anthropic API key |
| `PERPLEXITY_API_KEY` | No | Perplexity API key |
| `STRIPE_API_KEY` | Yes | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Yes | Stripe webhook signing secret |
| `SENTRY_DSN` | No | Sentry error tracking |
| `FRONTEND_URL` | Yes | Frontend URL for CORS |

---

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is accessible
psql $DATABASE_URL -c "SELECT 1"

# Check migrations status
alembic current
alembic upgrade head
```

### Worker Not Processing Jobs
```bash
# Check Redis connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping

# Check Celery logs
celery -A backend.app.worker inspect active
```

### CORS Errors
Ensure `FRONTEND_URL` is set correctly in backend environment.

### Health Check Failing
```bash
curl https://YOUR_API_URL/health
```

---

## Cost Estimates

### Railway (Starter)
- PostgreSQL: ~$5/month
- Redis: ~$5/month
- Backend: ~$5-20/month (usage-based)
- Worker: ~$5-20/month (usage-based)
- **Total: ~$20-50/month**

### GCP (Production)
- Cloud SQL (db-f1-micro): ~$10/month
- Memorystore Redis (1GB): ~$35/month
- Cloud Run API: ~$0-50/month (usage-based)
- Cloud Run Worker: ~$10-50/month
- **Total: ~$55-145/month**

### Vercel (Frontend)
- Hobby: Free
- Pro: $20/month (recommended for production)
