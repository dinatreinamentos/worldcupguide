import pandas as pd


URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads"


def extrair_squads():

    # Lê TODAS as tabelas da página
    tabelas = pd.read_html(URL)

    dados = []

    for tabela in tabelas:

        colunas = [str(c).lower() for c in tabela.columns]

        # tenta identificar tabelas de elenco
        if any("player" in c or "name" in c for c in colunas):

            for _, row in tabela.iterrows():

                valores = row.dropna().tolist()

                if len(valores) < 2:
                    continue

                # heurística: último campo costuma ser posição/clube/etc
                jogador = str(valores[0]).strip()

                if jogador.lower() in ["player", "name"]:
                    continue

                dados.append({
                    "jogador": jogador,
                    "raw": " | ".join(map(str, valores))
                })

    return pd.DataFrame(dados).drop_duplicates()
