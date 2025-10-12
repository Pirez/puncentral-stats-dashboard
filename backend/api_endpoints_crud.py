# Database Update API Endpoints
# Add these to your api_server.py for CRUD operations

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Pydantic models for database updates
class PlayerStatsCreate(BaseModel):
    match_id: str = Field(..., description="Unique match identifier")
    kills_total: int = Field(..., ge=0, description="Total kills")
    deaths_total: int = Field(..., ge=0, description="Total deaths") 
    dmg: int = Field(..., ge=0, description="Total damage dealt")
    utility_dmg: int = Field(default=0, ge=0, description="Utility damage")
    headshot_kills_total: int = Field(default=0, ge=0, description="Headshot kills")
    ace_rounds_total: int = Field(default=0, ge=0, description="Ace rounds")
    quad_rounds_total: int = Field(default=0, ge=0, description="Quad kill rounds")
    triple_rounds_total: int = Field(default=0, ge=0, description="Triple kill rounds")
    mvps: int = Field(default=0, ge=0, description="MVP awards")
    name: str = Field(..., description="Player name")

class PlayerStatsUpdate(BaseModel):
    kills_total: Optional[int] = Field(None, ge=0)
    deaths_total: Optional[int] = Field(None, ge=0)
    dmg: Optional[int] = Field(None, ge=0)
    utility_dmg: Optional[int] = Field(None, ge=0)
    headshot_kills_total: Optional[int] = Field(None, ge=0)
    ace_rounds_total: Optional[int] = Field(None, ge=0)
    quad_rounds_total: Optional[int] = Field(None, ge=0)
    triple_rounds_total: Optional[int] = Field(None, ge=0)
    mvps: Optional[int] = Field(None, ge=0)

class MapStatsCreate(BaseModel):
    match_id: str = Field(..., description="Unique match identifier")
    map_name: str = Field(..., description="Map name")
    date_time: str = Field(..., description="Match date and time")
    won: int = Field(..., ge=0, le=1, description="1 if won, 0 if lost")

# API Key authentication (optional)
API_KEY = os.getenv("API_KEY", "your-secret-api-key")

