# CS2 Player Stats API - Railway Deployment

This is a FastAPI application that serves CS2 player statistics with SQLite database.

## Files for Railway Deployment

- `requirements.txt` - Python dependencies
- `Procfile` - Railway process definition
- `railway.toml` - Railway configuration
- `api_server.py` - Main FastAPI application
- `player_stats.db` - SQLite database (will be included in deployment)

## Deployment Steps

1. **Initialize Railway project:**
   ```bash
   railway login
   railway init
   ```

2. **Deploy to Railway:**
   ```bash
   railway up
   ```

3. **Set environment variables (if needed):**
   ```bash
   railway variables set KEY=value
   ```

## Important Notes

- The SQLite database file (`player_stats.db`) will be deployed with your application
- Railway provides an ephemeral filesystem, so any changes to the database will be lost on restart
- For production use, consider using Railway's PostgreSQL addon for persistent data
- The application will be accessible at the URL provided by Railway after deployment

## API Endpoints

The API will be available at your Railway domain with endpoints like:
- `/docs` - Interactive API documentation
- `/players` - Get all players
- And other endpoints defined in the FastAPI application

## Database Persistence Warning

⚠️ **Important**: Railway's filesystem is ephemeral, meaning:
- Your SQLite database will be included in the deployment
- Any runtime changes to the database will be lost when the service restarts
- For production use, consider migrating to Railway's PostgreSQL addon

## Converting to PostgreSQL (Recommended for Production)

To use persistent storage:

1. Add PostgreSQL addon in Railway dashboard
2. Install psycopg2: Add `psycopg2-binary==2.9.7` to requirements.txt
3. Update database connection code to use PostgreSQL connection string from Railway environment variables