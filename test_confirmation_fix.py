#!/usr/bin/env python3
"""
Test to verify the confirmation handling fix.
This test verifies that when a user is in confirmation mode,
the system does NOT remap intent but instead processes yes/no patterns.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_confirmation_flow():
    """Test that confirmation flow works without intent remapping."""
    print("=" * 60)
    print("TESTING CONFIRMATION FIX")
    print("=" * 60)
    
    session_id = "test_confirmation_" + str(int(time.time()))
    user_id = 1
    
    print(f"\nSession ID: {session_id}")
    print(f"User ID: {user_id}\n")
    
    # Step 1: Ask to pay a bill for gas
    print("Step 1: User says 'pay a bill for gas'")
    r1 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "pay a bill for gas", "user_id": user_id, "session_id": session_id},
        timeout=10
    )
    resp1 = r1.json()
    print(f"  Intent: {resp1.get('intent')}")
    print(f"  Response: {resp1.get('response')}")
    print(f"  Confirmation pending: {resp1.get('state_intent') is not None}")
    
    sleep(1)
    
    # Step 2: User says "no" to cancel
    print("\nStep 2: User says 'no'")
    r2 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "no", "user_id": user_id, "session_id": session_id},
        timeout=10
    )
    resp2 = r2.json()
    print(f"  Intent: {resp2.get('intent')}")
    print(f"  Response: {resp2.get('response')}")
    print(f"  ✓ Action cancelled" if "cancelled" in resp2.get('response', '').lower() else "  ✗ Did not cancel")
    
    sleep(1)
    
    # Step 3: Ask to pay a bill again
    print("\nStep 3: User says 'pay a bill'")
    r3 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "pay a bill", "user_id": user_id, "session_id": session_id},
        timeout=10
    )
    resp3 = r3.json()
    print(f"  Intent: {resp3.get('intent')}")
    print(f"  Response: {resp3.get('response')}")
    
    sleep(1)
    
    # Step 4: User says "gas" again (THIS IS THE KEY TEST)
    # With the fix, this should NOT be remapped to cancel_card
    # Instead, it should ask to confirm the previous bill_payment intent
    print("\nStep 4: User says 'gas' again (CRITICAL TEST)")
    r4 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "gas", "user_id": user_id, "session_id": session_id},
        timeout=10
    )
    resp4 = r4.json()
    print(f"  Intent: {resp4.get('intent')}")
    print(f"  Response: {resp4.get('response')}")
    
    # VERIFY: The intent should be bill_payment, NOT cancel_card
    if resp4.get('state_intent') == 'bill_payment' or 'gas' in resp4.get('response', '').lower():
        print(f"  ✓ PASS: System correctly recognized gas bill payment (not remapped to cancel_card)")
    else:
        print(f"  ✗ FAIL: System remapped to {resp4.get('intent')} instead of keeping bill_payment")
    
    sleep(1)
    
    # Step 5: User confirms with "yes"
    print("\nStep 5: User says 'yes' to confirm")
    r5 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "yes", "user_id": user_id, "session_id": session_id},
        timeout=10
    )
    resp5 = r5.json()
    print(f"  Intent: {resp5.get('intent')}")
    print(f"  Response: {resp5.get('response')}")
    print(f"  ✓ Action confirmed and executed" if "transferred" in resp5.get('response', '').lower() or "completed" in resp5.get('response', '').lower() else "  (Action processing)")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    import time
    try:
        test_confirmation_flow()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend is running: python backend/app/main.py")
