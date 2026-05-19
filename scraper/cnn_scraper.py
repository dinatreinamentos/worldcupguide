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
    texto = re.sub(r"\(.*?\)", "", texto)
    texto = texto.replace(".", "").replace(";", "").strip()
    return texto


def eh_categoria(linha):
    return any(linha.startswith(cat + ":") for cat in CATEGORIAS)


def get_categoria(linha):
    for cat in CATEGORIAS:
        if linha.startswith(cat + ":"):
            return cat
    return None


def eh_selecao(linha):
    if len(linha) > 60:
        return False
    if ":" in linha:
        return False
    if "Grupo" in linha:
        return False
    if "Copa do Mundo" in linha:
        return False
    return True


def extrair_jogadores():

    dados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        print("🌐 Abrindo página...")

        page.goto(URL, timeout=60000, wait_until="domcontentloaded")

        # ESSENCIAL: não usar networkidle (quebra no CNN)
        page.wait_for_timeout(5000)

        html = page.content()

        browser.close()

    print("📄 HTML capturado com sucesso")

    # quebra em texto puro
    linhas = re.split(r"<[^>]+>", html)

    selecao_atual = None

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        # detectar seleção
        if eh_selecao(linha):
            selecao_atual = linha
            continue

        if not selecao_atual:
            continue

        # detectar categoria + jogadores
        if eh_categoria(linha):

            cat = get_categoria(linha)

            bloco = linha.split(":", 1)[1]

            bloco = bloco.replace(" e ", ",")

            jogadores = bloco.split(",")

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

    print(f"📊 Total de jogadores encontrados: {len(df)}")

    return df
