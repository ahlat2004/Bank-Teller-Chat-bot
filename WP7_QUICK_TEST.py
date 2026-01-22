#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WP7 QUICK TEST - Validates core functionality
"""

import requests
import sys

base_url = "http://localhost:8000"

print("=" * 80)
print("WP7 QUICK TEST - Core Features Validation")
print("=" * 80)

tests = {
    "Health Check": lambda: requests.get(f"{base_url}/health", timeout=2).status_code == 200,
    "Get Balance": lambda: requests.get(f"{base_url}/api/balance/1", timeout=2).status_code == 200,
    "Chat - Check Balance": lambda: requests.post(f"{base_url}/api/chat", json={"message": "What's my balance?", "user_id": 1}, timeout=2).status_code == 200,
    "Transaction History": lambda: requests.get(f"{base_url}/api/history/1?limit=3", timeout=2).status_code == 200,
    "Create Account Intent": lambda: requests.post(f"{base_url}/api/chat", json={"message": "I want to create a savings account", "user_id": 1}, timeout=2).status_code == 200,
}

passed = 0
failed = 0

for test_name, test_func in tests.items():
    try:
        if test_func():
            print(f"[PASS] {test_name}")
            passed += 1
        else:
            print(f"[FAIL] {test_name}")
            failed += 1
    except Exception as e:
        print(f"[ERROR] {test_name}: {str(e)[:50]}")
        failed += 1

print("\n" + "=" * 80)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 80)

if failed == 0:
    print("\n[SUCCESS] All core features working!")
    print("WP7 Backend Implementation: COMPLETE")
    print("\nNext Step: WP8 - Frontend Development")
    sys.exit(0)
else:
    print(f"\n[WARNING] {failed} test(s) failed")
    sys.exit(1)
