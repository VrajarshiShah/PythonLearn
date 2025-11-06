import requests
import json

# Simple version - just show the raw response
url = "https://api.sikkasoft.com/v4/practice_query"
headers = {
    "Request-Key": "fd34a6e6b28b2a272eef19682e6c428d",
    "Content-Type": "application/json"
}

data = {
    "pql": "SELECT [patients.patient_id] FROM [patients]",
    "limit": "50",
    "offset": "0"
}

response = requests.post(url, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))