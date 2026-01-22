#!/usr/bin/env python3
"""
Test account creation with real email
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/chat"
SESSION_ID = None

def send_msg(msg):
    global SESSION_ID
    payload = {
        "message": msg,
        "user_id": 1,
        "session_id": SESSION_ID if SESSION_ID else ""
    }
    r = requests.post(BASE_URL, json=payload, timeout=10)
    data = r.json()
    if 'session_id' in data:
        SESSION_ID = data['session_id']
    return data

# Start account creation
print('=== Starting Account Creation ===')
resp = send_msg('I want to open a new account')
print(f'Bot: {resp["response"][:100]}')
print(f'Session: {SESSION_ID}\n')

# Provide name
time.sleep(1)
resp = send_msg('My name is Ahmed Hassan')
print(f'Bot: {resp["response"][:100]}')
print(f'Intent: {resp["intent"]}\n')

# Provide phone
time.sleep(1)
resp = send_msg('My phone is 03001234567')
print(f'Bot: {resp["response"][:100]}')
print(f'Intent: {resp["intent"]}\n')

# Provide REAL email
time.sleep(1)
print('Sending email: apexwolf993@gmail.com')
resp = send_msg('My email is apexwolf993@gmail.com')
print(f'Bot: {resp["response"][:200]}')
print(f'Intent: {resp["intent"]}\n')
print('Check your email for OTP code!')
print(f'\nFull response: {resp["response"]}')
