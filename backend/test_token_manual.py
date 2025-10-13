"""
Manual tests for API token authentication

Run with: python3 test_token_manual.py
"""

import subprocess
import time
import signal
import sys
import os


def run_test(description, command, expected_status=None, expected_text=None):
    """Run a curl command and verify the output"""
    print(f"\n{description}")
    print(f"  Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        print(f"  Status Code: {result.returncode}")

        if result.stdout:
            print(f"  Response: {result.stdout[:200]}")

        if result.stderr and result.returncode != 0:
            print(f"  Error: {result.stderr[:200]}")

        # Check expected status
        if expected_status is not None and result.returncode == expected_status:
            print("  ✓ Status code matches expected")
        elif expected_status is not None:
            print(f"  ✗ Expected status {expected_status}, got {result.returncode}")
            return False

        # Check expected text
        if expected_text and expected_text in result.stdout:
            print("  ✓ Response contains expected text")
        elif expected_text:
            print(f"  ✗ Expected text '{expected_text}' not found in response")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("  ✗ Command timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("API Token Authentication - Manual Integration Test")
    print("=" * 60)

    # Set up test token
    test_token = "test-token-123"

    print("\n1. Starting API server with token authentication enabled...")
    env = os.environ.copy()
    env["API_TOKEN"] = test_token
    env["API_TOKEN_ENABLED"] = "true"
    env["GEOLOCATION_ENABLED"] = "false"  # Disable geolocation for testing

    server_process = subprocess.Popen(
        ["python3", "api_server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(3)

    try:
        # Test 1: Health check (should work without token - exempt path)
        print("\n" + "=" * 60)
        print("TEST 1: Health Check (Exempt Path)")
        print("=" * 60)
        run_test(
            "Health check should work without token",
            "curl -s http://localhost:8000/health",
            expected_text="healthy"
        )

        # Test 2: API endpoint without token (should fail)
        print("\n" + "=" * 60)
        print("TEST 2: Missing Token")
        print("=" * 60)
        run_test(
            "Request without token should be rejected",
            "curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/map-stats",
            expected_text="401"
        )

        # Test 3: API endpoint with invalid token (should fail)
        print("\n" + "=" * 60)
        print("TEST 3: Invalid Token")
        print("=" * 60)
        run_test(
            "Request with invalid token should be rejected",
            f"curl -s -w '\\nHTTP_CODE:%{{http_code}}' -H 'Authorization: Bearer wrong-token' http://localhost:8000/api/map-stats",
            expected_text="401"
        )

        # Test 4: API endpoint with valid token (should succeed)
        print("\n" + "=" * 60)
        print("TEST 4: Valid Token")
        print("=" * 60)
        run_test(
            "Request with valid token should succeed",
            f"curl -s -w '\\nHTTP_CODE:%{{http_code}}' -H 'Authorization: Bearer {test_token}' http://localhost:8000/api/map-stats",
            expected_text="200"
        )

        # Test 5: Root endpoint (should work without token - exempt path)
        print("\n" + "=" * 60)
        print("TEST 5: Root Endpoint (Exempt Path)")
        print("=" * 60)
        run_test(
            "Root endpoint should work without token",
            "curl -s http://localhost:8000/",
            expected_text="CS2 Player Stats API"
        )

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.send_signal(signal.SIGTERM)
        server_process.wait(timeout=5)
        print("Server stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        sys.exit(1)
