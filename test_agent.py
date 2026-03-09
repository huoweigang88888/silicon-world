import urllib.request
import json

url = "http://localhost:8000/api/v1/agents"
data = {
    "name": "三一",
    "controller": "0x1234567890abcdef",
    "personality": {"trait": "friendly", "voice": "warm"}
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        print("Status: 200")
        print(result)
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(e.read().decode('utf-8'))
