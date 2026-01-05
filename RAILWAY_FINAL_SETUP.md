# 🔧 Railway Deployment - Final Setup Steps

## ✅ What's Fixed:
- README.md is now included in Docker build
- Code pushed to GitHub (Railway will auto-redeploy)

---

## 🚀 Complete Your Deployment (3 Minutes)

### Step 1: Add Databases (In Railway Dashboard)

Go to: https://railway.com/project/fdc0642b-be3c-421b-8bca-8432400b3d28

1. Click **"+ New"** button (top right)
2. Select **"Database"** → **"Add PostgreSQL"**
3. Click **"+ New"** again
4. Select **"Database"** → **"Add Redis"**

✅ Done! Railway will auto-inject `DATABASE_URL` and `REDIS_URL`

---

### Step 2: Set Environment Variables

In your Railway dashboard:

1. Click on your **"echo-ai"** service (the one currently building)
2. Click **"Variables"** tab
3. Click **"RAW Editor"** button
4. Copy and paste this (replace JWT_SECRET and SECRET_KEY with generated values below):

```bash
APP_NAME=Echo AI
APP_VERSION=1.0.0
ENVIRONMENT=production
JWT_SECRET=REPLACE_WITH_GENERATED_SECRET_1
SECRET_KEY=REPLACE_WITH_GENERATED_SECRET_2
FRONTEND_URL=https://echo-ai.vercel.app
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
MAX_WORKERS=4
REDIS_MAX_CONNECTIONS=10
REDIS_SOCKET_KEEPALIVE=true
LOG_LEVEL=INFO
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
```

5. Click **"Add"** or **"Save"**

---

### Step 3: Generate Secrets (Run in Terminal)

```bash
# Generate JWT Secret
echo "JWT_SECRET=$(openssl rand -base64 32)"

# Generate Secret Key
echo "SECRET_KEY=$(openssl rand -base64 32)"
```

Copy these values and replace `REPLACE_WITH_GENERATED_SECRET_1` and `REPLACE_WITH_GENERATED_SECRET_2` in the variables above.

---

### Step 4: Wait for Deployment

Railway will automatically:
- ✅ Pull from GitHub
- ✅ Build Docker image (should work now!)
- ✅ Deploy your app
- ✅ Assign a public URL

**Check deployment status:**
- Go to **Deployments** tab
- Watch the build logs
- Should complete in ~3-5 minutes

---

### Step 5: Run Database Migrations

Once deployment is successful:

```bash
cd /Users/hamid/Documents/ai-visibility

# Link project (if not already linked)
railway link

# Run migrations
railway run alembic upgrade head
```

Or in Railway dashboard:
- Click on service → **Settings** → **One-off Commands**
- Run: `alembic upgrade head`

---

### Step 6: Get Your Deployment URL

In Railway dashboard:
- Click on your service
- Go to **Settings** → **Networking**
- Click **"Generate Domain"** if not already generated
- Copy the URL (e.g., `https://echo-ai-production.up.railway.app`)

Or via CLI:
```bash
railway domain
```

---

### Step 7: Test Your API

```bash
# Replace with your actual Railway URL
curl https://your-app.up.railway.app/health

# Should return:
# {"status":"healthy","environment":"production","version":"1.0.0",...}
```

---

## 📋 Quick Checklist

- [ ] PostgreSQL database added
- [ ] Redis database added
- [ ] Environment variables set (with generated secrets)
- [ ] Deployment successful (check logs)
- [ ] Database migrations run
- [ ] Health check passes
- [ ] Domain/URL obtained

---

## 🎯 Next: Deploy Frontend

Once backend is live:

```bash
cd /Users/hamid/Documents/ai-visibility/frontend

# Set backend URL
echo "NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app" > .env.local
echo "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_placeholder" >> .env.local
echo "NEXT_PUBLIC_APP_NAME=Echo AI" >> .env.local

# Deploy to Vercel
vercel --prod
```

Then update backend CORS:
```bash
railway variables --set "FRONTEND_URL=https://your-vercel-url.vercel.app"
```

---

## 🆘 If Build Still Fails

Check Railway deployment logs. If you see any errors, share them and I'll help fix!

---

## 🎉 Success Indicators

✅ Build completes without errors  
✅ Service shows "Active" status  
✅ Health check returns 200 OK  
✅ Logs show "Application startup complete"  

---

**Current Status:**
- ✅ Code fixed and pushed to GitHub
- ⏳ Railway should be rebuilding now
- 📍 Next: Add databases and set environment variables in dashboard

**Go to your Railway dashboard now:** https://railway.com/project/fdc0642b-be3c-421b-8bca-8432400b3d28

