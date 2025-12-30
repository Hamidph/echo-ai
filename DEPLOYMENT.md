# Deployment Guide - GCP Cloud Run

This guide covers deploying the AI Visibility platform to Google Cloud Platform using Cloud Run, Cloud SQL, and Memorystore Redis.

## Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP project
   - Billing enabled
   - Required APIs enabled (see below)

2. **Local Tools**
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Docker
   - Python 3.11+

3. **API Keys**
   - OpenAI API key
   - Anthropic API key
   - Perplexity API key

## Step 1: Enable Required GCP APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com
```

## Step 2: Set Up Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export DB_INSTANCE_NAME="ai-visibility-db"
export REDIS_INSTANCE_NAME="ai-visibility-redis"

gcloud config set project $PROJECT_ID
```

## Step 3: Create Cloud SQL PostgreSQL Instance

```bash
# Create Cloud SQL instance (PostgreSQL 16)
gcloud sql instances create $DB_INSTANCE_NAME \
  --database-version=POSTGRES_16 \
  --tier=db-g1-small \
  --region=$REGION \
  --root-password="CHANGE_THIS_PASSWORD" \
  --database-flags=max_connections=100

# Create database
gcloud sql databases create ai_visibility_db \
  --instance=$DB_INSTANCE_NAME

# Create user
gcloud sql users create ai_visibility \
  --instance=$DB_INSTANCE_NAME \
  --password="CHANGE_THIS_PASSWORD"
```

**Production Recommendations:**
- Use `db-custom-2-7680` (2 vCPU, 7.5 GB RAM) for production
- Enable automated backups
- Set up point-in-time recovery
- Use private IP for security

## Step 4: Create Memorystore Redis Instance

```bash
gcloud redis instances create $REDIS_INSTANCE_NAME \
  --size=1 \
  --region=$REGION \
  --redis-version=redis_7_0 \
  --tier=basic

# Get Redis host
export REDIS_HOST=$(gcloud redis instances describe $REDIS_INSTANCE_NAME \
  --region=$REGION \
  --format="get(host)")
```

## Step 5: Store Secrets in Secret Manager

```bash
# Create secrets
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "YOUR_PERPLEXITY_KEY" | gcloud secrets create perplexity-api-key --data-file=-

# Generate and store secret key
openssl rand -hex 32 | gcloud secrets create app-secret-key --data-file=-

# Store database password
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create postgres-password --data-file=-
```

## Step 6: Build and Push Docker Images

```bash
# Build and push API image
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-visibility-api:latest

# Build and push worker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-visibility-worker:latest -f Dockerfile.worker
```

## Step 7: Deploy to Cloud Run

### Deploy API Service

```bash
gcloud run deploy ai-visibility-api \
  --image gcr.io/$PROJECT_ID/ai-visibility-api:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "POSTGRES_HOST=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME" \
  --set-env-vars "POSTGRES_DB=ai_visibility_db" \
  --set-env-vars "POSTGRES_USER=ai_visibility" \
  --set-env-vars "REDIS_HOST=$REDIS_HOST" \
  --set-secrets "SECRET_KEY=app-secret-key:latest" \
  --set-secrets "POSTGRES_PASSWORD=postgres-password:latest" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets "PERPLEXITY_API_KEY=perplexity-api-key:latest" \
  --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME
```

### Deploy Celery Worker

```bash
gcloud run deploy ai-visibility-worker \
  --image gcr.io/$PROJECT_ID/ai-visibility-worker:latest \
  --platform managed \
  --region $REGION \
  --no-allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 5 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "POSTGRES_HOST=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME" \
  --set-env-vars "POSTGRES_DB=ai_visibility_db" \
  --set-env-vars "POSTGRES_USER=ai_visibility" \
  --set-env-vars "REDIS_HOST=$REDIS_HOST" \
  --set-secrets "SECRET_KEY=app-secret-key:latest" \
  --set-secrets "POSTGRES_PASSWORD=postgres-password:latest" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets "PERPLEXITY_API_KEY=perplexity-api-key:latest" \
  --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME
```

## Step 8: Run Database Migrations

```bash
# Create and run migration job
gcloud run jobs create ai-visibility-migrate \
  --image gcr.io/$PROJECT_ID/ai-visibility-api:latest \
  --region $REGION \
  --set-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
  --set-env-vars "POSTGRES_HOST=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME" \
  --set-env-vars "POSTGRES_DB=ai_visibility_db" \
  --set-env-vars "POSTGRES_USER=ai_visibility" \
  --set-secrets "POSTGRES_PASSWORD=postgres-password:latest" \
  --command alembic,upgrade,head

# Execute migration
gcloud run jobs execute ai-visibility-migrate --region $REGION --wait
```

