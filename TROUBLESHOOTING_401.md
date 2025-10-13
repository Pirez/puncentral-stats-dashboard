# Troubleshooting 401 Unauthorized Error

## What the 401 Error Means

The 401 error means API token authentication is enabled on the backend, but the request doesn't have a valid token. This is actually progress - you're no longer seeing CORS errors!

## Quick Diagnosis

### Check Backend Settings

SSH into Railway backend or check variables:
```bash
railway variables --service backend
```

Look for:
- `API_TOKEN_ENABLED` - Should be `true` or `false`
- `API_TOKEN` - The secure token (if enabled)

### Check Dashboard Settings

```bash
railway variables --service dashboard
```

Look for:
- `VITE_API_TOKEN` - Must match backend `API_TOKEN` exactly

## Solutions

### Option 1: Disable Token Authentication (Quick Test)

**Backend:**
```bash
railway variables set API_TOKEN_ENABLED=false --service backend
```

Then redeploy backend. The dashboard will work without tokens.

### Option 2: Enable Token Authentication (Recommended for Production)

#### Step 1: Generate a Secure Token

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Example output: `wK8xPl2QvZ9mNc4RtYuI0oHgFdSaEbXj1W3V6M7L5K`

#### Step 2: Set Backend Token

```bash
railway variables set API_TOKEN=wK8xPl2QvZ9mNc4RtYuI0oHgFdSaEbXj1W3V6M7L5K --service backend
railway variables set API_TOKEN_ENABLED=true --service backend
```

#### Step 3: Set Dashboard Token (Same Token!)

```bash
railway variables set VITE_API_TOKEN=wK8xPl2QvZ9mNc4RtYuI0oHgFdSaEbXj1W3V6M7L5K --service dashboard
```

#### Step 4: Redeploy Both Services

**Important:** The dashboard must be rebuilt after setting `VITE_API_TOKEN`:

1. Go to Railway dashboard (https://railway.app)
2. Select your dashboard service
3. Click "Deploy" → "Redeploy" (or "Restart")
4. Wait for build to complete

**Why redeploy?** Vite environment variables are embedded at build time, not runtime.

### Option 3: Test Locally First

Test the configuration locally before deploying:

```bash
# Backend
cd backend
export API_TOKEN=test-token-123
export API_TOKEN_ENABLED=true
export GEOLOCATION_ENABLED=false
python3 api_server.py

# Dashboard (in another terminal)
cd dashboard
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_API_TOKEN=test-token-123" >> .env
npm run dev
```

Visit http://localhost:5173 and verify it works.

## Common Issues

### Issue 1: Dashboard Shows 401 After Setting Token

**Cause:** Dashboard not rebuilt after setting `VITE_API_TOKEN`

**Solution:** Redeploy/rebuild dashboard service on Railway

### Issue 2: Tokens Don't Match

**Cause:** Different tokens on backend vs dashboard

**Solution:**
```bash
# Get backend token
railway variables --service backend | grep API_TOKEN

# Set same token on dashboard
railway variables set VITE_API_TOKEN=<same-token> --service dashboard
```

### Issue 3: Token Has Spaces or Special Characters

**Cause:** Token wasn't copied correctly

**Solution:** Use quotes when setting variables:
```bash
railway variables set API_TOKEN="your-token-here"
```

### Issue 4: Still Getting 401 After Everything

**Debugging steps:**

1. **Check backend logs:**
   ```bash
   railway logs --service backend
   ```
   Look for: "Invalid API token" or "Missing Authorization header"

2. **Check if token is being sent:**
   Open browser DevTools → Network tab → Click failed request → Headers
   Look for: `Authorization: Bearer <token>`

3. **Verify dashboard build includes token:**
   ```bash
   railway logs --service dashboard
   ```
   During build, you should NOT see the actual token (it's embedded in code)

4. **Test with curl:**
   ```bash
   # Without token (should fail)
   curl https://your-backend.railway.app/api/map-stats

   # With token (should work)
   curl -H "Authorization: Bearer your-token" https://your-backend.railway.app/api/map-stats
   ```

## Recommended Configuration for Railway

### Development/Testing
```bash
# Backend
API_TOKEN_ENABLED=false
GEOLOCATION_ENABLED=false

# Dashboard
(no token needed)
```

### Production
```bash
# Backend
API_TOKEN=<strong-random-token>
API_TOKEN_ENABLED=true
GEOLOCATION_ENABLED=true
ALLOWED_COUNTRIES=NO

# Dashboard
VITE_API_TOKEN=<same-token-as-backend>
```

## Verification Checklist

After configuration, verify:

- [ ] Backend has `API_TOKEN` set (if enabled)
- [ ] Backend has `API_TOKEN_ENABLED` set
- [ ] Dashboard has `VITE_API_TOKEN` set (same as backend)
- [ ] Dashboard was rebuilt after setting token
- [ ] Backend service restarted after setting variables
- [ ] CORS origins include dashboard URL
- [ ] Health endpoint works: `curl https://backend.railway.app/health`
- [ ] API endpoint requires token: `curl https://backend.railway.app/api/map-stats`

## Quick Fix Right Now

The fastest way to get your dashboard working:

```bash
# Disable token auth temporarily
railway variables set API_TOKEN_ENABLED=false --service backend
railway restart --service backend
```

Then your dashboard will work immediately. You can enable token auth later when ready.

## Need More Help?

Check the logs:
```bash
# Backend logs
railway logs --service backend --tail

# Dashboard logs
railway logs --service dashboard --tail
```

Or test the backend directly:
```bash
# Should work (exempt path)
curl https://your-backend.railway.app/health

# Should fail with 401 (protected path)
curl https://your-backend.railway.app/api/map-stats

# Should work with token
curl -H "Authorization: Bearer your-token" https://your-backend.railway.app/api/map-stats
```
