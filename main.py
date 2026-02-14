from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3
import os

# =============================
# CONFIGURAÇÕES
# =============================

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# BANCO DE DADOS
# =============================

DB_NAME = "jarvis.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =============================
# MODELS
# =============================

class User(BaseModel):
    email: str
    password: str

# =============================
# FUNÇÕES
# =============================

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =============================
# ROTAS
# =============================

@app.post("/register")
def register(user: User):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    hashed_password = hash_password(user.password)

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (user.email, hashed_password)
        )
        conn.commit()
    except:
        conn.close()
        raise HTTPException(status_code=400, detail="Usuário já existe")

    conn.close()
    return {"message": "Usuário criado com sucesso"}

@app.post("/login")
def login(user: User):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    stored_password = result[0]

    if not verify_password(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    token = create_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"status": "Jarvis SaaS online"}