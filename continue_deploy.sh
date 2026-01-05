#!/bin/bash

##############################################################################
# 🚀 Continue Railway Deployment - Echo AI
# 
# Your project is already created! Let's finish the setup.
##############################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      🚀 Continue Railway Deployment - Echo AI             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✓ Project created: echo-ai${NC}"
echo -e "${GREEN}✓ Logged in as: Hamid Pourhasan${NC}"
echo ""

# Add PostgreSQL
echo -e "${YELLOW}[1/5]${NC} Adding PostgreSQL..."
railway add --database postgres
echo ""

# Add Redis
echo -e "${YELLOW}[2/5]${NC} Adding Redis..."
railway add --database redis
echo ""

# Set environment variables
echo -e "${YELLOW}[3/5]${NC} Setting environment variables..."

# Generate secrets
JWT_SECRET=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)

# Ask for frontend URL
echo -e "${BLUE}Enter your frontend URL (or press Enter for placeholder):${NC}"
read -p "Frontend URL [https://placeholder.vercel.app]: " FRONTEND_URL
FRONTEND_URL=${FRONTEND_URL:-https://placeholder.vercel.app}

# Set all variables
echo -e "${BLUE}Setting variables...${NC}"
railway variables --set "APP_NAME=Echo AI"
railway variables --set "APP_VERSION=1.0.0"
railway variables --set "ENVIRONMENT=production"
railway variables --set "JWT_SECRET=$JWT_SECRET"
railway variables --set "SECRET_KEY=$SECRET_KEY"
railway variables --set "FRONTEND_URL=$FRONTEND_URL"
railway variables --set "CELERY_BROKER_URL=\${{REDIS_URL}}"
railway variables --set "CELERY_RESULT_BACKEND=\${{REDIS_URL}}"
railway variables --set "MAX_WORKERS=4"
railway variables --set "REDIS_MAX_CONNECTIONS=10"
railway variables --set "REDIS_SOCKET_KEEPALIVE=true"
railway variables --set "LOG_LEVEL=INFO"
railway variables --set "STRIPE_SECRET_KEY=sk_test_placeholder"
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_placeholder"

echo -e "${GREEN}✓ Variables configured!${NC}"
echo ""

# Deploy
echo -e "${YELLOW}[4/5]${NC} Deploying application..."
railway up
echo ""

# Post-deployment
echo -e "${YELLOW}[5/5]${NC} Post-deployment steps..."
echo ""
echo -e "${BLUE}Run database migrations:${NC}"
echo -e "${GREEN}railway run alembic upgrade head${NC}"
echo ""
echo -e "${BLUE}Get your deployment URL:${NC}"
echo -e "${GREEN}railway domain${NC}"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo -e "${GREEN}railway logs --follow${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 Deployment Script Complete!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"


