# API Token Authentication

This feature implements secure token-based authentication for the API using Bearer tokens.

## Features

- **Secure Token Generation**: Uses cryptographically secure random tokens
- **Bearer Authentication**: Standard HTTP Bearer token authentication
- **Timing Attack Protection**: Uses constant-time comparison to prevent timing attacks
- **Configurable**: Can be enabled/disabled via environment variables
- **Development-Friendly**: Easy to disable for local development
- **Exempt Paths**: Health check and documentation endpoints are exempt

## Implementation Details

### Files

- `api_token_auth.py`: Contains the middleware and token utilities
  - `APITokenAuthMiddleware`: FastAPI middleware for token verification
  - `generate_token()`: Helper function to generate secure tokens
  - `verify_token()`: Helper function for secure token comparison

- `api_server.py`: Updated to include the token authentication middleware
- Dashboard `services/api.ts`: Updated to send API tokens in requests

### How It Works

1. **Token Generation**: Generate a secure random token using `secrets.token_urlsafe()`
2. **Configuration**: Store token in environment variables on both backend and dashboard
3. **Request**: Dashboard sends token in `Authorization: Bearer <token>` header
4. **Verification**: Backend middleware verifies token using constant-time comparison
5. **Response**: If valid, request proceeds; if invalid, returns 401 Unauthorized

## Token Generation

### Generate a Secure Token

Run the token generator script:

```bash
cd backend
python3 api_token_auth.py
```

Output:
```
============================================================
API Token Generator
============================================================

Generated secure API token:
ABCdef123XYZ789_SecureRandomString-MoreRandomChars

Set this as your API_TOKEN environment variable:
  export API_TOKEN='ABCdef123XYZ789_SecureRandomString-MoreRandomChars'

Or in Railway:
  railway variables set API_TOKEN='ABCdef123XYZ789_SecureRandomString-MoreRandomChars'

For the dashboard .env file:
  VITE_API_TOKEN='ABCdef123XYZ789_SecureRandomString-MoreRandomChars'
============================================================
```

### Quick Command

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

## Configuration

### Backend Configuration

#### Environment Variables

**Required** (when token auth is enabled):
- `API_TOKEN`: The secure token that clients must provide
- Example: `API_TOKEN=ABCdef123XYZ789_SecureRandomString`

**Optional**:
- `API_TOKEN_ENABLED`: Set to `false` to disable token authentication (default: `true`)
- Example: `API_TOKEN_ENABLED=false`

#### Local Development

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
API_TOKEN=your-secure-token-here
API_TOKEN_ENABLED=true
```

Or disable for local development:

```bash
# backend/.env
API_TOKEN_ENABLED=false
```

#### Railway Deployment

Set environment variables in Railway dashboard:

1. Go to your backend service
2. Click on "Variables" tab
3. Add variables:
   - `API_TOKEN`: `<your-generated-token>`
   - `API_TOKEN_ENABLED`: `true`

Or use Railway CLI:

```bash
railway variables set API_TOKEN='<your-generated-token>'
railway variables set API_TOKEN_ENABLED=true
```

### Dashboard Configuration

#### Environment Variables

**Required** (when backend token auth is enabled):
- `VITE_API_TOKEN`: The API token (must match backend `API_TOKEN`)
- Example: `VITE_API_TOKEN=ABCdef123XYZ789_SecureRandomString`

#### Local Development

Create/update `.env` file in the `dashboard` directory:

```bash
# dashboard/.env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your-secure-token-here
```

#### Railway Deployment

Set environment variable in Railway dashboard:

1. Go to your dashboard service
2. Click on "Variables" tab
3. Add variable:
   - `VITE_API_TOKEN`: `<your-generated-token>` (same as backend)

Or use Railway CLI:

```bash
railway variables set VITE_API_TOKEN='<your-generated-token>'
```

**IMPORTANT**: After setting environment variables, rebuild the dashboard:
- Railway will automatically rebuild on the next deployment
- Or trigger a manual rebuild in the Railway dashboard

## Testing

### Test Token Generation

```bash
cd backend
python3 api_token_auth.py
```

### Test Backend with Token

1. **Start the backend**:
   ```bash
   cd backend
   export API_TOKEN='test-token-123'
   export API_TOKEN_ENABLED=true
   python3 api_server.py
   ```

2. **Test without token** (should fail):
   ```bash
   curl http://localhost:8000/api/map-stats
   ```

   Expected response:
   ```json
   {"detail":"Missing Authorization header"}
   ```

3. **Test with invalid token** (should fail):
   ```bash
   curl -H "Authorization: Bearer wrong-token" http://localhost:8000/api/map-stats
   ```

   Expected response:
   ```json
   {"detail":"Invalid API token"}
   ```

4. **Test with valid token** (should succeed):
   ```bash
   curl -H "Authorization: Bearer test-token-123" http://localhost:8000/api/map-stats
   ```

   Expected response: JSON data from the API

5. **Test exempt path** (should work without token):
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {"status":"healthy","database":"connected"}
   ```

