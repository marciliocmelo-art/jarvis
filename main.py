import os
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI(title="Jarvis AI")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"status": "Jarvis AI online 🚀"}

@app.post("/chat")
def chat(pergunta: str):
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é Jarvis, assistente pessoal de Marcílio Melo."},
            {"role": "user", "content": pergunta}
        ]
    )

    return {"resposta": resposta.choices[0].message.content}