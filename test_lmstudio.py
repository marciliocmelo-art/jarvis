import requests

url = "http://127.0.0.1:1234/v1/chat/completions"

data = {
    "model": "google/gemma-3-4b",
    "messages": [
        {
            "role": "user",
            "content": "Explique o que é FastAPI em 3 linhas"
        }
    ],
    "temperature": 0.7
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Resposta:", response.json())