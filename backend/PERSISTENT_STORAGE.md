# 💾 Railway Persistent SQLite Setup Guide

## Overview

Railway supports persistent volumes that survive deployments and restarts. This guide shows you how to configure your CS2 Player Stats API with persistent SQLite storage.

## 🔧 Configuration

### 1. Railway Volume Configuration

The `railway.toml` file is already configured with a persistent volume:

```toml
[[deploy.volumes]]
mountPath = "/app/data"
name = "cs2_database_volume"
```

This creates a 1GB persistent volume mounted at `/app/data`.

### 2. Database Path Configuration

The API server automatically:
- Uses `/app/data/player_stats.db` in Railway (persistent)
- Falls back to `./player_stats.db` for local development
- Copies your initial database to the volume on first run

## 🚀 Deployment with Persistent Storage

### Option 1: Using the Deploy Script
```bash
./deploy.sh
```

### Option 2: Manual Deployment
```bash
railway login
railway init
railway up
```

### Option 3: Railway CLI with Volume Management
```bash
# Deploy with volumes
railway up

# Check volume status
railway status

# View volume information
railway volumes list
```

## 📊 How It Works

1. **First Deployment**: Your initial `player_stats.db` is copied to the persistent volume
2. **Subsequent Deployments**: The database in the volume is preserved
3. **App Restarts**: Database persists across restarts
4. **New Deployments**: Database data remains intact

## 🔍 Verifying Persistence

After deployment, you can verify persistence:

```bash
# Check if volume is mounted
railway shell
ls -la /app/data/

# View database file
file /app/data/player_stats.db
```

## 📈 Volume Management

### Check Volume Usage
```bash
railway volumes list
```

### Volume Backup (Important!)
Railway volumes are persistent but you should still backup:

```bash
# Connect to your service
railway shell

# Create backup
cp /app/data/player_stats.db /tmp/backup_$(date +%Y%m%d_%H%M%S).db

# Download backup (from another terminal)
railway connect
# Then download the backup file
```

## ⚠️ Important Considerations

### Volume Size
- Default: 1GB volume (sufficient for most SQLite databases)
- Can be increased if needed through Railway dashboard

### Backup Strategy
- **Critical**: Always backup your database before major deployments
- Consider automated backups for production
- SQLite files can be easily copied/downloaded

### Performance
- Volumes are network-attached storage
- Good performance for SQLite workloads
- Consider PostgreSQL for high-traffic applications

## 🆚 Alternatives

### Option 1: Railway PostgreSQL (Recommended for Production)
```bash
# Add PostgreSQL addon
railway add postgresql

# Update your code to use PostgreSQL connection string
# Available as DATABASE_URL environment variable
```

### Option 2: External Database
- Use external PostgreSQL (AWS RDS, Supabase, etc.)
- Set connection string as environment variable

## 🔧 Migrating to PostgreSQL (Optional)

If you want to migrate to PostgreSQL for better scalability:

1. **Add PostgreSQL addon in Railway dashboard**
2. **Update requirements.txt**:
   ```
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   pandas==2.1.3
   pydantic==2.5.0
   psycopg2-binary==2.9.7
   sqlalchemy==2.0.23
   ```
3. **Update database connection code**
4. **Migrate data from SQLite to PostgreSQL**

## 🎯 Best Practices

1. **Backup Regularly**: Download database backups periodically
2. **Monitor Volume Usage**: Check volume usage in Railway dashboard
3. **Test Persistence**: Verify data persists after deployments
4. **Consider Migration**: For high-traffic apps, consider PostgreSQL

## 📋 Current Setup Summary

✅ **Persistent Volume**: Configured at `/app/data`  
✅ **Automatic Initialization**: Copies initial DB on first run  
✅ **Local Development**: Falls back to current directory  
✅ **Health Check**: Verifies database connectivity  
✅ **Backup Ready**: Easy to download and backup  

Your SQLite database will now persist across deployments and restarts!