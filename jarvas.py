# jarvas.py

import datetime

memoria = []

def responder(pergunta: str):

    global memoria

    pergunta_original = pergunta
    pergunta = pergunta.lower()

    memoria.append(pergunta_original)

    if "oi" in pergunta or "ola" in pergunta:
        return "Olá Marcílio. Estou ativo e aprendendo com você."

    if "dia" in pergunta or "data" in pergunta:
        hoje = datetime.datetime.now()
        return f"Hoje é {hoje.strftime('%d/%m/%Y')}"

    if "hora" in pergunta:
        agora = datetime.datetime.now()
        return f"Agora são {agora.strftime('%H:%M')}"

    if "o que eu falei antes" in pergunta or "o que eu disse antes" in pergunta:
        if len(memoria) <= 1:
            return "Você ainda não disse nada relevante."
        else:
            historico = memoria[:-1]
            return f"Você já disse: {historico}"

    return f"Marcílio, você disse: {pergunta_original}"