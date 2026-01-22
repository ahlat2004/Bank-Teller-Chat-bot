#!/usr/bin/env python3
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
    r = requests.post(BASE_URL, json=payload, timeout=10)
    data = r.json()
    if "session_id" in data:
        SESSION_ID = data["session_id"]
    return data

resp1 = send_msg("I want to open a new account")
print(f"MSG1 - Intent: {resp1['intent']}, State Intent: {resp1.get('debug_state_intent')}, Session Found: {resp1.get('debug_session_found')}")

resp2 = send_msg("My name is Ahmed")  
print(f"MSG2 - Intent: {resp2['intent']}, State Intent: {resp2.get('debug_state_intent')}, Session Found: {resp2.get('debug_session_found')}")