### Test Dashboard Integration

1. **Configure both backend and dashboard** with the same token
2. **Start backend**:
   ```bash
   cd backend
   export API_TOKEN='test-token-123'
   python3 api_server.py
   ```

3. **Configure dashboard**:
   ```bash
   cd dashboard
   echo "VITE_API_URL=http://localhost:8000" > .env
   echo "VITE_API_TOKEN=test-token-123" >> .env
   ```

4. **Start dashboard**:
   ```bash
   npm run dev
   ```

5. **Open browser** and verify dashboard loads data successfully

### Unit Tests

Create a test file to verify token functionality:

```bash
cd backend
python3 -c "
from api_token_auth import generate_token, verify_token

# Test token generation
token1 = generate_token()
token2 = generate_token()
print(f'Generated token 1: {token1[:20]}...')
print(f'Generated token 2: {token2[:20]}...')
print(f'Tokens are different: {token1 != token2}')

# Test token verification
expected = 'test-token-123'
assert verify_token('test-token-123', expected) == True
assert verify_token('wrong-token', expected) == False
print('✓ Token verification tests passed')
"
```

## Security Considerations

### Token Security

1. **Token Strength**: Uses 32 bytes (256 bits) of entropy by default
2. **URL-Safe Encoding**: Base64 URL-safe encoding for easy use in headers
3. **Timing Attack Protection**: Uses `secrets.compare_digest()` for constant-time comparison
4. **Secure Generation**: Uses `secrets.token_urlsafe()` from Python's secrets module

### Best Practices

1. **Keep Tokens Secret**: Never commit tokens to version control
2. **Use Strong Tokens**: Use the provided generator (32+ bytes)
3. **Rotate Tokens**: Change tokens periodically
4. **Different Environments**: Use different tokens for dev/staging/production
5. **HTTPS Only**: Always use HTTPS in production to prevent token interception

### Token Storage

- **Backend**: Store in environment variables (Railway Variables or .env file)
- **Dashboard**: Store in environment variables (Vite will embed at build time)
- **Never**: Store in source code, commit to git, or expose in client-side code

## Exempt Paths

The following paths do NOT require token authentication:

- `/` - API root/info endpoint
- `/health` - Health check endpoint
- `/docs` - Interactive API documentation (Swagger UI)
- `/openapi.json` - OpenAPI schema
- `/redoc` - Alternative API documentation

These paths are useful for:
- Health checks by monitoring systems
- API documentation access
- Service discovery

## Troubleshooting

### Issue: "API_TOKEN environment variable is required"

**Cause**: Token auth is enabled but `API_TOKEN` is not set

**Solution**: Either:
1. Set `API_TOKEN` environment variable, OR
2. Disable token auth: `API_TOKEN_ENABLED=false`

