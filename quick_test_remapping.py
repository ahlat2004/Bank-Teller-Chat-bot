import requests
import time

# Wait for server
time.sleep(3)

BASE_URL = "http://localhost:8000/api/chat"

print("Testing with remapping...")
print("="*80)

# Test 1: Check balance
print("\n[1] Testing: 'check my balance'")
r1 = requests.post(BASE_URL, json={"message": "check my balance", "user_id": 1, "session_id": ""})
resp1 = r1.json()
print(f"    Intent (remapped): {resp1.get('intent')}")
print(f"    Response: {resp1.get('response')[:60]}...")

# Test 2: Confirm
sid = resp1.get('session_id')
print(f"\n[2] Testing confirmation: 'yes' with session {sid}")
r2 = requests.post(BASE_URL, json={"message": "yes", "user_id": 1, "session_id": sid})
resp2 = r2.json()
print(f"    Intent: {resp2.get('intent')}")
print(f"    Response: {resp2.get('response')[:80]}...")

print("\n" + "="*80)
print("Test complete!")