def verify_api_key(api_key: str = Header(None)):
    """Verify API key for write operations"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# CRUD Endpoints

@app.post("/api/player-stats", status_code=201)
async def create_player_stats(
    player_data: PlayerStatsCreate,
    api_key: str = Depends(verify_api_key)
):
    """Add new player statistics record"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if record already exists
        cursor.execute(
            "SELECT COUNT(*) FROM player_stats WHERE match_id = ? AND name = ?",
            (player_data.match_id, player_data.name)
        )
        
        if cursor.fetchone()[0] > 0:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail=f"Player stats already exist for {player_data.name} in match {player_data.match_id}"
            )
        
        # Insert new record
        created_at = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO player_stats 
            (match_id, kills_total, deaths_total, dmg, utility_dmg, 
             headshot_kills_total, ace_rounds_total, 
             quad_rounds_total, triple_rounds_total, mvps, name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_data.match_id, player_data.kills_total, player_data.deaths_total,
            player_data.dmg, player_data.utility_dmg, player_data.headshot_kills_total,
            player_data.ace_rounds_total, player_data.quad_rounds_total,
            player_data.triple_rounds_total, player_data.mvps,
            player_data.name, created_at
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Player stats created successfully for {player_data.name}",
            "match_id": player_data.match_id,
            "player_name": player_data.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/api/player-stats/{match_id}/{player_name}")
async def update_player_stats(
    match_id: str,
    player_name: str,
    updates: PlayerStatsUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update existing player statistics"""
    try:
        # Get only non-None fields from the update model
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update fields provided")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute(
            "SELECT COUNT(*) FROM player_stats WHERE match_id = ? AND name = ?",
            (match_id, player_name)
        )
        
        if cursor.fetchone()[0] == 0:
            conn.close()
            raise HTTPException(
                status_code=404, 
                detail=f"Player stats not found for {player_name} in match {match_id}"
            )
        
        # Build UPDATE query
        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.extend([match_id, player_name])
        
        cursor.execute(f"""
            UPDATE player_stats 
            SET {set_clause}
            WHERE match_id = ? AND name = ?
        """, values)
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Player stats updated successfully for {player_name}",
            "match_id": match_id,
            "player_name": player_name,
            "updated_fields": list(update_data.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/api/player-stats/{match_id}/{player_name}")
async def delete_player_stats(
    match_id: str,
    player_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete player statistics for a specific match and player"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM player_stats WHERE match_id = ? AND name = ?",
            (match_id, player_name)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"Player stats not found for {player_name} in match {match_id}"
            )
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Player stats deleted successfully for {player_name}",
            "match_id": match_id,
            "player_name": player_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/api/match-stats/{match_id}")
async def delete_match_stats(
    match_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete all statistics for a specific match"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Delete from all related tables
        cursor.execute("DELETE FROM player_stats WHERE match_id = ?", (match_id,))
        player_deleted = cursor.rowcount
        
        cursor.execute("DELETE FROM map_stats WHERE match_id = ?", (match_id,))
        map_deleted = cursor.rowcount
        
        if player_deleted == 0 and map_deleted == 0:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"No statistics found for match {match_id}"
            )
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Match statistics deleted successfully",
            "match_id": match_id,
            "player_records_deleted": player_deleted,
            "map_records_deleted": map_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/map-stats", status_code=201)
async def create_map_stats(
    map_data: MapStatsCreate,
    api_key: str = Depends(verify_api_key)
):
    """Add new map statistics record"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO map_stats (match_id, map_name, date_time, won, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            map_data.match_id, map_data.map_name, map_data.date_time,
            map_data.won, created_at
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "message": "Map stats created successfully",
            "match_id": map_data.match_id,
            "map_name": map_data.map_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Bulk operations

@app.post("/api/bulk/player-stats")
async def bulk_create_player_stats(
    players_data: List[PlayerStatsCreate],
    api_key: str = Depends(verify_api_key)
):
    """Bulk create player statistics"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        created_count = 0
        errors = []
        
        for player_data in players_data:
            try:
                created_at = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO player_stats 
                    (match_id, kills_total, deaths_total, dmg, utility_dmg, 
                     headshot_kills_total, ace_rounds_total, 
                     quad_rounds_total, triple_rounds_total, mvps, name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_data.match_id, player_data.kills_total, player_data.deaths_total,
                    player_data.dmg, player_data.utility_dmg, player_data.headshot_kills_total,
                    player_data.ace_rounds_total, player_data.quad_rounds_total,
                    player_data.triple_rounds_total, player_data.mvps,
                    player_data.name, created_at
                ))
                created_count += 1
                
            except Exception as e:
                errors.append(f"Error creating stats for {player_data.name}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Bulk operation completed",
            "created_count": created_count,
            "total_attempted": len(players_data),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Add these imports to the top of your api_server.py file:
# from fastapi import Header, Depends, status
# from typing import List

"""
Usage Examples:

1. Create player stats:
POST /api/player-stats
Headers: api-key: your-secret-api-key
Body: {
    "match_id": "match_123",
    "name": "PlayerName", 
    "kills_total": 25,
    "deaths_total": 10,
    "dmg": 2500
}

2. Update player stats:
PUT /api/player-stats/match_123/PlayerName
Headers: api-key: your-secret-api-key
Body: {
    "kills_total": 30,
    "dmg": 2800
}

3. Delete player stats:
DELETE /api/player-stats/match_123/PlayerName
Headers: api-key: your-secret-api-key

4. Delete entire match:
DELETE /api/match-stats/match_123
Headers: api-key: your-secret-api-key

Set API key as environment variable:
railway variables set API_KEY=your-secret-api-key
"""