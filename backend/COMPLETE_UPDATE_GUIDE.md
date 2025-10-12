# 🔄 SQLite Database Update - Complete Guide

## 📋 Summary: How to Update Your SQLite Database

I've created multiple approaches for updating your persistent SQLite database on Railway. Here are your options:

## 🎯 **Option 1: Command Line Tool (Easiest)**

Use the `update_database.py` script I created:

### Quick Examples:
```bash
# Show database summary
python update_database.py summary

# Create backup
python update_database.py backup

# Add new player stats
python update_database.py add '{"match_id":"new_match_001","name":"NewPlayer","kills_total":25,"deaths_total":10,"dmg":2500}'

# Update existing player
python update_database.py update match_123 PlayerName '{"kills_total":30,"dmg":2800}'

# Delete player from match
python update_database.py delete match_123 PlayerName

# Import from CSV
python update_database.py import-csv new_stats.csv

# Export to CSV  
python update_database.py export-csv backup_stats.csv
```

### On Railway (via Railway CLI):
```bash
# Connect to your deployed service
railway shell

# Upload your update script
# (you'll need to include update_database.py in your deployment)

# Run updates on live database
python update_database.py summary
python update_database.py add '{"match_id":"live_match","name":"LivePlayer","kills_total":20,"deaths_total":5,"dmg":1800}'
```

## 🚀 **Option 2: Add API Endpoints (Most Flexible)**

Add CRUD endpoints to your FastAPI application by incorporating the code from `api_endpoints_crud.py`:

### Features:
- ✅ **POST** `/api/player-stats` - Create new player stats
- ✅ **PUT** `/api/player-stats/{match_id}/{player_name}` - Update existing stats  
- ✅ **DELETE** `/api/player-stats/{match_id}/{player_name}` - Delete player stats
- ✅ **DELETE** `/api/match-stats/{match_id}` - Delete entire match
- ✅ **POST** `/api/bulk/player-stats` - Bulk create multiple records
- ✅ **API Key Authentication** for security

### Usage Example:
```bash
# Set API key on Railway
railway variables set API_KEY=your-super-secret-key

# Create new player stats via API
curl -X POST "https://your-app.railway.app/api/player-stats" \
  -H "api-key: your-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "api_match_001",
    "name": "APIPlayer", 
    "kills_total": 35,
    "deaths_total": 8,
    "dmg": 3200
  }'
```

## 🖥️ **Option 3: Direct Database Access**

Connect directly to Railway and use SQLite commands:

```bash
# Connect to Railway service
railway shell

# Access SQLite database directly
sqlite3 /app/data/player_stats.db

# Run SQL commands
INSERT INTO player_stats (match_id, name, kills_total, deaths_total, dmg, created_at) 
VALUES ('direct_001', 'DirectPlayer', 28, 12, 2800, datetime('now'));

UPDATE player_stats SET kills_total = 32 WHERE match_id = 'direct_001' AND name = 'DirectPlayer';

DELETE FROM player_stats WHERE match_id = 'old_match';

.quit
```

## 📊 **Option 4: CSV Import/Export**

Use the database updater for bulk operations:

### Export Current Data:
```bash
python update_database.py export-csv current_stats.csv
```

### Import New Data:
```bash
# Prepare CSV file with columns: match_id,name,kills_total,deaths_total,dmg,...
python update_database.py import-csv new_batch_stats.csv
```

## 🔒 **Security & Best Practices**

### 1. Always Backup First:
```bash
# Local backup
python update_database.py backup

# Railway backup
railway shell
cp /app/data/player_stats.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Use API Keys for Web Endpoints:
```bash
railway variables set API_KEY=a-very-long-random-secret-key-here
```

### 3. Validate Data:
- The updater script includes validation
- API endpoints include Pydantic validation
- SQLite constraints prevent invalid data

## 📋 **Which Method Should You Use?**

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Command Line Tool** | One-off updates, imports | Simple, safe, validated | Manual process |
| **API Endpoints** | Real-time updates, apps | Programmatic, flexible | Requires code changes |
| **Direct SQL** | Complex queries, bulk ops | Full control, powerful | Manual, less safe |
| **CSV Import** | Large data migrations | Bulk operations | Requires file preparation |

## 🎯 **Recommended Approach**

1. **Development**: Use command line tool (`update_database.py`)
2. **Production Updates**: Add API endpoints for real-time updates  
3. **Bulk Operations**: Use CSV import/export
4. **Emergency**: Direct SQLite access via Railway shell

## 📁 **Files Created for Database Updates**

- ✅ `update_database.py` - Command line database updater
- ✅ `api_endpoints_crud.py` - API endpoints for CRUD operations
- ✅ `DATABASE_UPDATE_GUIDE.md` - Comprehensive update guide
- ✅ Database persistence already configured with Railway volumes

## 🚀 **Quick Start**

Want to add a new player right now?

```bash
cd /Users/johanpbj/projects/claude_area/cs2/backend

# Test locally first
python update_database.py add '{"match_id":"test_001","name":"TestPlayer","kills_total":15,"deaths_total":5,"dmg":1500}'

# Deploy to Railway with the updater script
railway up

# Connect to Railway and run updates
railway shell
python update_database.py summary
```

Your SQLite database is now fully updatable with persistent storage! 🎉