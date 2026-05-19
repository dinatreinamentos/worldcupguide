import re
import requests
import pandas as pd


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


def eh_categoria(linha):
    return any(linha.startswith(c + ":") for c in CATEGORIAS)


def get_categoria(linha):
    for c in CATEGORIAS:
        if linha.startswith(c + ":"):
            return c
    return None


def eh_selecao(linha):
    if "(" in linha and "pré-lista" in linha.lower():
        return False
    if len(linha) > 50:
        return False
    if ":" in linha:
        return False
    if "grupo" in linha.lower():
        return False
    return True


def extrair_jogadores():

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    texto = r.text

    # quebra tudo em linhas reais
    linhas = [
        l.strip()
        for l in texto.split("\n")
        if l.strip()
    ]

    dados = []

    selecao = None
    ignorar = False

    for linha in linhas:

        # Detecta seleção com pré-lista
        if eh_selecao(linha):

            selecao = linha

            if "pré-lista" in linha.lower():
                ignorar = True
            else:
                ignorar = False

            continue

        if ignorar:
            continue

        # Detecta categorias
        if eh_categoria(linha):

            cat = get_categoria(linha)

            bloco = linha.split(":", 1)[1]

            bloco = bloco.replace(" e ", ",")

            jogadores = [j.strip() for j in bloco.split(",")]

            for j in jogadores:

                j = limpar(j)

                if len(j) < 2:
                    continue

                dados.append({
                    "selecao": selecao,
                    "jogador": j,
                    "posicao": cat,
                    "categoria_base": CATEGORIAS[cat]
                })

    return pd.DataFrame(dados).drop_duplicates()
