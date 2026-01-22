#!/usr/bin/env python3
"""
Debug: Check if session state is persisting
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/chat"
SESSION_ID = None

def send_msg(msg):
    global SESSION_ID
    payload = {
        "message": msg,
        "user_id": 1,
        "session_id": SESSION_ID if SESSION_ID else ""
    }
    print(f"\n>>> Sending with session_id: '{SESSION_ID if SESSION_ID else 'EMPTY'}'")
    r = requests.post(BASE_URL, json=payload, timeout=10)
    data = r.json()
    print(f"<<< Received with session_id: '{data.get('session_id')}'")
    if 'session_id' in data:
        SESSION_ID = data['session_id']
    return data

# Message 1: Create account
print('MESSAGE 1: Create Account')
resp = send_msg('I want to open a new account')
print(f"Intent: {resp['intent']}")

# Message 2: Provide name
print('\nMESSAGE 2: Provide Name')
resp = send_msg('My name is Ahmed')
print(f"Intent: {resp['intent']}")
print(f"Expected: create_account, Got: {resp['intent']}")
