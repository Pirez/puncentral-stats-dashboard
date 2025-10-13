# Environment Variable Verification Guide

This dashboard includes built-in verification to confirm that Railway environment variables are being loaded correctly.

## How It Works

When the dashboard loads, it:
1. Reads all `VITE_*` environment variables
2. Logs them to the browser console
3. Sets cookies with the values for easy inspection

## Testing Steps

### Step 1: Set Test Variable in Railway

```bash
railway variables set VITE_TEST_VARIABLE=HelloFromRailway --service dashboard
```

Or in Railway dashboard:
1. Go to your dashboard service
2. Click "Variables" tab
3. Add variable: `VITE_TEST_VARIABLE` = `HelloFromRailway`

### Step 2: Trigger Rebuild

Railway needs to rebuild the dashboard for the variable to be embedded:

**Option A: Push a commit** (easiest)
```bash
git commit --allow-empty -m "Trigger rebuild"
git push
```

**Option B: Manual redeploy**
- Railway Dashboard → Dashboard Service → Deploy → Redeploy

### Step 3: Verify in Browser

Once the build completes:

1. **Open your dashboard** in browser
2. **Open DevTools** (F12)
3. **Go to Console tab**

You should see:
```
=== Environment Variables Check ===
VITE_TEST_VARIABLE: HelloFromRailway
VITE_API_TOKEN: wK8xPl2Qv... (first 10 chars shown)
VITE_API_URL: https://your-backend.railway.app
Build timestamp: 2025-10-13T...
===================================
✓ Set cookie: test_variable=HelloFromRailway
✓ Set cookie: api_token_set=yes
```

### Step 4: Check Cookies

**In DevTools:**
1. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
2. Expand "Cookies" in the sidebar
3. Click on your domain

You should see:
- `test_variable` = `HelloFromRailway`
- `api_token_set` = `yes` (if VITE_API_TOKEN is set)

**Using JavaScript Console:**
```javascript
document.cookie
```

Output should include:
```
test_variable=HelloFromRailway; api_token_set=yes
```

## What Each Variable Shows

### VITE_TEST_VARIABLE
- **Purpose:** Test that environment variables are working
- **Expected:** Whatever value you set in Railway
- **Cookie:** Full value stored in `test_variable` cookie
- **If missing:** Shows "(not set)" in console

### VITE_API_TOKEN
- **Purpose:** Bearer token for API authentication
- **Expected:** Long random string (32+ characters)
- **Console:** Only first 10 characters shown for security
- **Cookie:** Only shows "yes"/"no", not actual token
- **If missing:** Shows "(not set)" and cookie shows "no"

### VITE_API_URL
- **Purpose:** Backend API URL
- **Expected:** Your Railway backend URL or localhost
- **Cookie:** Not stored in cookie
- **If missing:** Falls back to default (http://localhost:8000)

## Common Issues

### Issue 1: Console Shows "(not set)" for All Variables

**Cause:** Variables not set in Railway, or dashboard not rebuilt

**Fix:**
1. Verify variables are set in Railway dashboard
2. Trigger a rebuild (push commit or manual redeploy)
3. Wait for build to complete (~2-3 minutes)
4. Hard refresh browser (Ctrl+Shift+R)

### Issue 2: Old Values Showing

**Cause:** Browser cache or variables changed but not rebuilt

**Fix:**
1. Check "Build timestamp" in console - should be recent
2. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. Or clear browser cache and reload

### Issue 3: Cookies Not Showing

**Cause:** Browser privacy settings or third-party cookie blocking

**Fix:**
- Check console logs instead (more reliable)
- Ensure DevTools is open on correct domain
- Try in incognito/private browsing mode

### Issue 4: Variables Show in Console But API Still Fails

**Cause:** Tokens don't match between backend and dashboard

**Fix:**
```bash
# Check both services have same token
railway variables --service backend | grep API_TOKEN
railway variables --service dashboard | grep VITE_API_TOKEN

# They should match exactly (case-sensitive)
```

## Verification Checklist

After setting variables and rebuilding, verify:

- [ ] Console shows "Environment Variables Check" section
- [ ] Build timestamp is recent (within last few minutes)
- [ ] VITE_TEST_VARIABLE shows your test value
- [ ] VITE_API_TOKEN shows first 10 characters (not "(not set)")
- [ ] VITE_API_URL shows your backend URL
- [ ] Cookie `test_variable` contains your test value
- [ ] Cookie `api_token_set` is "yes"
- [ ] Network tab shows `Authorization: Bearer ...` header in API requests

## Testing Locally

To test locally before deploying:

```bash
cd dashboard

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=test-token-123
VITE_TEST_VARIABLE=LocalTest
EOF

# Start dev server
npm run dev

# Open browser, check console
```

## Removing Test Variable

Once you've verified environment variables are working:

```bash
# Remove from Railway
railway variables delete VITE_TEST_VARIABLE --service dashboard

# Redeploy to remove from build
git commit --allow-empty -m "Remove test variable"
git push
```

Or keep it for future debugging - it's harmless!

## Build-Time vs Runtime

**Important:** Vite environment variables are **replaced at build time**, not runtime.

This means:
- Variables are embedded into the compiled JavaScript
- Changing variables requires a rebuild
- The values are visible in the compiled code (don't put secrets!)
- Each build has fixed values from that moment

Example compiled output:
```javascript
// Before build (source):
const TEST_VAR = import.meta.env.VITE_TEST_VARIABLE;

// After build (compiled):
const TEST_VAR = "HelloFromRailway";
```

## Security Note

⚠️ **Warning:** All `VITE_*` variables are embedded in the client-side code and visible to users who inspect the JavaScript.

- **Safe:** API URLs, feature flags, public config
- **Unsafe:** API secrets, private keys, admin passwords

For the API token: It's okay to include because:
1. It's required for the dashboard to work
2. It's already sent in HTTP headers (visible in Network tab)
3. Backend validates it, so stolen tokens are useless without also accessing the backend

## Troubleshooting Commands

```bash
# Check what Railway sees
railway variables --service dashboard

# Check build logs
railway logs --service dashboard --tail

# Force rebuild
railway up --service dashboard --detach

# Watch live logs during rebuild
railway logs --service dashboard --tail
```

## Need More Help?

If environment variables still aren't loading:

1. Check Railway build logs for errors
2. Verify the build completed successfully
3. Try deploying from a clean state
4. Contact Railway support if it's a platform issue
