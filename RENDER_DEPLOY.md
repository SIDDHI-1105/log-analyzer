# Deploy to Render

This guide walks you through deploying the Log Analyzer to Render using their free tier.

## Architecture

| Service | Type | Purpose |
|---------|------|---------|
| log-analyzer-backend | Web Service | FastAPI backend API |
| log-analyzer-frontend | Static Site | React frontend (CDN) |
| log-analyzer-db | PostgreSQL | Database (free tier) |

## Prerequisites

1. Render account (free)
2. GitHub repository with your code pushed
3. GitHub account connected to Render

## Step 1: Push Code to GitHub

Run these commands to commit all Render config files:

    git add render.yaml backend/build.sh backend/start.sh frontend/src/lib/api.ts
    git commit -m "feat(deploy): add Render deployment configuration"
    git push origin main

## Step 2: Deploy Using Blueprint

1. Go to dashboard.render.com
2. Click New + then Blueprint
3. Connect your GitHub repository
4. Render will read render.yaml and create all services automatically

## Step 3: Verify Deployment

- Backend Health: https://your-backend-url.onrender.com/health
- API Docs: https://your-backend-url.onrender.com/docs
- Frontend: https://your-frontend-url.onrender.com

## Free Tier Limits

- Web Service: Spins down after 15 min idle (cold start ~30s)
- PostgreSQL: 1 GB storage, shared CPU
- Static Site: Unlimited bandwidth, global CDN

## Updating After Deployment

Just push to GitHub - Render auto-deploys.
