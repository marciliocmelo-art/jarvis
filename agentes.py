import requests

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-3-4b"

def agente_local(pergunta):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.7
    }

    response = requests.post(LM_URL, json=data)
    return response.json()["choices"][0]["message"]["content"]