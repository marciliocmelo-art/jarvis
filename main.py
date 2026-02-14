from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import sqlite3
import os

# ==========================
# CONFIG
# ==========================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY não definida")

client = OpenAI(api_key=api_key.strip())

# 🔥 USANDO bcrypt_sha256 (resolve limite 72 bytes)
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

# ==========================
# FASTAPI
# ==========================

app = FastAPI(title="Jarvis SaaS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================
# BANCO
# ==========================

DB_PATH = "jarvis.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ==========================
# MODELOS
# ==========================

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str

# ==========================
# JWT
# ==========================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token ausente")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    return user_id

# ==========================
# ROTAS
# ==========================

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/register")
def register(data: RegisterRequest):
    try:
        hashed_password = pwd_context.hash(data.password)

        cursor.execute("""
            INSERT INTO users (email, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (data.email, hashed_password, datetime.utcnow().isoformat()))
        conn.commit()

        return {"message": "Usuário criado com sucesso"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

@app.post("/login")
def login(data: LoginRequest):
    cursor.execute("""
        SELECT id, password_hash FROM users WHERE email = ?
    """, (data.email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    user_id, password_hash = user

    if not pwd_context.verify(data.password, password_hash):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    token = create_access_token({"user_id": user_id})
    return {"access_token": token}

@app.post("/chat")
def chat(data: ChatRequest, user_id: int = Depends(get_current_user)):

    cursor.execute("""
        SELECT role, content FROM conversations
        WHERE user_id = ?
        ORDER BY id ASC
    """, (user_id,))
        
    history = cursor.fetchall()

    conversation = [
        {"role": "system", "content": "Você é Jarvis, assistente estratégico."}
    ]

    for role, content in history:
        conversation.append({"role": role, "content": content})

    conversation.append({"role": "user", "content": data.message})

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=conversation
    )

    assistant_message = response.output_text
    now = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO conversations (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, "user", data.message, now))

    cursor.execute("""
        INSERT INTO conversations (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, "assistant", assistant_message, now))

    conn.commit()

    return {"response": assistant_message}