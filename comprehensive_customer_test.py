#!/usr/bin/env python3
"""
Bank Teller Chatbot - Comprehensive Customer Test
Acts as a real bank customer testing all major functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/chat"
SESSION_ID = None

def send_message(msg):
    """Send a message and return response"""
    global SESSION_ID
    payload = {
        "message": msg,
        "user_id": 1,
        "session_id": SESSION_ID if SESSION_ID else ""
    }
    
    try:
        r = requests.post(BASE_URL, json=payload, timeout=5)
        data = r.json()
        
        # Store session ID
        if 'session_id' in data:
            SESSION_ID = data['session_id']
        
        return data
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_case(name, message, expected_keywords=None):
    """Test a single case"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"USER: {message}")
    print(f"{'-'*80}")
    
    response = send_message(message)
    if not response:
        print("❌ No response received!")
        return False
    
    bot_response = response.get('response', '')
    intent = response.get('intent', 'N/A')
    confidence = response.get('confidence', 0)
    
    print(f"BOT: {bot_response[:100]}{'...' if len(bot_response) > 100 else ''}")
    print(f"INTENT: {intent} ({confidence:.1%})")
    
    if expected_keywords:
        found = all(kw.lower() in bot_response.lower() for kw in expected_keywords)
        if found:
            print("✅ PASS - Response contains expected keywords")
            return True
        else:
            print(f"❌ FAIL - Expected keywords not found: {expected_keywords}")
            return False
    
    return True

# ==================== TEST SUITE ====================
print("\n" + "="*80)
print("BANK TELLER CHATBOT - COMPREHENSIVE CUSTOMER TEST")
print("="*80)

results = []

# Test 1: Greeting
print("\n[PHASE 1] GREETING & SETUP")
results.append(("Greeting", test_case("Greeting", "Hi there", ["help"])))

# Test 2: Check Balance (no confirmation needed) - Fresh session
print("\n[PHASE 2] BALANCE INQUIRY")
SESSION_ID = None  # Reset for new phase
results.append(("Check Balance", test_case("Check Balance", "What's my account balance?", ["balance", "PKR"])))

# Test 3: Recent Transactions - Fresh session
print("\n[PHASE 3] TRANSACTION HISTORY")
SESSION_ID = None  # Reset for new phase
results.append(("Check Transactions", test_case("Recent Transactions", "Show me my recent transactions", ["transaction"])))

# Test 4: Transfer Money (with confirmation) - Fresh session
print("\n[PHASE 4] MONEY TRANSFER")
SESSION_ID = None  # Reset for new phase
results.append(("Transfer Request", test_case("Transfer Request", "I want to transfer 5000 to Ali", ["account"])))
time.sleep(1)
results.append(("Transfer Confirm", test_case("Transfer Confirmation", "Yes, confirm that", [])))

# Test 5: Pay a Bill (with confirmation) - Fresh session
print("\n[PHASE 5] BILL PAYMENT")
SESSION_ID = None  # Reset for new phase
results.append(("Bill Payment Request", test_case("Bill Payment", "Pay my electricity bill for 3000", ["confirm", "bill"])))
time.sleep(1)
results.append(("Bill Payment Confirm", test_case("Bill Confirmation", "Yes do it", [])))

# Test 6: Create Account (email verification flow) - Fresh session
print("\n[PHASE 6] ACCOUNT CREATION")
SESSION_ID = None  # Reset for new phase
results.append(("Create Account", test_case("New Account", "I want to open a new account", ["name"])))
time.sleep(1)
results.append(("Provide Name", test_case("Name Input", "My name is Ahmed Hassan", [])))
time.sleep(1)
results.append(("Provide Phone", test_case("Phone Input", "My phone is 03001234567", [])))
time.sleep(1)
results.append(("Provide Email", test_case("Email Input", "My email is ahmed@example.com", ["verification", "OTP", "email"])))

# Test 7: General Help - Fresh session
print("\n[PHASE 7] CUSTOMER SERVICE")
SESSION_ID = None  # Reset for new phase
results.append(("Help Query", test_case("Help Request", "Where can I find the nearest ATM?", ["ATM", "branch"])))

# ==================== SUMMARY ====================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

passed = sum(1 for _, result in results if result)
total = len(results)

for test_name, result in results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

print(f"\n{passed}/{total} tests passed ({100*passed/total:.0f}%)")

if passed == total:
    print("\n🎉 ALL TESTS PASSED! System is working correctly.")
else:
    print(f"\n⚠️  {total - passed} tests failed. Review logs above.")

print("="*80)
