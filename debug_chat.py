import requests
import json

# Test the chat endpoint
response = requests.post(
    'http://localhost:8000/api/chat',
    json={'message': "What's my balance?", 'user_id': 1}
)

print('Status Code:', response.status_code)
print('\nFull Response:')
data = response.json()
print(json.dumps(data, indent=2))

print('\n\nDetailed Analysis:')
print(f"Response Text: {data.get('response')}")
print(f"Intent Detected: {data.get('intent')}")
print(f"Requires Input: {data.get('requires_input')}")
print(f"Session ID: {data.get('session_id')}")
