"""
Minimal Diagnostic Test
Tests individual endpoints one at a time to identify which one causes the shutdown
"""

import requests
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("MINIMAL DIAGNOSTIC TEST")
print("="*80)

# Test 1: Check server is alive
print("\n[TEST 1] Server Health (/docs)")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    print(f"✅ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

time.sleep(1)

# Test 2: Check chat endpoint with simple input
print("\n[TEST 2] Chat Endpoint (/api/chat) - Simple Message")
try:
    payload = {
        "message": "Hello",
        "user_id": 1,
        "session_id": "test_001"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=10)
    print(f"✅ Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Response: {response.json().get('response', '')[:100]}")
except Exception as e:
    print(f"❌ Error: {e}")

time.sleep(1)

# Test 3: Check balance endpoint
print("\n[TEST 3] Balance Endpoint (/api/balance/1)")
try:
    response = requests.get(f"{BASE_URL}/api/balance/1", timeout=5)
    print(f"✅ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
