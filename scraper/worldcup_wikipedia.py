import pandas as pd
import requests
import re

from bs4 import BeautifulSoup
from io import StringIO


URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def limpar(texto):

    texto = str(texto)

    texto = re.sub(r"\[.*?\]", "", texto)

    texto = texto.replace("\n", " ")

    return texto.strip()


def extrair_squads():

    print("🌐 Baixando página da Wikipedia...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    print("📄 HTML carregado com sucesso")

    soup = BeautifulSoup(response.text, "lxml")

    dados = []

    # headings das seleções
    headings = soup.find_all(["h2", "h3"])

    for heading in headings:

        titulo = limpar(heading.get_text())

        # ignorar grupos
        if "group" in titulo.lower():
            continue

        # ignorar contents
        if "contents" in titulo.lower():
            continue

        # pegar próxima tabela
        tabela = heading.find_next("table", {"class": "wikitable"})

        if tabela is None:
            continue

        try:

            df = pd.read_html(
                StringIO(str(tabela))
            )[0]

        except:
            continue

        colunas = [
            str(c).lower()
            for c in df.columns
        ]

        # validar tabela de elenco
        if not any(
            x in " ".join(colunas)
            for x in ["player", "name", "club"]
        ):
            continue

        print(f"✅ Seleção encontrada: {titulo}")

        for _, row in df.iterrows():

            valores = [
                limpar(v)
                for v in row.tolist()
                if str(v) != "nan"
            ]

            if len(valores) < 2:
                continue

            try:

                jogador = valores[1]

            except:
                continue

            # posição
            posicao = valores[0]

            clube = valores[-1]

            dados.append({
                "selecao": titulo,
                "jogador": jogador,
                "posicao": posicao,
                "clube": clube,
                "dados_raw": " | ".join(valores)
            })

    df_final = pd.DataFrame(dados)

    df_final = df_final.drop_duplicates()

    print(f"\n📊 Total jogadores encontrados: {len(df_final)}")

    return df_final
