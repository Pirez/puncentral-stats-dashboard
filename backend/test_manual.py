"""
Manual test script for IP Geolocation Middleware
Run this to verify the implementation works
"""

import asyncio
from ip_geolocation import IPGeolocationCache, IPGeolocationMiddleware


def test_cache():
    """Test the cache functionality"""
    print("Testing IPGeolocationCache...")

    cache = IPGeolocationCache(ttl_seconds=2)

    # Test 1: Set and get
    print("  Test 1: Set and get")
    cache.set("1.2.3.4", "NO")
    result = cache.get("1.2.3.4")
    assert result == "NO", f"Expected 'NO', got {result}"
    print("    ✓ Cache stores and retrieves values correctly")

    # Test 2: Cache miss
    print("  Test 2: Cache miss")
    result = cache.get("5.6.7.8")
    assert result is None, f"Expected None, got {result}"
    print("    ✓ Cache returns None for missing entries")

    # Test 3: Expiry
    print("  Test 3: Expiry (waiting 2.5 seconds...)")
    import time
    time.sleep(2.5)
    result = cache.get("1.2.3.4")
    assert result is None, f"Expected None (expired), got {result}"
    print("    ✓ Cache entries expire correctly")

    print("✓ All cache tests passed!\n")


async def test_geolocation_lookup():
    """Test actual geolocation API lookup"""
    print("Testing IP Geolocation API Lookup...")

    from fastapi import FastAPI
    app = FastAPI()
    middleware = IPGeolocationMiddleware(app, enabled=True)

    # Test with a known Norwegian IP (Telenor)
    print("  Test 1: Looking up Norwegian IP (185.13.160.1)...")
    country = await middleware._lookup_country("185.13.160.1")
    print(f"    Result: {country}")
    if country == "NO":
        print("    ✓ Norwegian IP correctly identified")
    else:
        print(f"    ! Warning: Expected 'NO', got '{country}'")

    # Test with a known Swedish IP (Telia)
    print("  Test 2: Looking up Swedish IP (81.226.0.1)...")
    country = await middleware._lookup_country("81.226.0.1")
    print(f"    Result: {country}")
    if country == "SE":
        print("    ✓ Swedish IP correctly identified")
    else:
        print(f"    ! Warning: Expected 'SE', got '{country}'")

    # Test with Google DNS (should be US)
    print("  Test 3: Looking up US IP (8.8.8.8)...")
    country = await middleware._lookup_country("8.8.8.8")
    print(f"    Result: {country}")
    if country == "US":
        print("    ✓ US IP correctly identified")
    else:
        print(f"    ! Warning: Expected 'US', got '{country}'")

    print("✓ Geolocation API tests completed!\n")


def test_local_ip_detection():
    """Test local IP detection"""
    print("Testing Local IP Detection...")

    from fastapi import FastAPI
    app = FastAPI()
    middleware = IPGeolocationMiddleware(app)

    test_cases = [
        ("127.0.0.1", True, "localhost"),
        ("192.168.1.1", True, "private network"),
        ("10.0.0.1", True, "private network"),
        ("172.16.0.1", True, "private network"),
        ("8.8.8.8", False, "public IP"),
        ("185.13.160.1", False, "Norwegian public IP"),
    ]

    all_passed = True
    for ip, expected, description in test_cases:
        result = middleware._is_local_ip(ip)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {ip} ({description}): {'local' if result else 'public'}")
        if result != expected:
            all_passed = False

    if all_passed:
        print("✓ All local IP detection tests passed!\n")
    else:
        print("✗ Some local IP detection tests failed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("IP Geolocation Middleware - Manual Test Suite")
    print("=" * 60)
    print()

    # Run synchronous tests
    test_cache()
    test_local_ip_detection()

    # Run async tests
    print("Running async tests...")
    asyncio.run(test_geolocation_lookup())

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
