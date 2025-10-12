# 🚀 Puncentral Stats Dashboard - Full Deployment Guide

This guide covers deploying both the **backend API** and **frontend dashboard** to Railway from a single monorepo.

## 📋 Table of Contents
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Railway Deployment](#railway-deployment)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## 📁 Repository Structure

```
cs2/
├── backend/           # FastAPI backend
│   ├── api_server.py
│   ├── requirements.txt
│   ├── railway.toml
│   └── Procfile
├── dashboard/         # React frontend
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── railway.toml
└── .gitignore
```

---

## ✅ Prerequisites

1. **GitHub Repository**: Already created at `git@github.com:Pirez/puncentral-stats-dashboard.git` ✅
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Railway CLI** (optional but recommended):
   ```bash
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

---

## 🚂 Railway Deployment

### Method 1: Using Railway Dashboard (Recommended)

#### Step 1: Deploy Backend

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select `Pirez/puncentral-stats-dashboard`
4. Railway will detect multiple services. Choose **backend** first
5. Configure the backend service:
   - **Root Directory**: `backend`
   - **Build Command**: (auto-detected from Procfile)
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
6. Click **"Deploy"**

**Set Environment Variables** (optional):
- Go to **Variables** tab
- Add: `ALLOWED_ORIGINS=*` (or specific domains for production)

**Get Backend URL**:
- Go to **Settings** → **Domains**
- Click **"Generate Domain"**
- Copy the URL (e.g., `https://cs2-player-stats-api-production.up.railway.app`)

#### Step 2: Deploy Dashboard

1. In the same Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → `Pirez/puncentral-stats-dashboard`
3. Configure the dashboard service:
   - **Root Directory**: `dashboard`
   - **Builder**: Dockerfile (auto-detected)
4. **Set Environment Variables**:
   - `VITE_API_URL=<your-backend-url-from-step-1>`
   - Example: `VITE_API_URL=https://cs2-player-stats-api-production.up.railway.app`
5. Click **"Deploy"**

**Generate Dashboard URL**:
- Go to **Settings** → **Domains**
- Click **"Generate Domain"**
- Your dashboard will be live at this URL!

#### Step 3: Configure Backend CORS

1. Go back to your **backend service**
2. Update the `ALLOWED_ORIGINS` variable:
   ```
   ALLOWED_ORIGINS=https://your-dashboard-domain.railway.app,http://localhost:5173
   ```
3. Redeploy the backend

---

### Method 2: Using Railway CLI

#### 1. Login to Railway
```bash
railway login
```

#### 2. Create New Project
```bash
railway init
```
- Choose **"Empty Project"**
- Name it: `puncentral-stats`

#### 3. Link GitHub Repository
```bash
railway link
```
- Select your project
- Connect the GitHub repo

#### 4. Deploy Backend
```bash
cd /Users/johanpbj/projects/claude_area/cs2/backend
railway up
```

Get the backend URL:
```bash
railway domain
```

#### 5. Deploy Dashboard
```bash
cd /Users/johanpbj/projects/claude_area/cs2/dashboard
railway up
```

Set the API URL:
```bash
railway variables set VITE_API_URL=https://your-backend-url.railway.app
```

Generate dashboard domain:
```bash
railway domain
```

---

## 💻 Local Development

### Backend Setup

1. **Navigate to backend**:
   ```bash
   cd /Users/johanpbj/projects/claude_area/cs2/backend
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python3 api_server.py
   ```
   Backend runs on `http://localhost:8000`

### Dashboard Setup

1. **Navigate to dashboard**:
   ```bash
   cd /Users/johanpbj/projects/claude_area/cs2/dashboard
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`**:
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

4. **Install dependencies**:
   ```bash
   npm install
   ```

5. **Run development server**:
   ```bash
   npm run dev
   ```
   Dashboard runs on `http://localhost:5173`

### Test Production Build Locally

```bash
cd dashboard
npm run build
npm run preview
```
Preview runs on `http://localhost:3000`

---

## 🔧 Environment Variables

### Backend
| Variable | Description | Example |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://your-dashboard.railway.app,http://localhost:5173` |
| `PORT` | Port to run on (auto-set by Railway) | `8000` |

### Dashboard
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `https://cs2-player-stats-api-production.up.railway.app` |
| `VITE_AUTH_PASSWORD` | ❌ No | Authentication password | `your-password` |

**Important**:
- Vite requires `VITE_` prefix for client-side environment variables
- Variables must be set in Railway dashboard **before** building
- Rebuild after changing environment variables

---

## 📊 Architecture

### Production (Railway)
```
┌─────────────────────────┐
│   Dashboard (React)     │
│   Railway Service       │─────┐
│   Port: 3000            │     │
└─────────────────────────┘     │
                                │ VITE_API_URL
                                │
┌─────────────────────────┐     │
│   Backend (FastAPI)     │◄────┘
│   Railway Service       │
│   Port: 8000            │
│   + SQLite Volume       │
└─────────────────────────┘
```

### Local Development
```
┌─────────────────────────┐
│   Dashboard             │
│   localhost:5173        │─────┐
└─────────────────────────┘     │
                                │ http://localhost:8000
                                │
┌─────────────────────────┐     │
│   Backend API           │◄────┘
│   localhost:8000        │
│   + SQLite DB           │
└─────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Issue: CORS Errors

**Symptoms**:
```
Access to fetch at 'https://backend...' from origin 'https://dashboard...' has been blocked by CORS
```

**Solution**:
1. Go to backend service in Railway
2. Add/update `ALLOWED_ORIGINS` variable:
   ```
   ALLOWED_ORIGINS=https://your-dashboard.railway.app
   ```
3. Redeploy backend

### Issue: Dashboard Can't Connect to Backend

**Symptoms**: Network timeout, connection refused

**Solution**:
1. Check backend is deployed and running:
   ```bash
   curl https://your-backend.railway.app/health
   ```
2. Verify `VITE_API_URL` is set correctly in dashboard service
3. Ensure backend URL includes `https://`
4. Rebuild dashboard after changing `VITE_API_URL`

### Issue: Environment Variables Not Working

**Solution**:
- ✅ Use: `VITE_API_URL` (correct)
- ❌ Not: `API_URL` (wrong - missing VITE_ prefix)
- Rebuild after changing variables
- Check variables are set in Railway dashboard

### Issue: 404 Errors on Dashboard Routes

**Solution**:
- Ensure `vite.config.ts` has preview configuration:
  ```typescript
  preview: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true,
  }
  ```
- Dockerfile uses correct preview command

### Issue: Build Fails on Railway

**Check logs**:
```bash
railway logs
```

**Common fixes**:
- Ensure `package.json` has all dependencies
- Check Dockerfile syntax
- Verify `railway.toml` configuration
- Ensure root directory is set correctly

---

## 📈 Monitoring

### View Backend Logs
```bash
cd backend
railway logs --tail
```

### View Dashboard Logs
```bash
cd dashboard
railway logs --tail
```

### Check Health
- Backend: `https://your-backend.railway.app/health`
- Dashboard: `https://your-dashboard.railway.app/`
- API Docs: `https://your-backend.railway.app/docs`

---

## 🔄 Updating

### Automatic Deployments
Railway automatically deploys on git push to main:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

### Manual Redeploy
Using CLI:
```bash
cd backend  # or dashboard
railway up
```

Using Dashboard:
- Go to service
- Click "Deploy" → "Redeploy"

### Rollback
1. Go to **Deployments** tab
2. Find previous successful deployment
3. Click **"Redeploy"**

---

## 🎯 Production Checklist

- [ ] Backend deployed on Railway
- [ ] Dashboard deployed on Railway
- [ ] `VITE_API_URL` set in dashboard service
- [ ] `ALLOWED_ORIGINS` set in backend service
- [ ] Backend health check returns 200: `/health`
- [ ] Dashboard loads and connects to backend
- [ ] Custom domains configured (optional)
- [ ] Railway volumes configured for backend database
- [ ] Rate limiting working (check browser console)
- [ ] Authentication working (if enabled)

---

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Backend Deployment Guide**: See `backend/DEPLOYMENT.md`
- **Dashboard Deployment Guide**: See `dashboard/RAILWAY_DEPLOYMENT.md`
- **Railway Status**: https://status.railway.app

---

## 🔐 Security Notes

- **Environment Variables**: Never commit `.env` files
- **CORS**: Set specific origins in production (not `*`)
- **Rate Limiting**: Already configured (100/min backend, 50/min frontend)
- **Authentication**: Consider adding AUTH_PASSWORD for production
- **HTTPS**: Railway provides automatic SSL certificates

---

**Repository**: https://github.com/Pirez/puncentral-stats-dashboard

**Happy Deploying! 🎉**
