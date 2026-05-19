from scraper.worldcup_wikipedia import extrair_squads
from generators.excel_generator import salvar_excel


def main():

    print("🌎 Iniciando pipeline (Fonte: Wikipedia)...\n")

    df = extrair_squads()

    print(df.head())

    print(f"\n📊 Total jogadores: {len(df)}")

    salvar_excel(df)

    print("\n✅ Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    main()