## Step 9: Set Up CI/CD with GitHub Actions

1. **Create Service Account**

```bash
gcloud iam service-accounts create github-actions \
  --display-name "GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

2. **Add GitHub Secrets**

In your GitHub repository settings, add these secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Contents of `key.json`

3. **Push to Main Branch**

The CI/CD pipeline will automatically deploy on push to `main`.

## Step 10: Verify Deployment

```bash
# Get Cloud Run URL
export SERVICE_URL=$(gcloud run services describe ai-visibility-api \
  --region $REGION \
  --format "value(status.url)")

# Test health endpoint
curl $SERVICE_URL/health

# Access API documentation
echo "$SERVICE_URL/api/v1/docs"
```

## Step 11: Set Up Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service ai-visibility-api \
  --domain api.yourdomain.com \
  --region $REGION
```

Follow the instructions to update your DNS settings.

## Step 12: Set Up Monitoring

### Enable Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create \
  --display-name="AI Visibility API Health" \
  --resource-type=uptime-url \
  --http-check-path="/health" \
  --host="$SERVICE_URL"

# Create alert policy (manually in console)
```

### Configure Sentry (Recommended)

1. Create Sentry project
2. Get DSN
3. Add to Secret Manager:

```bash
echo -n "YOUR_SENTRY_DSN" | gcloud secrets create sentry-dsn --data-file=-
```

4. Update Cloud Run service:

```bash
gcloud run services update ai-visibility-api \
  --region $REGION \
  --set-secrets "SENTRY_DSN=sentry-dsn:latest"
```

## Cost Optimization

### Development/Staging

- Cloud SQL: `db-f1-micro` (Free tier eligible)
- Redis: `basic` tier, 1GB
- Cloud Run: Min instances = 0

### Production

- Cloud SQL: `db-custom-2-7680` with read replicas
- Redis: `standard` tier (HA), 5GB
- Cloud Run: Min instances = 1-2 for low latency

### Estimated Monthly Costs

**Startup (Low Traffic)**
- Cloud SQL: $10-30
- Redis: $50-75
- Cloud Run: $10-50 (based on requests)
- **Total: ~$70-155/month**

**Production (Medium Traffic)**
- Cloud SQL: $100-200
- Redis: $150-200
- Cloud Run: $100-300
- **Total: ~$350-700/month**

## Troubleshooting

### Database Connection Issues

```bash
# Test connection from Cloud Shell
gcloud sql connect $DB_INSTANCE_NAME --user=ai_visibility

# Check Cloud Run logs
gcloud run services logs read ai-visibility-api --region $REGION --limit 50
```

### Migration Failures

```bash
# Run migration job manually
gcloud run jobs execute ai-visibility-migrate --region $REGION --wait

# View migration logs
gcloud run jobs executions logs ai-visibility-migrate-execution-xxxxx --region $REGION
```

### Performance Issues

```bash
# Increase Cloud Run resources
gcloud run services update ai-visibility-api \
  --region $REGION \
  --memory 4Gi \
  --cpu 4 \
  --min-instances 2

# Scale Cloud SQL
gcloud sql instances patch $DB_INSTANCE_NAME \
  --tier=db-custom-4-15360
```

## Security Checklist

- [ ] All secrets stored in Secret Manager (not env vars)
- [ ] Cloud SQL private IP enabled
- [ ] IAM roles follow least privilege
- [ ] Cloud Armor WAF configured (if public API)
- [ ] VPC Service Controls enabled (enterprise)
- [ ] Automated backups configured
- [ ] SSL/TLS certificate for custom domain
- [ ] Audit logging enabled
- [ ] Secret rotation policy in place

## Next Steps

1. **Set up staging environment** - Duplicate setup with `--env staging`
2. **Configure auto-scaling** - Based on traffic patterns
3. **Add CDN** - Use Cloud CDN for static assets
4. **Implement caching** - Redis for frequent queries
5. **Set up alerts** - Cloud Monitoring + PagerDuty
6. **Performance testing** - Load test with realistic traffic
7. **Documentation** - API versioning strategy

## Support

For issues or questions:
- Check logs: `gcloud run services logs read ai-visibility-api`
- GCP Status: https://status.cloud.google.com/
- GitHub Issues: https://github.com/yourusername/ai-visibility/issues
