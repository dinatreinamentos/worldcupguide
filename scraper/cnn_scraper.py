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


def limpar(texto):
    return re.sub(r"\(.*?\)", "", texto).replace(".", "").replace(";", "").strip()


def extrair_jogadores():

    dados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        print("🌐 Abrindo página com Playwright...")

        page.goto(URL, wait_until="networkidle", timeout=60000)

        html = page.content()

        browser.close()

    print("📄 HTML capturado com sucesso")

    linhas = re.split(r"<[^>]+>", html)

    selecao = None

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        # Detecta seleção (heurística simples)
        if len(linha) < 50 and ":" not in linha and "Grupo" not in linha:

            selecao = linha

        # Detecta categorias
        for cat in CATEGORIAS:

            if linha.startswith(cat + ":"):

                jogadores = linha.replace(cat + ":", "")
                jogadores = jogadores.replace(" e ", ",")
                jogadores = jogadores.split(",")

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

    df = pd.DataFrame(dados).drop_duplicates()

    print(f"📊 Total de jogadores encontrados: {len(df)}")

    return df
