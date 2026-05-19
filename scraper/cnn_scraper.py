# scraper/cnn_scraper.py

import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path


URL = "https://www.cnnbrasil.com.br/esportes/futebol/copa-do-mundo/listas-convocados-todas-48-selecoes-copa-do-mundo-2026/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def normalizar_categoria(posicao):
    posicao = posicao.lower()

    if any(x in posicao for x in [
        "atacante",
        "ponta",
        "centroavante",
        "segundo atacante"
    ]):
        return "ataque"

    if any(x in posicao for x in [
        "meia",
        "volante",
        "meio-campista"
    ]):
        return "meio-campo"

    if any(x in posicao for x in [
        "zagueiro",
        "lateral",
        "defensor"
    ]):
        return "defesa"

    if "goleiro" in posicao:
        return "goleiro"

    return "desconhecido"


def extrair_jogadores():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    dados = []

    selecao_atual = None

    elementos = soup.find_all(
        ["h2", "h3", "li"]
    )

    for elemento in elementos:

        texto = elemento.get_text(
            strip=True
        )

        if elemento.name in ["h2", "h3"]:

            texto_limpo = texto.strip()

            if (
                len(texto_limpo) <= 40
                and "Convocados" not in texto_limpo
            ):
                selecao_atual = texto_limpo

        elif elemento.name == "li":

            if " - " not in texto:
                continue

            partes = texto.split(" - ")

            if len(partes) < 2:
                continue

            jogador = partes[0].strip()
            posicao = partes[1].strip()

            categoria = normalizar_categoria(
                posicao
            )

            dados.append({
                "selecao": selecao_atual,
                "jogador": jogador,
                "posicao": posicao,
                "categoria_base": categoria
            })

    return pd.DataFrame(dados)


def salvar_excel(df):

    Path("output").mkdir(
        exist_ok=True
    )

    caminho = "output/copa_2026_base.xlsx"

    df.to_excel(
        caminho,
        index=False
    )

    print("\n✅ Planilha criada com sucesso!")
    print(f"📁 Arquivo: {caminho}")
    print(f"📊 Total de jogadores: {len(df)}")


def main():

    print("🌎 Lendo dados da CNN...\n")

    df = extrair_jogadores()

    print(df.head())

    salvar_excel(df)


if __name__ == "__main__":
    main()