### Issue: Dashboard gets 401 Unauthorized

**Causes**:
1. Token not set in dashboard environment variables
2. Token mismatch between backend and dashboard
3. Dashboard not rebuilt after setting token

**Solutions**:
1. Verify `VITE_API_TOKEN` is set in dashboard
2. Ensure tokens match exactly on both sides
3. Rebuild dashboard after changing env vars:
   ```bash
   npm run build
   ```

### Issue: Token not working after Railway deployment

**Cause**: Environment variables not set or dashboard not rebuilt

**Solutions**:
1. Verify variables are set in Railway dashboard
2. Trigger a new deployment to rebuild with new env vars
3. Check Railway logs for errors

### Issue: Health check failing

**Cause**: Health check endpoint should be exempt but might be blocked

**Solution**: Verify `/health` is in `exempt_paths` in `api_token_auth.py`

## Development Workflow

### Local Development (Token Disabled)

```bash
# Backend
cd backend
echo "API_TOKEN_ENABLED=false" > .env
python3 api_server.py

# Dashboard
cd dashboard
npm run dev
```

### Local Development (Token Enabled)

```bash
# Generate token
TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Backend
cd backend
echo "API_TOKEN=$TOKEN" > .env
echo "API_TOKEN_ENABLED=true" >> .env
python3 api_server.py

# Dashboard
cd dashboard
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_API_TOKEN=$TOKEN" >> .env
npm run dev
```

### Railway Deployment

```bash
# Generate token
TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Set backend variables
railway link  # Link to your project
railway service  # Select backend service
railway variables set API_TOKEN="$TOKEN"
railway variables set API_TOKEN_ENABLED=true

# Set dashboard variables
railway service  # Select dashboard service
railway variables set VITE_API_TOKEN="$TOKEN"

# Deploy
railway up
```

## Migration Guide

### Enabling Token Auth on Existing Deployment

1. **Generate a secure token**:
   ```bash
   python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
   ```

2. **Set backend variables**:
   - Railway: Set `API_TOKEN` and `API_TOKEN_ENABLED=true`
   - Local: Add to `.env` file

3. **Set dashboard variables**:
   - Railway: Set `VITE_API_TOKEN` (same value as backend)
   - Local: Add to `.env` file

4. **Rebuild dashboard** (important!):
   - Railway: Trigger new deployment
   - Local: Restart dev server

5. **Test the deployment**:
   - Verify dashboard still loads
   - Check API calls are successful
   - Monitor Railway logs for errors

### Disabling Token Auth

1. **Set backend variable**:
   ```bash
   API_TOKEN_ENABLED=false
   ```

2. **Remove dashboard token** (optional):
   - Can leave `VITE_API_TOKEN` set (will be ignored)
   - Or remove the variable

3. **Restart services**

## Performance Impact

- **Token Verification**: <1ms per request
- **Memory Usage**: Minimal (only stores token string)
- **No Database Lookups**: Token verified in-memory
- **Constant-Time Comparison**: Prevents timing attacks without performance penalty

## Integration with Other Middleware

Token authentication runs **before** other middleware (rate limiting, geolocation).

**Middleware Order** (from api_server.py):
1. CORS (first)
2. **API Token Authentication** ← Runs first for security
3. IP Geolocation Verification
4. Rate Limiting
5. Route Handlers

This ensures unauthenticated requests are rejected early.

## Future Enhancements

- [ ] Multiple token support (different tokens for different clients)
- [ ] Token expiration and rotation
- [ ] Token scoping (read-only vs read-write)
- [ ] Audit logging for authentication failures
- [ ] Rate limiting per token (not just per IP)
- [ ] Admin API to manage tokens

## Support

For issues or questions:
1. Review this documentation
2. Check the [troubleshooting](#troubleshooting) section
3. Verify environment variables are set correctly
4. Check Railway logs for errors
5. Test with curl commands to isolate issues
