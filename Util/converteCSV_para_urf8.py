import csv
import os
import chardet
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Pastas definidas no .env
pasta_entrada = os.getenv('UTIL_PASTA', r"D:\\")
pasta_saida = os.getenv('UTIL_PASTA_SAIDA', r"D:\\UTF8")

# Garante que a pasta de saída exista
os.makedirs(pasta_saida, exist_ok=True)

# Limpa arquivos antigos na pasta de saída
for f in os.listdir(pasta_saida):
    if f.lower().endswith(".csv"):
        try:
            os.remove(os.path.join(pasta_saida, f))
        except:
            pass

print(f"✓ Pasta de saída limpa: {pasta_saida}")

# Lista CSVs da pasta de origem
arquivos_csv = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(".csv")]

print(f"Encontrados {len(arquivos_csv)} arquivos CSV.\n")

for arquivo in arquivos_csv:
    caminho_entrada = os.path.join(pasta_entrada, arquivo)
    nome_saida = arquivo.replace(".csv", "_utf8.csv")
    caminho_saida = os.path.join(pasta_saida, nome_saida)

    print(f"Convertendo para UTF-8: {arquivo}")

    # Detectar encoding
    with open(caminho_entrada, "rb") as f:
        raw = f.read()
    encoding_detectado = chardet.detect(raw)["encoding"]

    print(f"  → Encoding detectado: {encoding_detectado}")

    # Converter e salvar em UTF-8
    with open(caminho_entrada, "r", encoding=encoding_detectado, errors="replace", newline="") as f_in:
        leitor = csv.reader(f_in, delimiter=";")

        with open(caminho_saida, "w", encoding="utf-8", newline="") as f_out:
            escritor = csv.writer(f_out, delimiter=";")
            for linha in leitor:
                escritor.writerow(linha)

    print(f"  ✔ Gerado: {caminho_saida}")

print("\n✔ FINALIZADO — Arquivos convertidos para UTF-8 criados.")
