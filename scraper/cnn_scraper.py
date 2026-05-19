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

    nome = nome.replace(";", "")
    nome = nome.replace(".", "")

    return nome


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
        ["h3", "li"]
    )

    for elemento in elementos:

        texto = elemento.get_text(
            " ",
            strip=True
        )

        # Seleções
        if elemento.name == "h3":

            texto_limpo = texto.strip()

            if (
                len(texto_limpo) <= 40
                and "Grupo" not in texto_limpo
            ):
                selecao_atual = texto_limpo

        # Jogadores
        elif elemento.name == "li":

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

                        if not jogador:
                            continue

                        dados.append({
                            "selecao": selecao_atual,
                            "jogador": jogador,
                            "posicao": categoria_texto,
                            "categoria_base": categoria_base
                        })

    return pd.DataFrame(dados)
