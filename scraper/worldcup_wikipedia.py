import pandas as pd
import requests
import re
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

    texto = texto.strip()

    return texto


def extrair_squads():

    print("🌐 Baixando página da Wikipedia...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    print("📄 HTML carregado com sucesso")

    # 🔥 CORREÇÃO AQUI
    html_io = StringIO(response.text)

    tabelas = pd.read_html(html_io)

    print(f"📊 Total de tabelas encontradas: {len(tabelas)}")

    dados = []

    for tabela in tabelas:

        try:

            colunas = [
                str(c).lower()
                for c in tabela.columns
            ]

            colunas_texto = " ".join(colunas)

            # tenta identificar tabelas de jogadores
            if not any(
                x in colunas_texto
                for x in ["player", "name", "pos."]
            ):
                continue

            print(f"✅ Tabela válida encontrada")

            for _, row in tabela.iterrows():

                valores = [
                    limpar(v)
                    for v in row.tolist()
                    if str(v) != "nan"
                ]

                if len(valores) < 2:
                    continue

                jogador = valores[0]

                # ignora headers repetidos
                if jogador.lower() in [
                    "player",
                    "name",
                    "no."
                ]:
                    continue

                dados.append({
                    "jogador": jogador,
                    "dados_raw": " | ".join(valores)
                })

        except Exception as e:

            print(f"⚠️ erro em tabela: {e}")

            continue

    df = pd.DataFrame(dados)

    df = df.drop_duplicates()

    print(f"\n📊 Total jogadores encontrados: {len(df)}")

    return df
