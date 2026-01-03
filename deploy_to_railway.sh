#!/bin/bash

##############################################################################
# 🚂 Railway Deployment Script for Echo AI
# 
# This script will guide you through deploying Echo AI to Railway.
# Run this script in your terminal to deploy the application.
##############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🚂 Railway Deployment - Echo AI Platform          ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Step 1: Check if Railway CLI is installed
echo -e "${YELLOW}[1/7]${NC} Checking Railway CLI installation..."
if ! command -v railway &> /dev/null; then
    echo -e "${RED}✗ Railway CLI not found!${NC}"
    echo -e "${YELLOW}Installing Railway CLI via Homebrew...${NC}"
    brew install railway
    echo -e "${GREEN}✓ Railway CLI installed successfully!${NC}"
else
    echo -e "${GREEN}✓ Railway CLI is already installed ($(railway --version))${NC}"
fi
echo ""

# Step 2: Login to Railway
echo -e "${YELLOW}[2/7]${NC} Authenticating with Railway..."
echo -e "${BLUE}This will open a browser window for authentication...${NC}"
railway login
echo -e "${GREEN}✓ Successfully authenticated!${NC}"
echo ""

# Step 3: Initialize or link project
echo -e "${YELLOW}[3/7]${NC} Setting up Railway project..."
if [ -f ".railway/config.json" ]; then
    echo -e "${BLUE}Found existing Railway configuration${NC}"
    railway status
else
    echo -e "${BLUE}Creating new Railway project...${NC}"
    railway init
fi
echo ""

# Step 4: Add PostgreSQL database
echo -e "${YELLOW}[4/7]${NC} Setting up PostgreSQL database..."
echo -e "${BLUE}Adding PostgreSQL to your project...${NC}"
railway add --database postgres || echo -e "${YELLOW}PostgreSQL might already exist${NC}"
echo -e "${GREEN}✓ PostgreSQL configured!${NC}"
echo ""

# Step 5: Add Redis
echo -e "${YELLOW}[5/7]${NC} Setting up Redis cache..."
echo -e "${BLUE}Adding Redis to your project...${NC}"
railway add --database redis || echo -e "${YELLOW}Redis might already exist${NC}"
echo -e "${GREEN}✓ Redis configured!${NC}"
echo ""

# Step 6: Set environment variables
echo -e "${YELLOW}[6/7]${NC} Configuring environment variables..."
echo -e "${BLUE}Setting up essential environment variables...${NC}"

# Core Settings
railway variables --set "APP_NAME=Echo AI"
railway variables --set "APP_VERSION=1.0.0"
railway variables --set "ENVIRONMENT=production"

# Security
echo -e "${YELLOW}⚠️  Generating secure JWT secret...${NC}"
JWT_SECRET=$(openssl rand -base64 32)
railway variables --set "JWT_SECRET=$JWT_SECRET"

echo -e "${YELLOW}⚠️  Generating secure secret key...${NC}"
SECRET_KEY=$(openssl rand -base64 32)
railway variables --set "SECRET_KEY=$SECRET_KEY"

# CORS (you'll need to update this after frontend deployment)
echo -e "${YELLOW}Enter your frontend URL (e.g., https://echo-ai.vercel.app):${NC}"
read -p "Frontend URL: " FRONTEND_URL
railway variables --set "FRONTEND_URL=$FRONTEND_URL"

# Worker Settings
railway variables --set "CELERY_BROKER_URL=\${{REDIS_URL}}"
railway variables --set "CELERY_RESULT_BACKEND=\${{REDIS_URL}}"
railway variables --set "MAX_WORKERS=4"

# Redis Settings
railway variables --set "REDIS_MAX_CONNECTIONS=10"
railway variables --set "REDIS_SOCKET_KEEPALIVE=true"

# Logging
railway variables --set "LOG_LEVEL=INFO"

# Email (optional - you mentioned you have a working email)
echo -e "${YELLOW}Do you want to configure email settings now? (y/n)${NC}"
read -p "Configure email? " configure_email
if [ "$configure_email" = "y" ]; then
    read -p "SMTP Host: " SMTP_HOST
    read -p "SMTP Port: " SMTP_PORT
    read -p "SMTP Username: " SMTP_USERNAME
    read -sp "SMTP Password: " SMTP_PASSWORD
    echo ""
    read -p "From Email: " FROM_EMAIL
    
    railway variables --set "SMTP_HOST=$SMTP_HOST"
    railway variables --set "SMTP_PORT=$SMTP_PORT"
    railway variables --set "SMTP_USERNAME=$SMTP_USERNAME"
    railway variables --set "SMTP_PASSWORD=$SMTP_PASSWORD"
    railway variables --set "FROM_EMAIL=$FROM_EMAIL"
fi

# Stripe (you mentioned you'll add this later)
echo -e "${YELLOW}Stripe configuration (you can update these later):${NC}"
railway variables --set "STRIPE_SECRET_KEY=sk_test_placeholder"
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_placeholder"

echo -e "${GREEN}✓ Environment variables configured!${NC}"
echo ""

# Step 7: Deploy
echo -e "${YELLOW}[7/7]${NC} Deploying to Railway..."
echo -e "${BLUE}Starting deployment...${NC}"
railway up

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 Deployment Complete!                   ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Get deployment URL
DEPLOYMENT_URL=$(railway domain 2>/dev/null || echo "Check Railway dashboard for your URL")
echo -e "${BLUE}🌐 Your API URL: ${YELLOW}$DEPLOYMENT_URL${NC}"
echo ""

# Post-deployment steps
echo -e "${YELLOW}📋 Post-Deployment Steps:${NC}"
echo ""
echo -e "1. ${BLUE}Run Database Migrations:${NC}"
echo -e "   ${GREEN}railway run alembic upgrade head${NC}"
echo ""
echo -e "2. ${BLUE}Check Health:${NC}"
echo -e "   ${GREEN}curl $DEPLOYMENT_URL/health${NC}"
echo ""
echo -e "3. ${BLUE}View Logs:${NC}"
echo -e "   ${GREEN}railway logs${NC}"
echo ""
echo -e "4. ${BLUE}Open Dashboard:${NC}"
echo -e "   ${GREEN}railway open${NC}"
echo ""
echo -e "5. ${BLUE}Deploy Frontend to Vercel:${NC}"
echo -e "   - Update ${YELLOW}frontend/.env.local${NC} with:"
echo -e "     ${GREEN}NEXT_PUBLIC_API_URL=$DEPLOYMENT_URL${NC}"
echo -e "   - Deploy: ${GREEN}cd frontend && vercel --prod${NC}"
echo ""
echo -e "6. ${BLUE}Update CORS:${NC}"
echo -e "   - After frontend deployment, update FRONTEND_URL:"
echo -e "     ${GREEN}railway variables --set FRONTEND_URL=<your-vercel-url>${NC}"
echo ""
echo -e "${GREEN}✨ Your Echo AI platform is now live!${NC}"
echo ""

