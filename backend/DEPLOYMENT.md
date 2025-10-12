# 🚀 Railway Deployment Guide for CS2 Player Stats API

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway CLI
   ```bash
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

## 📦 Deployment Steps

### 1. Navigate to your project directory
```bash
cd /Users/johanpbj/projects/claude_area/cs2/backend
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Railway project
```bash
railway init
```
- Choose "Empty Project" or "Deploy from current directory"
- Give your project a name (e.g., "cs2-player-stats-api")

### 4. Deploy to Railway
```bash
railway up
```

This will:
- Upload your code and database to Railway
- Install dependencies from `requirements.txt`
- Start your FastAPI application using the `Procfile`
- Make your API publicly accessible

### 5. Get your deployment URL
```bash
railway domain
```

## 🔧 Configuration

### Environment Variables (Optional)
If you need to set environment variables:

```bash
# Set CORS origins for production
railway variables set ALLOWED_ORIGINS="https://yourdomain.com,https://anotherdomain.com"

# Or allow all origins (development only)
railway variables set ALLOWED_ORIGINS="*"
```

### View logs
```bash
railway logs
```

### Check deployment status
```bash
railway status
```

## 💾 Database Persistence

✅ **Your SQLite database is now persistent!**

- Configured with Railway volumes for data persistence
- Database survives deployments and restarts
- Initial database is automatically copied to persistent storage
- See `PERSISTENT_STORAGE.md` for detailed information

## 🌐 Access Your API

After deployment, your API will be available at:
- **Base URL**: `https://your-app-name.railway.app`
- **API Documentation**: `https://your-app-name.railway.app/docs`
- **Health Check**: `https://your-app-name.railway.app/health`

## 📊 API Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check (used by Railway)
- `GET /docs` - Interactive API documentation
- `GET /api/player-stats` - Get all player statistics
- `GET /api/map-stats` - Get map statistics
- `GET /api/chicken-kills` - Get chicken kill stats
- `GET /api/map-win-rates` - Get map win rates
- `GET /api/rank-info` - Get rank information
- `GET /api/kd-ratios` - Get K/D ratios
- `GET /api/kd-over-time` - Get K/D over time
- `GET /api/multi-kills` - Get multi-kill statistics
- `GET /api/utility-damage` - Get utility damage stats
- `GET /api/last-match` - Get last match information

## ⚠️ Important Notes

### Database Persistence ✅
- **Persistent Storage Configured**: SQLite database now uses Railway volumes
- **Data Survives**: Database persists across deployments and restarts  
- **Automatic Setup**: Initial database is copied to persistent volume
- **See**: `PERSISTENT_STORAGE.md` for detailed volume management

### CORS Configuration
- Currently allows all origins (`*`) for development
- Set `ALLOWED_ORIGINS` environment variable for production

## 🔄 Updates

To deploy updates:
```bash
railway up
```

## 🆘 Troubleshooting

### Check logs
```bash
railway logs --tail
```

### Connect to your service
```bash
railway shell
```

### Restart your service
```bash
railway restart
```

## 🎯 Production Recommendations

1. **Use PostgreSQL**: Add Railway's PostgreSQL addon for persistent data
2. **Configure CORS**: Set specific allowed origins
3. **Add monitoring**: Use Railway's built-in metrics
4. **Set up custom domain**: Configure your own domain name
5. **Environment separation**: Create separate Railway projects for staging/production

## 📝 Files Included

- `api_server.py` - Main FastAPI application
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process definition
- `railway.toml` - Railway configuration
- `player_stats.db` - SQLite database
- `.railwayignore` - Files to exclude from deployment
- `start.sh` - Local development script