"""
Test script to debug the confirmation loop issue during account creation
Run: python test_confirmation_flow.py
"""
import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/chat"

def send_message(message: str, session_id: str = None) -> Dict[str, Any]:
    """Send a message to the chatbot and return the response"""
    payload = {
        "message": message,
        "user_id": 1,
        "session_id": session_id
    }
    
    print(f"\n{'='*80}")
    print(f"[SEND] {message}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        print(f"[STATUS] {response.status_code if 'response' in locals() else 'N/A'}")
        return {}
    
    print(f"[RESPONSE] {data.get('response', 'N/A')}")
    print(f"[INTENT] {data.get('debug_state_intent', 'N/A')}")
    print(f"[STATUS] {data.get('status', 'N/A')}")
    
    return data

def test_confirmation_loop():
    """Test the account creation confirmation loop"""
    print("\n" + "="*80)
    print("TEST: Account Creation Confirmation Loop")
    print("="*80)
    
    session_id = None
    
    # Step 1: Start account creation
    print("\n[STEP 1] Starting account creation...")
    response = send_message("I want to create an account", session_id)
    session_id = response.get('session_id')
    
    # Step 2: Provide name
    print("\n[STEP 2] Providing name...")
    response = send_message("Ahmed Hassan", session_id)
    
    # Step 3: Provide phone
    print("\n[STEP 3] Providing phone number...")
    response = send_message("03001234567", session_id)
    
    # Step 4: Provide email
    print("\n[STEP 4] Providing email...")
    response = send_message("ahmed.test@example.com", session_id)
    time.sleep(2)  # Wait for OTP to be sent
    
    # Step 5: Provide OTP (mock OTP, should fail but that's okay for this test)
    print("\n[STEP 5] Providing OTP...")
    response = send_message("123456", session_id)
    
    # Step 6: Provide account type
    print("\n[STEP 6] Providing account type...")
    response = send_message("savings", session_id)
    
    # Step 7: First confirmation (say YES)
    print("\n[STEP 7] First confirmation (YES)...")
    response = send_message("yes", session_id)
    
    # Track the response to check for loop
    print(f"\n[AFTER YES]")
    print(f"   Response: {response.get('response', 'N/A')}")
    print(f"   State Intent: {response.get('debug_state_intent', 'N/A')}")
    
    # Step 8: Send another message (should NOT repeat confirmation)
    print("\n[STEP 8] Sending another message after confirmation...")
    response = send_message("hello", session_id)
    
    print(f"\n[AFTER HELLO]")
    print(f"   Response: {response.get('response', 'N/A')}")
    print(f"   State Intent: {response.get('debug_state_intent', 'N/A')}")
    
    # Check if we're stuck in confirmation loop
    if "Please confirm" in response.get('response', ''):
        print("\n[ERROR] Still in confirmation loop!")
        return False
    else:
        print("\n[SUCCESS] Confirmation loop handled correctly!")
        return True

if __name__ == "__main__":
    try:
        success = test_confirmation_loop()
        print("\n" + "="*80)
        if success:
            print("[PASS] TEST PASSED")
        else:
            print("[FAIL] TEST FAILED - Confirmation loop detected")
        print("="*80)
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
