"""
Focused test for the confirmation loop issue
This test will:
1. Start account creation
2. Provide all required info (name, phone, email)
3. Use a special marker to simulate successful OTP (we'll manually verify in logs)
4. Provide account type
5. Say YES to confirmation
6. Check if action executes
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/chat"

def send_message(message: str, session_id: str = None):
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
        print(f"[ERROR] Request failed: {e}")
        return {}

def test_with_real_otp():
    """Test with the real OTP that was sent"""
    session_id = None
    
    # Get a fresh email for testing
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"test.{randomsuffix}@example.com"
    
    print("="*80)
    print("TEST: Account Creation with Real OTP")
    print("="*80)
    
    # Step 1: Create account intent
    print("\n[STEP 1] Intent: create account")
    response = send_message("Create an account", session_id)
    session_id = response.get('session_id')
    print(f"Response: {response.get('response', 'N/A')}")
    
    # Step 2: Name
    print("\n[STEP 2] Provide name")
    response = send_message("Test User", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    
    # Step 3: Phone
    print("\n[STEP 3] Provide phone")
    response = send_message("03001234567", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    
    # Step 4: Email
    print("\n[STEP 4] Provide email")
    response = send_message("test.otp@example.com", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    print(f"[INFO] OTP should have been sent to test.otp@example.com")
    print(f"[ACTION] Manually check your email/SMS for the 6-digit OTP")
    
    # Wait for OTP
    otp_code = input("\n[INPUT] Enter the 6-digit OTP you received (or type 'skip' to exit): ").strip()
    if otp_code.lower() == 'skip':
        print("[SKIPPED] Test skipped")
        return
    
    if not otp_code.isdigit() or len(otp_code) != 6:
        print("[ERROR] Invalid OTP format")
        return
    
    # Step 5: OTP verification
    print(f"\n[STEP 5] Verify OTP: {otp_code}")
    response = send_message(otp_code, session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    
    if "✅" not in response.get('response', ''):
        print("[ERROR] OTP verification failed")
        return
    
    # Step 6: Account type
    print("\n[STEP 6] Provide account type")
    response = send_message("savings", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    
    # Check if confirmation is pending
    if "Please confirm" in response.get('response', ''):
        print("[INFO] Confirmation prompt detected - good!")
    else:
        print("[WARNING] No confirmation prompt")
    
    # Step 7: Confirm with YES
    print("\n[STEP 7] Send YES to confirm")
    response = send_message("yes", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    print(f"State Intent: {response.get('debug_state_intent', 'N/A')}")
    
    # Check for success or repeat
    resp_text = response.get('response', '').lower()
    if "✅" in response.get('response', '') or "successfully" in resp_text:
        print("[SUCCESS] Account created successfully!")
    elif "please confirm" in resp_text:
        print("[ERROR] Still showing confirmation - LOOP DETECTED!")
    else:
        print(f"[UNKNOWN] Unexpected response")
    
    # Step 8: Send another message
    print("\n[STEP 8] Send 'hello' to check if session is clean")
    response = send_message("hello", session_id)
    print(f"Response: {response.get('response', 'N/A')}")
    print(f"State Intent: {response.get('debug_state_intent', 'N/A')}")

if __name__ == "__main__":
    test_with_real_otp()
