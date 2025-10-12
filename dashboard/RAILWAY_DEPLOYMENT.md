# CS2 Dashboard - Railway Deployment Guide

This guide explains how to deploy the CS2 Dashboard to Railway and link it with your existing `cs2-player-stats-api` backend.

## Prerequisites

- Railway account
- Existing Railway backend service: `cs2-player-stats-api`
- Railway CLI installed (optional, but recommended)

## Deployment Steps

### 1. Create New Railway Service

**Option A: Using Railway Dashboard**
1. Go to your Railway project
2. Click "New Service"
3. Select "GitHub Repo"
4. Choose this repository and select the `dashboard` directory
5. Railway will auto-detect the Dockerfile

**Option B: Using Railway CLI**
```bash
cd dashboard
railway link
railway up
```

### 2. Configure Environment Variables

In the Railway dashboard for your dashboard service, add these environment variables:

```bash
VITE_API_URL=<your-backend-railway-url>
```

**Finding your backend URL:**
- Go to your `cs2-player-stats-api` service in Railway
- Click "Settings" → "Domains"
- Copy the public domain (e.g., `https://cs2-player-stats-api-production.up.railway.app`)
- Use this as your `VITE_API_URL`

**Example:**
```bash
VITE_API_URL=https://cs2-player-stats-api-production.up.railway.app
```

### 3. Configure Backend CORS

Update your backend's environment variables to allow the dashboard domain:

1. Go to your `cs2-player-stats-api` service
2. Add/update the `ALLOWED_ORIGINS` variable:

```bash
ALLOWED_ORIGINS=https://your-dashboard-domain.railway.app,http://localhost:5173
```

### 4. Deploy

Railway will automatically deploy on push. You can also manually trigger a deployment:

**Via Dashboard:**
- Click "Deploy" in your service

**Via CLI:**
```bash
railway up
```

### 5. Access Your Dashboard

Once deployed, Railway will provide a public URL for your dashboard:
- Go to Settings → Domains
- Click "Generate Domain" if one doesn't exist
- Access your dashboard at the provided URL

## Local Development

### 1. Setup Environment

Create a `.env` file in the `dashboard` directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env
VITE_API_URL=http://localhost:8000
```

### 2. Run Backend Locally

```bash
cd backend
python3 api_server.py
```

The backend will run on http://localhost:8000

### 3. Run Dashboard Locally

```bash
cd dashboard
npm install
npm run dev
```

The dashboard will run on http://localhost:5173

### 4. Test Production Build Locally

```bash
npm run build
npm run preview
```

This simulates the Railway deployment locally.

## Architecture

### Production (Railway)
```
┌─────────────────┐
│   Dashboard     │
│   (Railway)     │──────┐
└─────────────────┘      │
                         ├──> VITE_API_URL
┌─────────────────┐      │
│   Backend API   │<─────┘
│   (Railway)     │
└─────────────────┘
```

### Local Development
```
┌─────────────────┐
│   Dashboard     │
│  localhost:5173 │──────┐
└─────────────────┘      │
                         ├──> http://localhost:8000
┌─────────────────┐      │
│   Backend API   │<─────┘
│  localhost:8000 │
└─────────────────┘
```

## Troubleshooting

### Issue: 404 or routing errors
**Solution:** Ensure your preview server is configured correctly. Check `vite.config.ts`:
```typescript
export default defineConfig({
  preview: {
    port: 3000,
    strictPort: true,
  }
})
```

### Issue: CORS errors
**Solution:** Update backend's `ALLOWED_ORIGINS`:
```bash
ALLOWED_ORIGINS=https://your-dashboard.railway.app
```

### Issue: API connection timeout
**Solution:** Check if backend is running and VITE_API_URL is correct:
```bash
# Check backend health
curl https://your-backend.railway.app/health
```

### Issue: Build fails on Railway
**Solution:** Ensure all dependencies are in package.json:
```bash
npm install --save-dev @types/node
```

### Issue: Environment variables not working
**Solution:** Remember that Vite requires `VITE_` prefix for client-side env vars:
- ✅ `VITE_API_URL`
- ❌ `API_URL`

## Service Linking (Optional)

For better security, you can use Railway's internal networking:

1. In Railway dashboard, link the services
2. Use the internal URL format:
```bash
VITE_API_URL=http://cs2-player-stats-api.railway.internal:8000
```

This keeps traffic within Railway's private network.

## Monitoring

### Check Dashboard Logs
```bash
railway logs
```

### Check Backend Logs
```bash
railway logs -s cs2-player-stats-api
```

### Health Checks
- Dashboard: `https://your-dashboard.railway.app/`
- Backend: `https://your-backend.railway.app/health`

## Updating

### Automatic Deployments
Railway automatically deploys on git push to your main branch.

### Manual Redeploy
```bash
railway up
```

### Rollback
In Railway dashboard:
1. Go to "Deployments"
2. Find previous successful deployment
3. Click "Redeploy"

## Cost Optimization

- **Builds are cached:** Subsequent deployments are faster
- **Rate limiting:** Reduces API load and costs
- **Client-side caching:** 30-second cache reduces backend requests
- **Efficient Docker build:** Multi-stage build reduces image size

## Support

For issues:
1. Check Railway logs: `railway logs`
2. Verify environment variables
3. Test locally first
4. Check CORS configuration
