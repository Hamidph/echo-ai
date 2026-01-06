#!/bin/bash

##############################################################################
# 🚀 Complete Railway Deployment - Echo AI
# Run this from: /Users/hamid/Documents/ai-visibility
##############################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🚀 Complete Railway Deployment - Echo AI              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Already done
echo -e "${GREEN}✓ Project linked: refreshing-exploration${NC}"
echo -e "${GREEN}✓ PostgreSQL added${NC}"
echo -e "${GREEN}✓ Redis added${NC}"
echo ""

# Generated secrets (already created)
JWT_SECRET="DmMNTlmJPpiEjPZcnMw/G3UAYyLviQzx23pGthrKEJ8="
SECRET_KEY="qyM33xBekcbpALOVT79DxowsIyufHpFW/DD+s0K+W4s="

echo -e "${YELLOW}[1/4]${NC} Linking to service..."
echo -e "${BLUE}You'll need to select your service from the menu${NC}"
railway service
echo ""

echo -e "${YELLOW}[2/4]${NC} Setting environment variables..."
railway variables --set "APP_NAME=Echo AI"
railway variables --set "APP_VERSION=1.0.0"
railway variables --set "ENVIRONMENT=production"
railway variables --set "JWT_SECRET=$JWT_SECRET"
railway variables --set "SECRET_KEY=$SECRET_KEY"
railway variables --set "FRONTEND_URL=https://echo-ai-production.up.railway.app"
railway variables --set "CELERY_BROKER_URL=\${{Redis.REDIS_URL}}"
railway variables --set "CELERY_RESULT_BACKEND=\${{Redis.REDIS_URL}}"
railway variables --set "MAX_WORKERS=4"
railway variables --set "REDIS_MAX_CONNECTIONS=10"
railway variables --set "REDIS_SOCKET_KEEPALIVE=true"
railway variables --set "LOG_LEVEL=INFO"
railway variables --set "STRIPE_SECRET_KEY=sk_test_placeholder"
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_placeholder"
echo -e "${GREEN}✓ Variables set!${NC}"
echo ""

echo -e "${YELLOW}[3/4]${NC} Deploying from GitHub..."
railway up
echo ""

echo -e "${YELLOW}[4/4]${NC} Running database migrations..."
railway run alembic upgrade head
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 Deployment Complete!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Get your deployment URL:${NC}"
railway domain
echo ""

echo -e "${BLUE}View logs:${NC}"
echo -e "${GREEN}railway logs --follow${NC}"
echo ""

echo -e "${BLUE}Test health endpoint:${NC}"
echo -e "${GREEN}curl \$(railway domain)/health${NC}"
echo ""



