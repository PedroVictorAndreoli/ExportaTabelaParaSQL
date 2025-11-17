import csv
import os
import chardet

# 👉 Informe aqui a pasta onde estão os CSVs
pasta = r"CAMINHO"

# Listar todos os arquivos CSV da pasta
arquivos_csv = [f for f in os.listdir(pasta) if f.lower().endswith(".csv")]

print(f"Encontrados {len(arquivos_csv)} arquivos CSV.")

for arquivo in arquivos_csv:
    caminho_entrada = os.path.join(pasta, arquivo)
    caminho_saida = os.path.join(
        pasta,
        arquivo.replace(".csv", "_corrigido.csv")
    )

    print(f"\nProcessando: {arquivo}")

    # Detectar encoding
    with open(caminho_entrada, "rb") as f:
        raw = f.read()
        encoding_detectado = chardet.detect(raw)["encoding"]

    print(f"  → Encoding detectado: {encoding_detectado}")

    # Ler arquivo com o encoding detectado
    with open(caminho_entrada, "r", encoding=encoding_detectado, errors="replace", newline="") as f_in:
        leitor = csv.reader(f_in, delimiter=";")

        # Criar arquivo UTF-8 corrigido
        with open(caminho_saida, "w", encoding="utf-8", newline="") as f_out:
            escritor = csv.writer(f_out, delimiter=";")

            for linha in leitor:
                nova_linha = []
                for valor in linha:

                    # Converter NULL para vazio
                    if valor.strip().upper() == "NULL":
                        nova_linha.append("")
                    else:
                        nova_linha.append(valor)

                escritor.writerow(nova_linha)

    print(f"  ✔ Arquivo gerado: {caminho_saida}")

print("\nFinalizado com sucesso!")
