import requests
import json

print("=" * 80)
print("Testing Create Account Feature")
print("=" * 80)

# Test 1: Create account request
print("\n✅ Test 1: Create Savings Account")
print("-" * 80)

response = requests.post('http://localhost:8000/api/chat', 
    json={'message': 'I want to create a savings account', 'user_id': 1})

data = response.json()
print(f"User: I want to create a savings account")
print(f"Bot: {data['response']}")
print(f"Intent: {data['intent']}")
print(f"Requires Input: {data['requires_input']}")

# Test 2: Create current account
print("\n✅ Test 2: Create Current Account")
print("-" * 80)

response = requests.post('http://localhost:8000/api/chat', 
    json={'message': 'Create a current account for me', 'user_id': 2})

data = response.json()
print(f"User: Create a current account for me")
print(f"Bot: {data['response']}")
print(f"Intent: {data['intent']}")

# Test 3: Invalid account type
print("\n✅ Test 3: Invalid Account Type")
print("-" * 80)

response = requests.post('http://localhost:8000/api/chat', 
    json={'message': 'Create a crypto account', 'user_id': 1})

data = response.json()
print(f"User: Create a crypto account")
print(f"Bot: {data['response']}")

print("\n" + "=" * 80)
print("Testing Complete!")
print("=" * 80)
