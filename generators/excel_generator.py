from pathlib import Path


def salvar_excel(df):

    Path("output").mkdir(
        exist_ok=True
    )

    caminho = "output/copa_2026_base.xlsx"

    df.to_excel(
        caminho,
        index=False
    )

    print(f"\n📁 Planilha salva em: {caminho}")
    print(f"📊 Total de jogadores: {len(df)}")
