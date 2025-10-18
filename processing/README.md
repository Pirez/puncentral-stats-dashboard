# CS2 Demo Processor - Railway Deployment

This service downloads CS2 demos from Steam and parses/uploads stats to your API backend.

## Railway Cron Job Setup

This service is designed to run as a **Railway Cron Job** that executes every hour.

### 1. Deploy to Railway

```bash
cd cs2/processing
railway up
```

### 2. Configure Railway Cron Schedule

In Railway dashboard:
1. Go to your service settings
2. Navigate to **Cron** section
3. Set schedule: `0 * * * *` (runs every hour at minute 0)
4. The service will automatically run `python cs2_processor.py`

### 3. Set Environment Variables

Add these in Railway's environment variables section:

```bash
# Steam Authentication (get from .steamlogin file)
steam_token=YOUR_STEAM_LOGIN_TOKEN

# Steam cookies (get from browser while logged into steamcommunity.com)
sessionid=YOUR_SESSION_ID
cookieSettings=YOUR_COOKIE_SETTINGS
broswerid=YOUR_BROWSER_ID
steamCountry=YOUR_COUNTRY_CODE
timezoneOffset=YOUR_TIMEZONE_OFFSET

# Configuration
download_folder=.tmp
clean=true

# API Configuration (use Railway internal networking)
CS2_API_URL=http://backend.railway.internal:8000
CS2_API_TOKEN=your_api_token_here
```

### 4. How It Works

- **Cron triggers**: Every hour at minute 0 (1:00, 2:00, 3:00, etc.)
- **Downloads**: Fetches latest demos from Steam
- **Parses**: Analyzes demo files and extracts stats
- **Uploads**: Sends data to backend API via Railway internal network
- **Cleans**: Deletes demos 3 hours after processing (saves storage)

### Railway Internal Networking

The service uses Railway's internal networking to communicate with your backend:
- Internal URL: `http://backend.railway.internal:8000`
- This is faster and more secure than public URLs
- No external bandwidth usage between services

### Monitoring

View logs in Railway dashboard or via CLI:

```bash
railway logs
```

### Manual Testing

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run once
python cs2_processor.py

# Or with specific mode
python cs2_processor.py --mode download  # Only download
python cs2_processor.py --mode parse     # Only parse
```

### Modes

- `--mode all` (default): Download and parse demos
- `--mode download`: Only download demos from Steam
- `--mode parse`: Only parse and upload existing demos
- `--clean`: Enable cleanup (demos deleted after 3 hours)

### Files

- `cs2_processor.py` - Main script combining download and parse
- `get_data.py` - Downloads demos from Steam
- `parse_demo.py` - Parses demos and uploads to API
- `railway.json` - Railway configuration
- `requirements.txt` - Python dependencies
