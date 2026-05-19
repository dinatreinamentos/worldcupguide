import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads"


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def limpar(texto):
    return re.sub(r"\[.*?\]", "", texto).strip()


def extrair_squads():

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    dados = []

    selecao_atual = None
    posicao_atual = None

    # Wikipedia é estruturada em headings + listas
    for tag in soup.find_all(["h2", "h3", "li"]):

        texto = tag.get_text(" ", strip=True)

        if not texto:
            continue

        # detectar seleção
        if tag.name in ["h2", "h3"]:

            if "squad" in texto.lower() or "group" in texto.lower():
                continue

            if len(texto) < 60:
                selecao_atual = limpar(texto)
                posicao_atual = None
                continue

        # detectar posição (goleiro, defesa etc - padrão Wikipedia)
        if tag.name == "h3" and any(x in texto.lower() for x in ["goalkeeper", "defender", "midfielder", "forward"]):

            posicao_atual = texto
            continue

        # jogadores
        if tag.name == "li" and selecao_atual:

            jogador = limpar(texto)

            if len(jogador) < 2:
                continue

            dados.append({
                "selecao": selecao_atual,
                "jogador": jogador,
                "posicao": posicao_atual or "unknown"
            })

    return pd.DataFrame(dados).drop_duplicates()
