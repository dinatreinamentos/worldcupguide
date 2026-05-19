import re
import pandas as pd
from playwright.sync_api import sync_playwright


URL = "https://www.cnnbrasil.com.br/esportes/futebol/copa-do-mundo/listas-convocados-todas-48-selecoes-copa-do-mundo-2026/"


CATEGORIAS = {
    "Goleiros": "goleiro",
    "Defensores": "defesa",
    "Meio-campistas": "meio-campo",
    "Atacantes": "ataque"
}


def limpar(t):
    return re.sub(r"\(.*?\)", "", t).strip()


def extrair_jogadores():

    dados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60000)

        html = page.content()

        browser.close()

    # parsing simples em cima do HTML renderizado
    linhas = re.split(r"<[^>]+>", html)

    selecao = None

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        if len(linha) < 40 and ":" not in linha:
            selecao = linha

        for cat in CATEGORIAS:

            if linha.startswith(cat + ":"):

                jogadores = linha.replace(cat + ":", "")
                jogadores = jogadores.replace(" e ", ",").split(",")

                for j in jogadores:

                    j = limpar(j)

                    if len(j) > 1:

                        dados.append({
                            "selecao": selecao,
                            "jogador": j,
                            "posicao": cat,
                            "categoria_base": CATEGORIAS[cat]
                        })

    return pd.DataFrame(dados).drop_duplicates()
