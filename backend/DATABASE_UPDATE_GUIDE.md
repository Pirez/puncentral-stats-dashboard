# 🔄 SQLite Database Update Guide

## Overview

There are several ways to update your persistent SQLite database on Railway. Choose the method that best fits your needs:

## 🎯 Methods for Updating Database

### 1. 🔧 **Add API Endpoints for Data Management** (Recommended)

Add POST/PUT/DELETE endpoints to your FastAPI application for dynamic updates.

#### Example: Add New Player Stats
```python
@app.post("/api/player-stats")
async def add_player_stats(player_data: PlayerStats):
    """Add new player statistics"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO player_stats 
            (match_id, kills_total, deaths_total, dmg, utility_dmg, he_dmg, 
             molotov_dmg, headshot_kills_total, ace_rounds_total, 
             quad_rounds_total, triple_rounds_total, mvps, name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_data.match_id, player_data.kills_total, player_data.deaths_total,
            player_data.dmg, player_data.utility_dmg, player_data.he_dmg,
            player_data.molotov_dmg, player_data.headshot_kills_total,
            player_data.ace_rounds_total, player_data.quad_rounds_total,
            player_data.triple_rounds_total, player_data.mvps,
            player_data.name, player_data.created_at
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Player stats added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 🖥️ **Direct Database Access via Railway CLI**

Connect directly to your deployed service and modify the database.

```bash
# Connect to your Railway service
railway shell

# Access SQLite database
sqlite3 /app/data/player_stats.db

# Run SQL commands
.tables
SELECT * FROM player_stats LIMIT 5;
INSERT INTO player_stats (...) VALUES (...);
UPDATE player_stats SET kills_total = 50 WHERE name = 'PlayerName';
DELETE FROM player_stats WHERE match_id = 'old_match';
.quit
```

### 3. 📁 **Upload New Database File**

Replace the entire database with a new one.

#### Option A: Through Code Deployment
```bash
# 1. Update your local player_stats.db file
# 2. Deploy to Railway
railway up

# The ensure_database_exists() function will preserve existing data
# To force overwrite, you'll need to delete the volume first
```

#### Option B: Direct File Upload
```bash
# Connect to service
railway shell

# Backup current database
cp /app/data/player_stats.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db

# Upload new database (you'll need to transfer file first)
# This requires copying your new database to the container
```

### 4. 🔄 **Database Migration Script**

Create a migration script for structured updates.

```python
# migrations.py
import sqlite3
import os
from datetime import datetime

def run_migration():
    """Run database migrations"""
    VOLUME_PATH = "/app/data"
    if not os.path.exists(VOLUME_PATH):
        VOLUME_PATH = "."
    
    DB_PATH = os.path.join(VOLUME_PATH, "player_stats.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Example: Add new column
    try:
        cursor.execute("ALTER TABLE player_stats ADD COLUMN new_stat INTEGER DEFAULT 0")
        print("Added new_stat column")
    except sqlite3.OperationalError:
        print("Column already exists")
    
    # Example: Update existing data
    cursor.execute("UPDATE player_stats SET new_stat = kills_total * 2")
    
    conn.commit()
    conn.close()
    print("Migration completed")

if __name__ == "__main__":
    run_migration()
```

### 5. 📊 **Bulk Data Import**

Import data from CSV or other formats.

```python
import pandas as pd
import sqlite3

def import_csv_data(csv_file_path):
    """Import data from CSV file"""
    VOLUME_PATH = "/app/data" if os.path.exists("/app/data") else "."
    DB_PATH = os.path.join(VOLUME_PATH, "player_stats.db")
    
    # Read CSV
    df = pd.read_csv(csv_file_path)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Import to database
    df.to_sql('player_stats', conn, if_exists='append', index=False)
    
    conn.close()
    print(f"Imported {len(df)} records from {csv_file_path}")
```

## 🛠️ **Implementation Examples**

### Adding CRUD Endpoints to Your API

Let me create the endpoints for you:

```python
# Add these to your api_server.py

from pydantic import BaseModel
from typing import Optional

class PlayerStatsCreate(BaseModel):
    match_id: str
    kills_total: int
    deaths_total: int
    dmg: int
    utility_dmg: int = 0
    he_dmg: int = 0
    molotov_dmg: int = 0
    headshot_kills_total: int = 0
    ace_rounds_total: int = 0
    quad_rounds_total: int = 0
    triple_rounds_total: int = 0
    mvps: int = 0
    name: str

class PlayerStatsUpdate(BaseModel):
    kills_total: Optional[int] = None
    deaths_total: Optional[int] = None
    dmg: Optional[int] = None
    # ... other fields as optional

@app.post("/api/player-stats")
async def create_player_stats(player_data: PlayerStatsCreate):
    """Add new player statistics"""
    # Implementation here...

@app.put("/api/player-stats/{match_id}/{player_name}")
async def update_player_stats(match_id: str, player_name: str, updates: PlayerStatsUpdate):
    """Update existing player statistics"""
    # Implementation here...

@app.delete("/api/player-stats/{match_id}/{player_name}")
async def delete_player_stats(match_id: str, player_name: str):
    """Delete player statistics"""
    # Implementation here...
```

## 🔒 **Security Considerations**

### API Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(token: str = Depends(security)):
    """Verify API token for write operations"""
    expected_token = os.getenv("API_TOKEN", "your-secret-token")
    if token.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return token

@app.post("/api/player-stats")
async def create_player_stats(
    player_data: PlayerStatsCreate, 
    token: str = Depends(verify_token)
):
    # Protected endpoint
```

## 📋 **Best Practices**

### 1. **Backup Before Updates**
```bash
# Always backup before major changes
railway shell
cp /app/data/player_stats.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. **Transaction Safety**
```python
def safe_database_update():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        
        # Your updates here
        cursor.execute("UPDATE ...")
        cursor.execute("INSERT ...")
        
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    finally:
        conn.close()
```

### 3. **Validation**
```python
def validate_player_data(data):
    """Validate data before database insertion"""
    if data.kills_total < 0:
        raise ValueError("Kills cannot be negative")
    if data.deaths_total < 0:
        raise ValueError("Deaths cannot be negative")
    # Add more validations...
```

## 🚀 **Quick Implementation**

Would you like me to add CRUD endpoints to your current API? I can:

1. ✅ Add POST endpoints for creating new records
2. ✅ Add PUT endpoints for updating existing records  
3. ✅ Add DELETE endpoints for removing records
4. ✅ Add bulk import functionality
5. ✅ Add authentication for write operations
6. ✅ Add data validation and error handling

Just let me know which functionality you'd like to implement!