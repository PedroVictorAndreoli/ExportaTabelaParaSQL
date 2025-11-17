import csv
import os
import chardet

pasta = r"D:\"

arquivos_csv = [f for f in os.listdir(pasta) if f.lower().endswith(".csv")]

print(f"Encontrados {len(arquivos_csv)} arquivos CSV.")

for arquivo in arquivos_csv:
    entrada = os.path.join(pasta, arquivo)
    saida = os.path.join(pasta, arquivo.replace(".csv", "_utf8.csv"))

    print(f"\nConvertendo para UTF-8: {arquivo}")

    # Detectar encoding real
    with open(entrada, "rb") as f:
        raw = f.read()
    encoding = chardet.detect(raw)["encoding"]

    print(f"  → Encoding detectado: {encoding}")

    # Converter
    with open(entrada, "r", encoding=encoding, errors="replace", newline="") as f_in:
        leitor = csv.reader(f_in, delimiter=";")

        with open(saida, "w", encoding="utf-8", newline="") as f_out:
            escritor = csv.writer(f_out, delimiter=";")

            for linha in leitor:
                escritor.writerow(linha)

    print(f"  ✔ Arquivo convertido desenvolvido: {saida}")

print("\n✔ FINALIZADO — Arquivos em UTF-8 foram criados.")
