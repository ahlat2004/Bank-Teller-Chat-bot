"""
WP7 FastAPI Backend Test Suite
Tests all API endpoints and integration
"""

import requests
import json
import sys

base_url = "http://localhost:8000"

print("=" * 80)
print(" " * 20 + "FASTAPI BACKEND TEST SUITE - WP7")
print("=" * 80)

tests_passed = 0
tests_failed = 0

# Test 1: Health Check
print("\n✅ Test 1: Health Check")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Database: {'✅' if data.get('database') else '❌'}")
        print(f"Intent Classifier: {'✅' if data.get('intent_classifier') else '❌'}")
        print(f"Entity Extractor: {'✅' if data.get('entity_extractor') else '❌'}")
        print(f"Dialogue Manager: {'✅' if data.get('dialogue_manager') else '❌'}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ Error: {e}")
    tests_failed += 1

# Test 2: Get Balance
print("\n✅ Test 2: Get Balance")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/api/balance/1")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved balance for user 1")
        if 'accounts' in data:
            for acc in data['accounts']:
                print(f"  {acc['account_type']:10s}: PKR {acc['balance']:>12,.2f}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ Error: {e}")
    tests_failed += 1

# Test 3: Chat Endpoint
print("\n✅ Test 3: Chat Endpoint")
print("-" * 80)
try:
    response = requests.post(
        f"{base_url}/api/chat",
        json={"message": "What's my balance?", "user_id": 1}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"User: What's my balance?")
        print(f"Bot: {data['response']}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ Error: {e}")
    tests_failed += 1

# Test 4: Transaction History
print("\n✅ Test 4: Transaction History")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/api/history/1?limit=3")
    if response.status_code == 200:
        data = response.json()
        transactions = data.get('transactions', [])
        print(f"✅ Retrieved {len(transactions)} transactions")
        for i, txn in enumerate(transactions[:3], 1):
            print(f"  {i}. {txn['type']:15s} PKR {txn['amount']:>10,.2f}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ Error: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 80)
print(" " * 25 + "TEST SUMMARY")
print("=" * 80)
print(f"\nTests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests: {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! ✅")
    print("\n   WP7 FastAPI Backend is working successfully!")
    print("   Server: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    sys.exit(0)
else:
    print(f"\n❌ {tests_failed} test(s) failed")
    sys.exit(1)
