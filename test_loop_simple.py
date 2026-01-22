"""
Simple test for the confirmation loop issue - no Unicode/emoji
"""
import requests
import time
import json
import sys
from typing import Dict, Any

# Set UTF-8 encoding for terminal output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/chat"

def send_message(message: str, session_id: str = None) -> Dict[str, Any]:
    """Send a message and return response"""
    payload = {
        "message": message,
        "user_id": 1,
        "session_id": session_id
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        print(f"ERROR: {e}")
        return {}

def test():
    """Test account creation confirmation flow"""
    print("\n" + "="*80)
    print("TEST: Account Creation Confirmation Loop")
    print("="*80)
    
    session_id = None
    
    # Step 1: Start account creation
    print("\n[1] Create account intent...")
    resp = send_message("Create an account", session_id)
    session_id = resp.get('session_id')
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    
    # Step 2: Name
    print("\n[2] Provide name...")
    resp = send_message("Test User Flow", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    
    # Step 3: Phone
    print("\n[3] Provide phone...")
    resp = send_message("03001234567", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    
    # Step 4: Email - use the real test email
    print("\n[4] Provide email (apexwolf993@gmail.com)...")
    resp = send_message("apexwolf993@gmail.com", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    print("    [INFO] OTP has been sent to apexwolf993@gmail.com")
    print("    [INFO] Check your email for the 6-digit code")
    time.sleep(2)
    
    # Step 5: Get OTP from user
    print("\n[5] Enter the OTP from your email:")
    otp = input("    OTP (6 digits): ").strip()
    if not otp.isdigit() or len(otp) != 6:
        print("    [ERROR] Invalid OTP format")
        return False
    
    print(f"\n[5b] Verify OTP ({otp})...")
    resp = send_message(otp, session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:100]}")
    
    # Check if OTP was verified
    if "successfully" not in resp.get('response', '').lower() and "verified" not in resp.get('response', '').lower():
        print("    [ERROR] OTP verification failed")
        return False
    
    # Step 6: Account type
    print("\n[6] Provide account type (savings)...")
    resp = send_message("savings", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:100]}")
    
    # Check if confirmation is pending now
    conf_text = resp.get('response', '').lower()
    if "please confirm" in conf_text or "yes/no" in conf_text or "confirm:" in conf_text:
        print("    [GOOD] Confirmation prompt detected!")
    else:
        print(f"    [WARNING] No confirmation prompt - response was: {resp.get('response', '')[:100]}")
        return False
    
    # Step 7: Say YES
    print("\n[7] Send YES to confirmation...")
    resp = send_message("yes", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:150]}")
    print(f"    State intent after YES: {resp.get('debug_state_intent', 'N/A')}")
    
    # Check for loop
    resp_lower = resp.get('response', '').lower()
    if "please confirm" in resp_lower:
        print("\n[FAIL] Still showing confirmation - LOOP DETECTED!")
        return False
    elif "successfully" in resp_lower or "account created" in resp_lower or "account" in resp_lower and "created" in resp_lower:
        print("\n[PASS] Account created successfully!")
        return True
    else:
        print(f"\n[UNKNOWN] Unexpected response: {resp.get('response', '')[:100]}")
        return False

if __name__ == "__main__":
    success = test()
    print("\n" + "="*80)
    if success:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL or UNKNOWN")
    print("="*80)
