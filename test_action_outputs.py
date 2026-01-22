import requests
import json

BASE_URL = "http://localhost:8000/api/chat"

test_cases = [
    ("hello", "Greeting"),
    ("check my balance", "Check Balance"),
    ("yes", "Confirmation - Balance"),
    ("transfer 100 to john", "Transfer Money"),
    ("yes", "Confirmation - Transfer"),
    ("pay my electricity bill", "Bill Payment"),
    ("yes", "Confirmation - Bill"),
]

session_id = None

print("="*80)
print("COMPREHENSIVE ACTION OUTPUT TEST")
print("="*80)

for message, test_name in test_cases:
    print(f"\n[TEST] {test_name}: '{message}'")
    print("-" * 80)
    
    payload = {
        "message": message,
        "user_id": 1,
        "session_id": session_id if session_id else ""
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        data = response.json()
        
        # Store session ID for continuation
        if not session_id and 'session_id' in data:
            session_id = data['session_id']
        
        print(f"Status Code: {response.status_code}")
        print(f"Session ID: {data.get('session_id', 'N/A')}")
        print(f"Intent: {data.get('intent', 'N/A')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        print(f"\nResponse:")
        print(f"  {data.get('response', 'N/A')}")
        
        # Check for additional fields
        if 'action_output' in data:
            print(f"\nAction Output:")
            print(f"  {data['action_output']}")
        
        if 'receipt' in data:
            print(f"\nReceipt:")
            print(json.dumps(data['receipt'], indent=2))
            
        if 'balance' in data:
            print(f"\nBalance:")
            print(f"  {data['balance']}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        session_id = None  # Reset on error
    
    print("-" * 80)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
