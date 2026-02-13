import sqlite3

def criar_banco():
    conn = sqlite3.connect("jarvas.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave TEXT,
        valor TEXT
    )
    """)

    conn.commit()
    conn.close()

def salvar_memoria(chave, valor):
    conn = sqlite3.connect("jarvas.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO memoria (chave, valor) VALUES (?, ?)", (chave, valor))

    conn.commit()
    conn.close()

def buscar_memorias():
    conn = sqlite3.connect("jarvas.db")
    cursor = conn.cursor()

    cursor.execute("SELECT chave, valor FROM memoria")
    dados = cursor.fetchall()

    conn.close()
    return dados