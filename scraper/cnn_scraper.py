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


MAPA_CATEGORIAS = {
    "Goleiros": "goleiro",
    "Defensores": "defesa",
    "Meio-campistas": "meio-campo",
    "Atacantes": "ataque"
}


def limpar_nome(nome):

    nome = nome.strip()

    nome = re.sub(r"\(.*?\)", "", nome)

    nome = nome.replace(";", "")
    nome = nome.replace(".", "")

    return nome.strip()


def eh_grupo(texto):

    return texto.startswith("Grupo ")


def eh_pre_lista(texto):

    return "(pré-lista)" in texto.lower()


def eh_selecao(texto):

    texto = texto.strip()

    if ":" in texto:
        return False

    if eh_grupo(texto):
        return False

    if len(texto) > 40:
        return False

    return True


def processar_linha_jogadores(
    linha,
    selecao,
    dados
):

    for categoria_texto, categoria_base in MAPA_CATEGORIAS.items():

        prefixo = f"{categoria_texto}:"

        if linha.startswith(prefixo):

            jogadores_texto = linha.replace(
                prefixo,
                ""
            ).strip()

            jogadores_texto = jogadores_texto.replace(
                " e ",
                ", "
            )

            jogadores = jogadores_texto.split(",")

            for jogador in jogadores:

                jogador = limpar_nome(
                    jogador
                )

                if not jogador:
                    continue

                dados.append({
                    "selecao": selecao,
                    "jogador": jogador,
                    "posicao": categoria_texto,
                    "categoria_base": categoria_base
                })


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

    texto = soup.get_text("\n")

    linhas = [
        linha.strip()
        for linha in texto.split("\n")
        if linha.strip()
    ]

    dados = []

    selecao_atual = None

    ignorar_bloco = False

    for linha in linhas:

        # Ignorar grupos
        if eh_grupo(linha):
            continue

        # Detectar seleção
        if eh_selecao(linha):

            if eh_pre_lista(linha):

                ignorar_bloco = True

                selecao_atual = None

                print(f"⛔ Ignorando pré-lista: {linha}")

                continue

            ignorar_bloco = False

            selecao_atual = linha

            print(f"🌎 Seleção encontrada: {linha}")

            continue

        # Ignorar bloco inválido
        if ignorar_bloco:
            continue

        # Processar jogadores
        if selecao_atual:

            processar_linha_jogadores(
                linha,
                selecao_atual,
                dados
            )

    df = pd.DataFrame(dados)

    df = df.drop_duplicates()

    return df
