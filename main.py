from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import sqlite3
import os

# ==========================
# CONFIG
# ==========================

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

# ==========================
# DATABASE (Render safe)
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

# ==========================
# UTILS
# ==========================

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# ROUTES
# ==========================

@app.get("/")
def root():
    return {"status": "Jarvis SaaS online"}

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

    except Exception as e:
        print("ERRO REAL:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(user: User):
    try:
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

        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        print("ERRO REAL LOGIN:", str(e))
        raise HTTPException(status_code=500, detail=str(e))