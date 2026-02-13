from fastapi import FastAPI
from fastapi.responses import FileResponse
import jarvas

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Jarvis online 🚀"}

@app.get("/manifest.json")
def manifest():
    return FileResponse("frontend/manifest.json")

@app.get("/sw.js")
def service_worker():
    return FileResponse("frontend/sw.js")

@app.post("/chat")
def chat(pergunta: str):
    resposta = jarvas.responder(pergunta)
    return {"resposta": resposta}