"""Quick test of the account creation flow"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_chat(message, session_id=None):
    """Send a chat message and return response"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "user_id": 1, "session_id": session_id},
            timeout=10
        )
        data = resp.json()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Testing Account Creation Flow...")
print("=" * 60)

# Step 1: Start conversation
print("\n1. Starting account creation...")
r1 = test_chat("I want to create a new account")
if r1:
    session_id = r1.get('session_id')
    print(f"   Session: {session_id}")
    print(f"   Bot: {r1.get('response')}")
    print(f"   Intent: {r1.get('intent')}")

# Step 2: Provide name
print("\n2. Providing name...")
r2 = test_chat("Test User", session_id)
if r2:
    print(f"   Bot: {r2.get('response')}")
    print(f"   Intent: {r2.get('intent')}")

# Step 3: Provide phone
print("\n3. Providing phone...")
r3 = test_chat("03001234567", session_id)
if r3:
    print(f"   Bot: {r3.get('response')}")
    print(f"   Intent: {r3.get('intent')}")

# Step 4: Provide email
print("\n4. Providing email (OTP will be sent)...")
r4 = test_chat("apexwolf993@gmail.com", session_id)
if r4:
    print(f"   Bot: {r4.get('response')}")
    print(f"   Intent: {r4.get('intent')}")

# Step 5: Get OTP from user
print("\n5. Waiting for OTP...")
otp = input("   Enter OTP from email: ").strip()

print(f"\n6. Verifying OTP...")
r5 = test_chat(otp, session_id)
if r5:
    print(f"   Bot: {r5.get('response')}")
    print(f"   Intent: {r5.get('intent')}")

print("\nTest complete!")
