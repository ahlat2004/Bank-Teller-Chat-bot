import requests

tests = [
    ('check fees', ''),
    ('yes', ''),
    ('hi', ''),
    ('bye', ''),
]

sid = None
for msg, _ in tests:
    r = requests.post('http://localhost:8000/api/chat', json={'message': msg, 'user_id': 1, 'session_id': sid if sid else ''})
    resp = r.json()
    if not sid:
        sid = resp['session_id']
    resp_text = resp['response'][:60]
    print(f'{msg:20} -> {resp_text}...')
