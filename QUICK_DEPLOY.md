# 🚀 Quick Deploy to Railway - Echo AI

## Option 1: Automated Script (Recommended)

Run the deployment script that will handle everything for you:

```bash
./deploy_to_railway.sh
```

This script will:
- ✅ Install Railway CLI (if needed)
- ✅ Authenticate with Railway
- ✅ Create/link project
- ✅ Add PostgreSQL & Redis
- ✅ Configure environment variables
- ✅ Deploy the application

---

## Option 2: Manual Commands

If you prefer to run commands manually:

### 1. Login to Railway
```bash
railway login
```

### 2. Initialize Project
```bash
railway init
```

### 3. Add Services
```bash
railway add --database postgres
railway add --database redis
```

### 4. Set Environment Variables
```bash
# Generate secrets
export JWT_SECRET=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -base64 32)

# Set variables
railway variables --set "APP_NAME=Echo AI"
railway variables --set "APP_VERSION=1.0.0"
railway variables --set "ENVIRONMENT=production"
railway variables --set "JWT_SECRET=$JWT_SECRET"
railway variables --set "SECRET_KEY=$SECRET_KEY"
railway variables --set "FRONTEND_URL=https://your-frontend.vercel.app"
railway variables --set "CELERY_BROKER_URL=\${{REDIS_URL}}"
railway variables --set "CELERY_RESULT_BACKEND=\${{REDIS_URL}}"
railway variables --set "MAX_WORKERS=4"
railway variables --set "LOG_LEVEL=INFO"

# Stripe (update later with real keys)
railway variables --set "STRIPE_SECRET_KEY=sk_test_placeholder"
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_placeholder"
```

### 5. Deploy
```bash
railway up
```

### 6. Run Migrations
```bash
railway run alembic upgrade head
```

### 7. Check Health
```bash
# Get your URL
railway domain

# Test health endpoint
curl https://your-app.up.railway.app/health
```

---

## Option 3: Deploy from GitHub (No CLI needed)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose** `Hamidph/echo-ai`
5. **Add Services**:
   - Click "+ New" → Database → PostgreSQL
   - Click "+ New" → Database → Redis
6. **Set Environment Variables** (in Railway dashboard):
   - Copy from `.env.production.example`
   - Railway auto-injects `DATABASE_URL` and `REDIS_URL`
7. **Deploy**: Railway auto-deploys on git push

---

## Post-Deployment Checklist

### ✅ Backend Verification
```bash
# Check deployment status
railway status

# View logs
railway logs

# Test health endpoint
curl $(railway domain)/health

# Test API docs
curl $(railway domain)/docs
```

### ✅ Run Database Migrations
```bash
railway run alembic upgrade head
```

### ✅ Create Test User (Optional)
```bash
railway run python backend/scripts/create_test_user.py
```

### ✅ Monitor Application
```bash
# Real-time logs
railway logs --follow

# Open Railway dashboard
railway open
```

---

## Frontend Deployment (Next Step)

After backend is deployed:

### 1. Get Backend URL
```bash
railway domain
# Example: https://echo-ai-production.up.railway.app
```

### 2. Deploy Frontend to Vercel
```bash
cd frontend

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
NEXT_PUBLIC_APP_NAME="Echo AI"
EOF

# Install Vercel CLI (if needed)
npm i -g vercel

# Deploy
vercel --prod
```

### 3. Update Backend CORS
```bash
# After getting Vercel URL
railway variables --set "FRONTEND_URL=https://your-app.vercel.app"
```

---

## Environment Variables Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | Auto-injected by Railway | PostgreSQL connection |
| `REDIS_URL` | ✅ | Auto-injected by Railway | Redis connection |
| `JWT_SECRET` | ✅ | Random 32-byte string | JWT token signing |
| `SECRET_KEY` | ✅ | Random 32-byte string | App secret key |
| `FRONTEND_URL` | ✅ | `https://app.vercel.app` | CORS origin |
| `STRIPE_SECRET_KEY` | ⚠️ | `sk_live_...` or `sk_test_...` | Stripe API key |
| `STRIPE_WEBHOOK_SECRET` | ⚠️ | `whsec_...` | Stripe webhook |
| `SMTP_HOST` | ⚠️ | `smtp.gmail.com` | Email server |
| `SMTP_PORT` | ⚠️ | `587` | Email port |
| `SMTP_USERNAME` | ⚠️ | `your@email.com` | Email username |
| `SMTP_PASSWORD` | ⚠️ | `your-password` | Email password |

**Legend**: ✅ Required | ⚠️ Optional (can configure later)

---

## Troubleshooting

### Issue: Build fails
```bash
# Check build logs
railway logs --build

# Verify Dockerfile
docker build -t echo-ai .
```

### Issue: Health check fails
```bash
# Check if app is running
railway logs --follow

# Verify database connection
railway run python -c "from backend.app.core.database import engine; print('DB OK')"
```

### Issue: Database connection error
```bash
# Check DATABASE_URL
railway variables

# Run migrations
railway run alembic upgrade head
```

### Issue: Redis connection error
```bash
# Check REDIS_URL
railway variables

# Test Redis connection
railway run python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

---

## Monitoring & Maintenance

### View Real-time Logs
```bash
railway logs --follow
```

### Check Resource Usage
```bash
railway status
```

### Restart Service
```bash
railway restart
```

### Update Environment Variable
```bash
railway variables --set "VARIABLE_NAME=new-value"
```

### Redeploy Latest Code
```bash
git push origin main
# Railway auto-deploys on push
```

---

## Cost Estimation

Railway Pricing (as of deployment):

| Resource | Usage | Monthly Cost |
|----------|-------|--------------|
| **Hobby Plan** | Up to $5 free | $0 |
| **Web Service** | ~$5-10/month | Included |
| **PostgreSQL** | 1GB storage | Included |
| **Redis** | 100MB storage | Included |
| **Bandwidth** | 100GB/month | Included |

**Estimated Total**: $0-5/month for MVP testing
**Production Scale**: $20-50/month with paid plan

---

## Next Steps After Deployment

1. ✅ **Verify Backend**: Test health endpoint and API docs
2. ✅ **Run Migrations**: Initialize database schema
3. ✅ **Deploy Frontend**: Push to Vercel with backend URL
4. ✅ **Update CORS**: Add Vercel URL to backend
5. ✅ **Test Authentication**: Create user and login
6. ✅ **Configure Stripe**: Add production keys when ready
7. ✅ **Set Up Monitoring**: Configure Sentry (optional)
8. ✅ **Custom Domain**: Add domain in Railway dashboard
9. ✅ **SSL Certificate**: Auto-configured by Railway
10. ✅ **Backup Strategy**: Enable Railway backups

---

## Support & Resources

- 📚 **Railway Docs**: https://docs.railway.app/
- 💬 **Railway Discord**: https://discord.gg/railway
- 🐛 **Issues**: https://github.com/Hamidph/echo-ai/issues
- 📖 **Full Guide**: See `RAILWAY_DEPLOYMENT.md`

---

**Ready to deploy? Run `./deploy_to_railway.sh` to get started! 🚀**

