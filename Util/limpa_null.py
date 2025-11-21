import csv
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Pastas definidas no .env
pasta_entrada = os.getenv('UTIL_PASTA', r"D:\\")
pasta_saida = os.getenv('UTIL_PASTA_LIMPO', r"D:\\LIMPOS")

# Garante que a pasta de saída exista
os.makedirs(pasta_saida, exist_ok=True)

# Limpa arquivos antigos na pasta de saída
for f in os.listdir(pasta_saida):
    if f.lower().endswith(".csv"):
        try:
            os.remove(os.path.join(pasta_saida, f))
        except:
            pass

print(f"✓ Pasta limpa: {pasta_saida}")

# Lista CSVs da pasta de origem
arquivos_csv = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(".csv")]

print(f"Encontrados {len(arquivos_csv)} arquivos CSV.\n")

for arquivo in arquivos_csv:
    entrada = os.path.join(pasta_entrada, arquivo)
    saida = os.path.join(pasta_saida, arquivo.replace(".csv", "_limpo.csv"))

    print(f"Limpando NULL de: {arquivo}")

    with open(entrada, "r", encoding="latin1", errors="replace", newline="") as f_in:
        leitor = csv.reader(f_in, delimiter=";")

        with open(saida, "w", encoding="latin1", newline="") as f_out:
            escritor = csv.writer(f_out, delimiter=";")

            for linha in leitor:
                nova_linha = []
                for valor in linha:
                    # Troca exatamente NULL por vazio
                    if valor.strip().upper() == "NULL":
                        nova_linha.append("")
                    else:
                        nova_linha.append(valor)

                escritor.writerow(nova_linha)

    print(f"  ✔ Arquivo limpo criado: {saida}")

print("\n✔ FINALIZADO — Arquivos *limpos* gerados com sucesso.")
