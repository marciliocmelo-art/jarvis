import requests
from datetime import datetime

URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-3-4b"

def perguntar(pergunta):

    hoje = datetime.now().strftime("%d/%m/%Y")

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": f"Hoje é {hoje}. Sempre use essa data como referência atual."
            },
            {
                "role": "user",
                "content": pergunta
            }
        ],
        "temperature": 0.7
    }

    response = requests.post(URL, json=data)
    resposta = response.json()
    return resposta["choices"][0]["message"]["content"]

print("🤖 Chatbot iniciado. Digite 'sair' para encerrar.\n")

while True:
    pergunta = input("Você: ")

    if pergunta.lower() == "sair":
        break

    resposta = perguntar(pergunta)
    print("\nIA:", resposta, "\n")