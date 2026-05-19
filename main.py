from scraper.cnn_scraper import extrair_jogadores
from generators.excel_generator import salvar_excel


def main():

    print("🌎 Iniciando pipeline da Copa 2026...\n")

    df = extrair_jogadores()

    print(df.head())

    salvar_excel(df)

    print("\n✅ Processo concluído com sucesso!")


if __name__ == "__main__":
    main()
