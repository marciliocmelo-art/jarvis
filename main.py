from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# ======================
# BANCO DE DADOS
# ======================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jarvis.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ======================
# MODELO
# ======================

class User(BaseModel):
    email: str
    password: str

# ======================
# ROTAS
# ======================

@app.get("/")
def root():
    return {"status": "VERSAO ORIGINAL LIMPA"}

@app.post("/register")
def register(user: User):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (user.email, user.password)
        )

        conn.commit()
        conn.close()

        return {"message": "Usuário criado com sucesso"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário já existe")

@app.post("/login")
def login(user: User):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    if result[0] != user.password:
        raise HTTPException(status_code=400, detail="Senha incorreta")

    return {"message": "Login realizado com sucesso"}