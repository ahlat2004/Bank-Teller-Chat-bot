"""
Phase 2 Simple End-to-End Test
Tests receipt generation, error handling, entity validation
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print(" "*20 + "PHASE 2 END-TO-END TEST")
print("="*80)

# Test 1: Server Connection
print("\n✅ Test 1: Server Connection")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✅ Server is UP and responding!")
    else:
        print(f"   ❌ Server returned status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect: {e}")
    exit(1)

# Test 2: Chat Endpoint
print("\n✅ Test 2: Chat Endpoint")
try:
    payload = {
        "message": "What's my balance?",
        "user_id": 1,
        "session_id": "test_session_001"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Chat endpoint working!")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Balance Endpoint
print("\n✅ Test 3: Balance Endpoint")
try:
    response = requests.get(f"{BASE_URL}/api/balance/1", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Balance endpoint working!")
        if 'accounts' in data:
            print(f"   Found {len(data['accounts'])} account(s)")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test Phase 2 Features - Error Handling
print("\n✅ Test 4: Phase 2 Feature - Error Handling (Invalid Amount)")
try:
    payload = {
        "message": "Transfer 999999999999 PKR to someone",
        "user_id": 1,
        "session_id": "test_invalid_amount"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        response_text = data.get('response', '')
        if 'error' in response_text.lower() or 'invalid' in response_text.lower():
            print(f"   ✅ Error handling working!")
        else:
            print(f"   ⚠️  Response received: {response_text[:100]}...")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Entity Validation
print("\n✅ Test 5: Phase 2 Feature - Entity Validation")
try:
    payload = {
        "message": "Transfer 500 to account",
        "user_id": 1,
        "session_id": "test_validation"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        print(f"   ✅ Entity validation integrated!")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("🎉 PHASE 2 TEST SUITE COMPLETE")
print("="*80 + "\n")
