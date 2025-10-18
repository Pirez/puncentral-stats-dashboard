import os
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from combined_security_middleware import CombinedSecurityMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter (100 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app = FastAPI(title="CS2 Player Stats API",
                version="1.0.0", 
                docs_url=None,           # Disable Swagger UI
                redoc_url=None,          # Disable ReDoc
                openapi_url=None         # Disable OpenAPI schema
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend access
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Can be configured via ALLOWED_ORIGINS env var
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add combined security middleware (token auth + geolocation)
# Configuration via environment variables:
#   API_TOKEN_ENABLED=true|false (default: true)
#   API_TOKEN=<your-secure-token> (required if API_TOKEN_ENABLED=true)
#   GEOLOCATION_ENABLED=true|false (default: true)
#   ALLOWED_COUNTRIES=NO,SE,DK (default: NO,NL)
#   GEO_CACHE_TTL=3600 (default: 3600 seconds)
#
# This replaces the previous separate API token and geolocation middlewares
# with a single, unified security layer for better robustness and maintainability
token_auth_enabled = os.getenv("API_TOKEN_ENABLED", "true").lower() == "true"
geolocation_enabled = os.getenv("GEOLOCATION_ENABLED", "true").lower() == "true"
api_token = os.getenv("API_TOKEN") if token_auth_enabled else None
allowed_countries = os.getenv("ALLOWED_COUNTRIES", "NO,NL").split(",")
cache_ttl = int(os.getenv("GEO_CACHE_TTL", "3600"))

app.add_middleware(
    CombinedSecurityMiddleware,
    token_auth_enabled=token_auth_enabled,
    api_token=api_token,
    geolocation_enabled=geolocation_enabled,
    allowed_countries=allowed_countries,
    cache_ttl=cache_ttl,
    cors_origins=allowed_origins,  # Pass CORS origins for error responses
)

# Database path - use Railway volume for persistence
# Railway volumes are mounted at the path specified in railway.toml
VOLUME_PATH = "/app/data"  # This matches the mountPath in railway.toml
DB_PATH = os.path.join(VOLUME_PATH, "player_stats.db")

# For local development, fall back to current directory
if not os.path.exists(VOLUME_PATH):
    VOLUME_PATH = "."
    DB_PATH = os.path.join(VOLUME_PATH, "player_stats.db")


# Pydantic models for responses
class PlayerStats(BaseModel):
    match_id: str
    kills_total: int
    deaths_total: int
    dmg: int
    utility_dmg: int
    headshot_kills_total: int
    ace_rounds_total: int
    quad_rounds_total: int
    triple_rounds_total: int
    mvps: int
    name: str
    created_at: str


class MapStats(BaseModel):
    match_id: str
    map_name: str
    date_time: str
    won: int
    created_at: str


class ChickenKills(BaseModel):
    name: str
    chicken: int


class MapWinRate(BaseModel):
    map_name: str
    total_matches: int
    total_wins: int
    win_ratio: float


class RankInfo(BaseModel):
    user_name: str
    rank_new: int
    rank_change: float


class KDRatio(BaseModel):
    name: str
    avg_kd: float
    last_match_kd: float
    kd_change: float


class KDOverTime(BaseModel):
    name: str
    match_id: str
    date_time: str
    map_name: str
    match_kd: float


class MultiKillStats(BaseModel):
    name: str
    total_aces: int
    total_quads: int
    total_triples: int
    total_multi_kills: int


class UtilityDamageStats(BaseModel):
    name: str
    total_utility_dmg: int
    avg_utility_dmg_per_match: float


class LastMatchPlayer(BaseModel):
    match_id: str
    kills_total: int
    deaths_total: int
    dmg: int
    utility_dmg: int
    headshot_kills_total: int
    ace_rounds_total: int
    quad_rounds_total: int
    triple_rounds_total: int
    mvps: int
    name: str
    created_at: str


class LastMatchInfo(BaseModel):
    map_name: str
    date_time: str
    won: bool


class PlayerStatsUpload(BaseModel):
    kills_total: int
    deaths_total: int
    dmg: int
    utility_dmg: int
    headshot_kills_total: int
    ace_rounds_total: int
    quad_rounds_total: int
    triple_rounds_total: int
    mvps: int
    name: str


class MapStatsUpload(BaseModel):
    map_name: str
    date_time: str
    won: int


class MatchUpload(BaseModel):
    match_id: str
    player_stats: List[PlayerStatsUpload]
    map_stats: MapStatsUpload


def ensure_database_exists():
    """Ensure database directory exists and create empty database with schema if needed"""
    import shutil

    # Create volume directory if it doesn't exist
    os.makedirs(VOLUME_PATH, exist_ok=True)
    logger.info(f"Volume path: {VOLUME_PATH}")
    logger.info(f"Database path: {DB_PATH}")

    # If database doesn't exist in volume, copy from initial location or create new
    if not os.path.exists(DB_PATH):
        initial_db_path = "./player_stats.db"  # Initial DB in deployment
        if os.path.exists(initial_db_path):
            shutil.copy2(initial_db_path, DB_PATH)
            logger.info(f"Copied initial database to persistent volume: {DB_PATH}")
        else:
            # Create empty database with schema
            logger.info(f"Creating new empty database at {DB_PATH}")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Create all required tables
            cursor.execute("""
                CREATE TABLE player_stats (
                    match_id TEXT,
                    kills_total INTEGER,
                    deaths_total INTEGER,
                    dmg INTEGER,
                    utility_dmg INTEGER,
                    headshot_kills_total INTEGER,
                    ace_rounds_total INTEGER,
                    quad_rounds_total INTEGER,
                    triple_rounds_total INTEGER,
                    mvps INTEGER,
                    name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE map_stats (
                    match_id TEXT UNIQUE,
                    map_name TEXT,
                    date_time DATETIME,
                    won INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE chicken_kills (
                    match_id TEXT,
                    name TEXT,
                    chicken INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE locations (
                    match_id TEXT,
                    name TEXT,
                    location TEXT,
                    kills INT,
                    deaths INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE rank (
                    match_id TEXT,
                    num_wins INTEGER,
                    rank_change REAL,
                    rank_new INTEGER,
                    rank_old INTEGER,
                    rank_type_id INTEGER,
                    user_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info(f"Successfully created empty database with schema at {DB_PATH}")
    else:
        logger.info(f"Database already exists at {DB_PATH}")


def get_db():
    """Get database connection"""
    ensure_database_exists()
    return sqlite3.connect(DB_PATH)


@app.get("/")
@limiter.limit("200/minute")
async def root(request: Request):
    """API root endpoint"""
    return {
        "message": "CS2 Player Stats API",
        "version": "1.0.0",
        "endpoints": [
            "/api/upload (POST)",
            "/api/player-stats",
            "/api/map-stats",
            "/api/chicken-kills",
            "/api/map-win-rates",
            "/api/rank-info",
            "/api/kd-ratios",
            "/api/kd-over-time",
            "/api/multi-kills",
            "/api/utility-damage",
            "/api/last-match",
        ],
    }


@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_match_data(request: Request, match_data: MatchUpload):
    """
    Upload match data to the database.
    Requires authentication via API token.

    Request body should contain:
    - match_id: Unique identifier for the match
    - player_stats: List of player statistics
    - map_stats: Map information and outcome
    """
    logger.info(f"Received upload request for match_id: {match_data.match_id}")
    logger.info(f"Number of players: {len(match_data.player_stats)}")
    logger.info(f"Map: {match_data.map_stats.map_name}, Won: {match_data.map_stats.won}")

    try:
        logger.info("Getting database connection...")
        conn = get_db()
        cursor = conn.cursor()

        # Check if match already exists
        logger.info(f"Checking if match {match_data.match_id} already exists...")
        cursor.execute(
            "SELECT COUNT(*) FROM map_stats WHERE match_id = ?",
            (match_data.match_id,)
        )
        if cursor.fetchone()[0] > 0:
            logger.warning(f"Match {match_data.match_id} already exists in database")
            conn.close()
            raise HTTPException(
                status_code=409,
                detail=f"Match {match_data.match_id} already exists in database"
            )

        # Insert map stats
        logger.info(f"Inserting map stats for match {match_data.match_id}...")
        cursor.execute("""
            INSERT INTO map_stats (match_id, map_name, date_time, won)
            VALUES (?, ?, ?, ?)
        """, (
            match_data.match_id,
            match_data.map_stats.map_name,
            match_data.map_stats.date_time,
            match_data.map_stats.won
        ))
        logger.info("Map stats inserted successfully")

        # Insert player stats
        logger.info(f"Inserting player stats for {len(match_data.player_stats)} players...")
        for i, player in enumerate(match_data.player_stats):
            logger.debug(f"Inserting player {i+1}/{len(match_data.player_stats)}: {player.name}")
            cursor.execute("""
                INSERT INTO player_stats (
                    match_id, kills_total, deaths_total, dmg, utility_dmg,
                    headshot_kills_total, ace_rounds_total, quad_rounds_total,
                    triple_rounds_total, mvps, name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_data.match_id,
                player.kills_total,
                player.deaths_total,
                player.dmg,
                player.utility_dmg,
                player.headshot_kills_total,
                player.ace_rounds_total,
                player.quad_rounds_total,
                player.triple_rounds_total,
                player.mvps,
                player.name
            ))
        logger.info("All player stats inserted successfully")

        logger.info("Committing transaction...")
        conn.commit()
        conn.close()
        logger.info(f"Match {match_data.match_id} uploaded successfully")

        return {
            "status": "success",
            "message": f"Match {match_data.match_id} uploaded successfully",
            "players_uploaded": len(match_data.player_stats)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading match data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading match data: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/api/player-stats", response_model=List[PlayerStats])
async def get_player_stats():
    """Get all player statistics"""
    try:
        conn = get_db()
        df = pd.read_sql("SELECT * FROM player_stats", conn)
        conn.close()
        return df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/map-stats", response_model=List[MapStats])
async def get_map_stats():
    """Get all map statistics"""
    try:
        conn = get_db()
        df = pd.read_sql("SELECT * FROM map_stats", conn)
        conn.close()
        return df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chicken-kills", response_model=List[ChickenKills])
async def get_chicken_kills():
    """Get chicken kills aggregated by player"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, SUM(chicken) AS chicken
            FROM chicken_kills
            GROUP BY name
            ORDER BY chicken DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [{"name": row[0], "chicken": row[1]} for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/map-win-rates", response_model=List[MapWinRate])
async def get_map_win_rates():
    """Get win rates by map"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                map_name, 
                COUNT(*) as total_matches,
                SUM(won) as total_wins,
                1.0 * SUM(won) / COUNT(*) as win_ratio
            FROM 
                map_stats
            GROUP BY 
                map_name
            ORDER BY 
                win_ratio DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "map_name": row[0],
                "total_matches": row[1],
                "total_wins": row[2],
                "win_ratio": row[3],
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rank-info", response_model=List[RankInfo])
async def get_rank_info():
    """Get latest rank information for all players"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                r.user_name, r.rank_new, r.rank_change
            FROM 
                rank r
            JOIN 
                (SELECT match_id FROM map_stats ORDER BY date_time DESC LIMIT 1) latest_match
            ON 
                r.match_id = latest_match.match_id
            ORDER BY 
                r.rank_new DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {"user_name": row[0], "rank_new": row[1], "rank_change": row[2]}
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kd-ratios", response_model=List[KDRatio])
async def get_kd_ratios():
    """Get K/D ratios with comparison to last match"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            WITH PlayerMatchKD AS (
                SELECT 
                    ps.name,
                    ps.match_id,
                    CAST(ps.kills_total AS FLOAT) / NULLIF(ps.deaths_total, 0) AS kd_ratio,
                    ROW_NUMBER() OVER (PARTITION BY ps.name ORDER BY ms.date_time DESC) AS match_order
                FROM 
                    player_stats ps
                JOIN 
                    map_stats ms ON ps.match_id = ms.match_id
            ),
            AverageKD AS (
                SELECT 
                    name,
                    AVG(kd_ratio) AS avg_kd
                FROM 
                    PlayerMatchKD
                WHERE 
                    match_order > 1
                GROUP BY 
                    name
            ),
            LastMatchKD AS (
                SELECT 
                    name,
                    kd_ratio AS last_match_kd
                FROM 
                    PlayerMatchKD
                WHERE 
                    match_order = 1
            )
            SELECT 
                a.name,
                a.avg_kd,
                l.last_match_kd,
                l.last_match_kd - a.avg_kd AS kd_change
            FROM 
                AverageKD a
            JOIN 
                LastMatchKD l ON a.name = l.name
            ORDER BY 
                a.avg_kd DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "name": row[0],
                "avg_kd": row[1],
                "last_match_kd": row[2],
                "kd_change": row[3],
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kd-over-time", response_model=List[KDOverTime])
async def get_kd_over_time():
    """Get K/D ratio over time for all players"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ps.name,
                ps.match_id,
                ms.date_time,
                ms.map_name,
                ROUND(CAST(ps.kills_total AS FLOAT) / NULLIF(ps.deaths_total, 0), 4) AS match_kd
            FROM 
                player_stats ps
            JOIN 
                map_stats ms ON ps.match_id = ms.match_id
            ORDER BY 
                ms.date_time, ps.name
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "name": row[0],
                "match_id": row[1],
                "date_time": row[2],
                "map_name": row[3],
                "match_kd": row[4],
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multi-kills", response_model=List[MultiKillStats])
async def get_multi_kills():
    """Get total multi-kills (aces, quads, triples) for all players"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                name,
                SUM(ace_rounds_total) AS total_aces,
                SUM(quad_rounds_total) AS total_quads,
                SUM(triple_rounds_total) AS total_triples,
                SUM(ace_rounds_total + quad_rounds_total + triple_rounds_total) AS total_multi_kills
            FROM
                player_stats
            GROUP BY
                name
            ORDER BY
                total_multi_kills DESC, total_aces DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "name": row[0],
                "total_aces": row[1],
                "total_quads": row[2],
                "total_triples": row[3],
                "total_multi_kills": row[4],
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/utility-damage", response_model=List[UtilityDamageStats])
async def get_utility_damage():
    """Get total utility damage stats for all players"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                name,
                SUM(utility_dmg) AS total_utility_dmg,
                ROUND(AVG(utility_dmg), 2) AS avg_utility_dmg_per_match
            FROM
                player_stats
            GROUP BY
                name
            ORDER BY
                total_utility_dmg DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "name": row[0],
                "total_utility_dmg": row[1],
                "avg_utility_dmg_per_match": row[2],
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/last-match")
async def get_last_match():
    """Get information about the last match played"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get player stats from last match
        cursor.execute("""
            SELECT ps.*
            FROM player_stats ps
            JOIN (
                SELECT name, MAX(created_at) AS max_created
                FROM player_stats
                GROUP BY name
            ) latest
            ON ps.name = latest.name AND ps.created_at = latest.max_created
        """)
        player_data = cursor.fetchall()
        
        # Get map info from last match
        cursor.execute("""
            SELECT map_name, date_time, won
            FROM map_stats
            ORDER BY created_at DESC
            LIMIT 1
        """)
        map_data = cursor.fetchone()
        
        conn.close()
        
        players = [
            {
                "match_id": row[0],
                "kills_total": row[1],
                "deaths_total": row[2],
                "dmg": row[3],
                "utility_dmg": row[4],
                "headshot_kills_total": row[5],
                "ace_rounds_total": row[6],
                "quad_rounds_total": row[7],
                "triple_rounds_total": row[8],
                "mvps": row[9],
                "name": row[10],
                "created_at": row[11],
            }
            for row in player_data
        ]
        
        match_info = {
            "map_name": map_data[0],
            "date_time": map_data[1],
            "won": bool(map_data[2]),
        } if map_data else None
        
        return {"players": players, "match_info": match_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting CS2 Player Stats API on port {port}")
    logger.info(f"API Token Auth: {'enabled' if token_auth_enabled else 'disabled'}")
    logger.info(f"Geolocation: {'enabled' if geolocation_enabled else 'disabled'}")
    uvicorn.run(app, host="0.0.0.0", port=port)
