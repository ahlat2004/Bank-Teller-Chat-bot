import requests
import json

response = requests.post('http://localhost:8000/api/chat', 
    json={'message': "What's my balance?", 'user_id': 1})

print(f'Status Code: {response.status_code}')
print(f'Response:')
print(json.dumps(response.json(), indent=2))
