# IP Geolocation Verification

This feature implements IP geolocation verification to restrict API access to Norwegian IPs only.

## Features

- **Geolocation Verification**: Verifies that incoming requests originate from Norwegian IP addresses
- **Smart Caching**: Caches IP lookups for 1 hour to minimize API calls and improve performance
- **Configurable**: Can be enabled/disabled via environment variables
- **Development-Friendly**: Automatically bypasses checks for localhost and private IPs
- **Exempt Paths**: Health check and documentation endpoints are exempt from geolocation checks

## Implementation Details

### Files

- `ip_geolocation.py`: Contains the middleware implementation
  - `IPGeolocationCache`: Simple in-memory cache with TTL support
  - `IPGeolocationMiddleware`: FastAPI middleware for geolocation verification

- `api_server.py`: Updated to include the middleware
- `requirements.txt`: Updated with `httpx` dependency
- `test_ip_geolocation.py`: Comprehensive unit tests
- `test_manual.py`: Manual test script for verification

### How It Works

1. **Request Reception**: When a request comes in, the middleware extracts the client IP
2. **Local IP Check**: If the IP is localhost or private network, the request passes through
3. **Exempt Path Check**: If the path is `/health`, `/docs`, `/openapi.json`, or `/redoc`, the request passes through
4. **Cache Lookup**: Check if we've recently looked up this IP
5. **API Lookup**: If not cached, query ip-api.com for the country code
6. **Cache Storage**: Store the result in cache for future requests
7. **Verification**: If country code is "NO" (Norway), allow; otherwise, return 403 Forbidden

### Geolocation API

Uses [ip-api.com](http://ip-api.com) free tier:
- 45 requests per minute
- No API key required
- Returns country code and status

## Configuration

### Environment Variables

- `GEOLOCATION_ENABLED`: Set to `false` to disable geolocation checks (default: `true`)
- Example: `GEOLOCATION_ENABLED=false`

### Code Configuration

In `api_server.py`:

```python
app.add_middleware(
    IPGeolocationMiddleware,
    cache_ttl=3600,  # Cache duration in seconds (1 hour)
    enabled=geolocation_enabled,  # Enable/disable via env var
    allowed_countries=["NO"]  # List of allowed country codes
)
```

### Customization Options

1. **Change allowed countries**:
   ```python
   allowed_countries=["NO", "SE", "DK"]  # Allow Nordic countries
   ```

2. **Change cache TTL**:
   ```python
   cache_ttl=1800  # Cache for 30 minutes instead
   ```

3. **Add more exempt paths**:
   Edit `ip_geolocation.py`:
   ```python
   self.exempt_paths = ["/health", "/docs", "/openapi.json", "/redoc", "/custom-path"]
   ```

## Testing

### Run Unit Tests

```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run tests
pytest test_ip_geolocation.py -v
```

### Run Manual Tests

```bash
python test_manual.py
```

This will test:
- Cache functionality
- Local IP detection
- Real geolocation API lookups

### Test the API Server

1. **Start the server**:
   ```bash
   python api_server.py
   ```

2. **Test with local IP** (should work):
   ```bash
   curl http://localhost:8000/api/map-stats
   ```

3. **Test with mock Norwegian IP** (requires proxy or actual Norwegian IP)

4. **Disable geolocation for testing**:
   ```bash
   GEOLOCATION_ENABLED=false python api_server.py
   ```

## Deployment

### Railway Deployment

The middleware is production-ready and will automatically:
- Use Railway's forwarded IP headers (`X-Forwarded-For`, `X-Real-IP`)
- Cache IP lookups to stay within API rate limits
- Fail gracefully if the geolocation API is unavailable (fails open - allows requests)

### Environment Variables in Railway

Set `GEOLOCATION_ENABLED=true` in Railway dashboard to enable the feature.

## Error Handling

- **API Timeout**: 5-second timeout on geolocation API calls
- **API Failure**: If lookup fails, defaults to allowing the request (fail-open) to avoid blocking legitimate users
- **Rate Limiting**: Cache helps stay within ip-api.com's 45 requests/minute limit

## Security Considerations

1. **Fail-Open vs Fail-Closed**: Currently fails open (allows requests if API is down). For stricter security, modify `_lookup_country` to return `None` on error.

2. **IP Spoofing**: Middleware trusts `X-Forwarded-For` and `X-Real-IP` headers. Ensure your reverse proxy/load balancer is configured to set these correctly.

3. **VPN/Proxy**: Users with Norwegian VPNs/proxies will be allowed. This is expected behavior.

## Performance Impact

- **First Request**: ~50-200ms (geolocation API lookup)
- **Cached Requests**: <1ms (cache lookup)
- **Memory Usage**: Minimal (only stores IP → country code mappings)

With 1-hour cache TTL and typical traffic patterns, API calls are minimized to <45/minute even with many users.

## Troubleshooting

### Issue: Getting 403 errors from Norwegian IPs

1. Check if geolocation is enabled: `echo $GEOLOCATION_ENABLED`
2. Test IP lookup manually:
   ```python
   import asyncio
   from ip_geolocation import IPGeolocationMiddleware
   from fastapi import FastAPI

   async def test():
       app = FastAPI()
       middleware = IPGeolocationMiddleware(app)
       result = await middleware._lookup_country("YOUR_IP_HERE")
       print(f"Country: {result}")

   asyncio.run(test())
   ```

### Issue: Too many API requests

- Increase `cache_ttl` to cache longer (e.g., 7200 for 2 hours)
- Consider implementing a persistent cache (Redis, database)

### Issue: Need to allow additional countries

Edit `api_server.py`:
```python
allowed_countries=["NO", "SE"]  # Add Sweden
```

## Future Enhancements

- [ ] Use Redis for distributed caching across multiple instances
- [ ] Add metrics/logging for blocked requests
- [ ] Implement allowlist for specific non-Norwegian IPs
- [ ] Switch to a premium geolocation service for better accuracy
- [ ] Add admin endpoint to view cache statistics
