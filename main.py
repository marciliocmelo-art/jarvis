from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from openai import OpenAI
import sqlite3
import os

# ==========================
# CONFIG
# ==========================

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 🔥 SEM BCRYPT (SEM LIMITE 72 BYTES)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# DATABASE
# ==========================

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

# ==========================
# MODELS
# ==========================

class User(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    message: str

# ==========================
# AUTH FUNCTIONS
# ==========================

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ==========================
# ROUTES
# ==========================

@app.get("/")
def root():
    return {"status": "JARVIS AI ONLINE"}

@app.post("/register")
def register(user: User):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        hashed_password = hash_password(user.password)

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (user.email, hashed_password)
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

    stored_password = result[0]

    if not verify_password(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    token = create_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/chat")
def chat(data: ChatMessage, current_user: str = Depends(get_current_user)):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é Jarvis, um assistente inteligente e profissional."},
            {"role": "user", "content": data.message}
        ]
    )

    return {
        "user": current_user,
        "reply": response.choices[0].message.content
    }