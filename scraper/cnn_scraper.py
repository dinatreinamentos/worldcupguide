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


def eh_pre_lista(texto):

    texto = texto.lower()

    palavras = [
        "pré-lista",
        "pre-lista",
        "lista preliminar",
        "possíveis convocados",
        "aguardando convocação"
    ]

    return any(p in texto for p in palavras)


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

    artigos = soup.find_all(
        ["h2", "h3", "p", "li"]
    )

    for elemento in artigos:

        texto = elemento.get_text(
            " ",
            strip=True
        )

        if not texto:
            continue

        # Ignorar pré-listas
        if eh_pre_lista(texto):
            continue

        # Detectar seleção
        if elemento.name in ["h2", "h3"]:

            texto_limpo = texto.strip()

            if (
                len(texto_limpo) <= 40
                and ":" not in texto_limpo
                and "grupo" not in texto_limpo.lower()
                and "convocados" not in texto_limpo.lower()
            ):

                selecao_atual = texto_limpo

                print(f"\n🌎 Seleção encontrada: {selecao_atual}")

        # Buscar jogadores
        for categoria_texto, categoria_base in MAPA_CATEGORIAS.items():

            prefixo = f"{categoria_texto}:"

            if texto.startswith(prefixo):

                jogadores_texto = texto.replace(
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

                    if len(jogador) <= 1:
                        continue

                    if jogador.lower() in [
                        "nenhum",
                        "não definido"
                    ]:
                        continue

                    dados.append({
                        "selecao": selecao_atual,
                        "jogador": jogador,
                        "posicao": categoria_texto,
                        "categoria_base": categoria_base
                    })

    df = pd.DataFrame(dados)

    df = df.drop_duplicates()

    return df
