from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import jarvas

app = FastAPI(title="Jarvas AI")

# Monta a pasta frontend como estática
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Página principal
@app.get("/")
def home():
    return FileResponse("frontend/index.html")

# Manifest (OBRIGATÓRIO para PWA)
@app.get("/manifest.json")
def manifest():
    return FileResponse("frontend/manifest.json")

# Service Worker
@app.get("/sw.js")
def service_worker():
    return FileResponse("frontend/sw.js")

# Chat
@app.post("/chat")
def chat(pergunta: str):
    resposta = jarvas.responder(pergunta)
    return {"resposta": resposta}