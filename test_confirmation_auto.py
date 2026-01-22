"""
Test account creation confirmation with auto OTP entry
Waits a few seconds to allow user to check email and get the OTP
"""
import requests
import time
import sys
from typing import Dict, Any

# Set UTF-8 encoding
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
    print("TEST: Account Creation Confirmation (AUTO OTP)")
    print("="*80)
    
    session_id = None
    
    # Step 1: Start account creation
    print("\n[1] Create account intent...")
    resp = send_message("Create an account", session_id)
    session_id = resp.get('session_id')
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    time.sleep(0.5)
    
    # Step 2: Name
    print("\n[2] Provide name...")
    resp = send_message("Test User Flow", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    time.sleep(0.5)
    
    # Step 3: Phone
    print("\n[3] Provide phone...")
    resp = send_message("03001234567", session_id)
    print(f"    Response: {resp.get('response', 'N/A')[:80]}")
    time.sleep(0.5)
    
    # Step 4: Email - use the real test email
    print("\n[4] Provide email (apexwolf993@gmail.com)...")
    resp = send_message("apexwolf993@gmail.com", session_id)
    resp_text = resp.get('response', '')
    print(f"    Response: {resp_text[:80]}")
    print("    [INFO] Waiting 10 seconds for OTP email...")
    
    # Wait for OTP to be sent and user to check email
    for i in range(10, 0, -1):
        print(f"    [{i}] Checking email...", end='\r')
        time.sleep(1)
    print("\n    [INFO] Please manually check your email and enter OTP below")
    print("    [INFO] If no OTP received, check spam folder or use 'resend'")
    time.sleep(1)
    
    # Step 5: Get OTP from user
    print("\n[5] Enter the OTP from your email:")
    otp = input("    OTP (6 digits): ").strip()
    if not otp.isdigit() or len(otp) != 6:
        print("    [ERROR] Invalid OTP format")
        return False
    
    print(f"\n[5b] Verify OTP ({otp})...")
    resp = send_message(otp, session_id)
    resp_text = resp.get('response', '')
    print(f"    Response: {resp_text[:100]}")
    
    # Check if OTP was verified
    if "successfully" not in resp_text.lower() and "verified" not in resp_text.lower():
        if "invalid" in resp_text.lower():
            print("    [ERROR] OTP verification failed - invalid code")
            return False
        else:
            print(f"    [WARNING] Unexpected response: {resp_text[:80]}")
    else:
        print("    [GOOD] OTP verified!")
    
    time.sleep(0.5)
    
    # Step 6: Account type
    print("\n[6] Provide account type (savings)...")
    resp = send_message("savings", session_id)
    resp_text = resp.get('response', '')
    print(f"    Response: {resp_text[:100]}")
    
    # Check if confirmation is pending now
    conf_text = resp_text.lower()
    if "please confirm" in conf_text or "yes/no" in conf_text or "confirm:" in conf_text:
        print("    [GOOD] Confirmation prompt detected!")
    else:
        print(f"    [WARNING] No confirmation prompt - response was: {resp_text[:100]}")
        return False
    
    time.sleep(0.5)
    
    # Step 7: Say YES
    print("\n[7] Send YES to confirmation...")
    resp = send_message("yes", session_id)
    resp_text = resp.get('response', '')
    state_intent = resp.get('debug_state_intent', 'N/A')
    print(f"    Response: {resp_text[:150]}")
    print(f"    State intent after YES: {state_intent}")
    
    # Check for loop or success
    resp_lower = resp_text.lower()
    if "please confirm" in resp_lower:
        print("\n[FAIL] Still showing confirmation - LOOP DETECTED!")
        print(f"    Full response: {resp_text}")
        return False
    elif "successfully" in resp_lower or ("account" in resp_lower and "created" in resp_lower) or "receipt" in resp_lower:
        print("\n[SUCCESS] Account created successfully!")
        print(f"    Full response:\n{resp_text}")
        return True
    else:
        print(f"\n[UNKNOWN] Unexpected response: {resp_text}")
        return False

if __name__ == "__main__":
    try:
        success = test()
        print("\n" + "="*80)
        if success:
            print("RESULT: PASS ✓")
        else:
            print("RESULT: FAIL ✗")
        print("="*80)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\nTest error: {e}")
        import traceback
        traceback.print_exc()
