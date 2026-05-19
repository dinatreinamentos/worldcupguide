import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


URL = "https://www.cnnbrasil.com.br/esportes/futebol/copa-do-mundo/listas-convocados-todas-48-selecoes-copa-do-mundo-2026/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


CATEGORIAS = {
    "Goleiros": "goleiro",
    "Defensores": "defesa",
    "Meio-campistas": "meio-campo",
    "Atacantes": "ataque"
}


def limpar(texto):
    texto = re.sub(r"\(.*?\)", "", texto)
    return texto.replace(".", "").replace(";", "").strip()


def eh_pre_lista(texto):
    return "(pré-lista)" in texto.lower()


def extrair_jogadores():

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    dados = []

    selecao_atual = None
    categoria_atual = None
    ignorar = False

    # Trabalhar por blocos reais (parágrafos + headings)
    elementos = soup.find_all(["h2", "h3", "p"])

    for el in elementos:

        texto = el.get_text(" ", strip=True)

        if not texto:
            continue

        # Detecta seleção (ex: "Coreia do Sul")
        if el.name in ["h2", "h3"]:

            if "(" in texto and "pré-lista" in texto.lower():
                ignorar = True
                selecao_atual = None
                categoria_atual = None
                continue

            if len(texto) < 50 and "grupo" not in texto.lower():
                selecao_atual = texto
                ignorar = False

            continue

        if ignorar or not selecao_atual:
            continue

        # Detecta categoria
        for cat in CATEGORIAS.keys():

            if texto.startswith(cat + ":"):

                categoria_atual = cat

                jogadores_texto = texto.replace(cat + ":", "").strip()

                jogadores_texto = jogadores_texto.replace(" e ", ", ")

                jogadores = jogadores_texto.split(",")

                for j in jogadores:

                    j = limpar(j)

                    if len(j) < 2:
                        continue

                    dados.append({
                        "selecao": selecao_atual,
                        "jogador": j,
                        "posicao": cat,
                        "categoria_base": CATEGORIAS[cat]
                    })

    df = pd.DataFrame(dados).drop_duplicates()

    return df
