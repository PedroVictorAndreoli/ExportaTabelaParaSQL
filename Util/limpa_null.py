import csv
import os

pasta = r"CAMINHO"

arquivos_csv = [f for f in os.listdir(pasta) if f.lower().endswith(".csv")]

print(f"Encontrados {len(arquivos_csv)} arquivos CSV.")

for arquivo in arquivos_csv:
    entrada = os.path.join(pasta, arquivo)
    saida = os.path.join(pasta, arquivo.replace(".csv", "_limpo.csv"))

    print(f"\nLimpando NULL de: {arquivo}")

    with open(entrada, "r", encoding="latin1", errors="replace", newline="") as f_in:
        leitor = csv.reader(f_in, delimiter=";")

        with open(saida, "w", encoding="latin1", newline="") as f_out:
            escritor = csv.writer(f_out, delimiter=";")

            for linha in leitor:
                nova_linha = []
                for valor in linha:
                    if valor.strip().upper() == "NULL":
                        nova_linha.append("")
                    else:
                        nova_linha.append(valor)

                escritor.writerow(nova_linha)

    print(f"  ✔ Arquivo limpo criado: {saida}")

print("\n✔ FINALIZADO — Arquivos *limpos* gerados com sucesso.")
