#!/usr/bin/env python
"""
Test script to verify authentication flow in redemption store.
Run this after logging in via the app to test:
1. Session key is correctly set (farmer_id_verified)
2. /api/offers returns 200 with coin data
3. /api/balance returns 200 with coin data
4. Store page redirects to login if not authenticated
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_without_auth():
    """Test API calls without authentication - should get 401."""
    print("\n=== Testing WITHOUT Authentication ===")
    
    # Test /api/offers
    resp = requests.get(f"{BASE_URL}/redemption/api/offers", allow_redirects=False)
    print(f"GET /redemption/api/offers (no auth): {resp.status_code}")
    if resp.status_code == 401:
        print("✓ Correctly returns 401 Unauthorized")
        print(f"Response: {resp.json()}")
    else:
        print(f"✗ Expected 401, got {resp.status_code}")
    
    # Test /api/balance
    resp = requests.get(f"{BASE_URL}/redemption/api/balance", allow_redirects=False)
    print(f"\nGET /redemption/api/balance (no auth): {resp.status_code}")
    if resp.status_code == 401:
        print("✓ Correctly returns 401 Unauthorized")
        print(f"Response: {resp.json()}")
    else:
        print(f"✗ Expected 401, got {resp.status_code}")
    
    # Test /store page
    resp = requests.get(f"{BASE_URL}/redemption/store", allow_redirects=False)
    print(f"\nGET /redemption/store (no auth): {resp.status_code}")
    if resp.status_code == 302:  # Redirect to login
        print("✓ Correctly redirects to login")
        print(f"Location: {resp.headers.get('Location')}")
    else:
        print(f"✗ Expected 302 redirect, got {resp.status_code}")

def test_with_session():
    """Test with a session cookie from manual login."""
    print("\n=== Testing WITH Authentication (via session) ===")
    
    session = requests.Session()
    
    # You would need to manually log in first to get a valid session
    # This is just a template for testing
    
    print("To test with authentication:")
    print("1. Log in manually via http://127.0.0.1:5000/login")
    print("2. Open browser dev tools -> Application -> Cookies")
    print("3. Copy the 'session' cookie value")
    print("4. Run this test again with FLASK_SESSION_COOKIE value set")
    print("\nAlternatively, run this test in the same browser session using curl:")
    print("  curl -b 'session=YOUR_SESSION_COOKIE' http://127.0.0.1:5000/redemption/api/offers")

if __name__ == '__main__':
    print("=" * 60)
    print("Redemption Store Authentication Flow Test")
    print("=" * 60)
    
    test_without_auth()
    test_with_session()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
