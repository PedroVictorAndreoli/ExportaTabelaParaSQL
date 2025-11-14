import pandas as pd
import os
import datetime
import csv

# Caminho da pasta com os arquivos CSV
pasta = r"C:\Users\Meu Computador\Documents\DADOS\anexos"
arquivos = [f for f in os.listdir(pasta) if f.endswith('.csv')]

LIMITE_TAMANHO = int(2.2 * 1024 * 1024)  # 2,2 MB em bytes
contador_arquivo = 1
tamanho_atual = 0


def abrir_novo_arquivo():
    global contador_arquivo, tamanho_atual
    nome_arquivo = f"backup_{contador_arquivo}.sql"
    contador_arquivo += 1
    tamanho_atual = 0
    return open(nome_arquivo, "w", encoding="utf-8")


def tipo_sql(serie):
    if pd.api.types.is_integer_dtype(serie):
        if serie.max() > 2_147_483_647 or serie.min() < -2_147_483_648:
            return "BIGINT"
        return "INT"
    elif pd.api.types.is_float_dtype(serie):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(serie):
        return "BIT"
    elif pd.api.types.is_datetime64_any_dtype(serie):
        return "DATETIME"
    else:
        return "NVARCHAR(MAX)"


def ler_csv_corretamente(caminho):
    """Lê o CSV corretamente lidando com o formato específico"""
    try:
        # Primeira tentativa: usar o módulo csv do Python para entender a estrutura
        with open(caminho, 'r', encoding='utf-8') as f:
            # Detecta o dialeto do CSV
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            
            # Lê o CSV
            reader = csv.reader(f, dialect)
            linhas = list(reader)
        
        if linhas:
            # Cria DataFrame a partir das linhas processadas
            df = pd.DataFrame(linhas[1:], columns=linhas[0])
            return df
            
    except Exception as e:
        print(f"Erro na leitura avançada: {e}")
    
    # Fallback: tenta abordagem mais direta
    try:
        df = pd.read_csv(caminho, encoding="utf-8", sep=',', quotechar='"', 
                        doublequote=True, escapechar=None, header=0)
        return df
    except:
        pass
    
    # Última tentativa: ler como texto e processar manualmente
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Processa manualmente se necessário
        linhas = content.strip().split('\n')
        if linhas:
            # Remove aspas externas e split por vírgula
            dados_processados = []
            for linha in linhas:
                # Remove aspas do início e fim, depois split
                linha_limpa = linha.strip().strip('"')
                campos = [campo.strip().strip('"') for campo in linha_limpa.split('","')]
                dados_processados.append(campos)
            
            if dados_processados:
                df = pd.DataFrame(dados_processados[1:], columns=dados_processados[0])
                return df
    except Exception as e:
        print(f"Erro no processamento manual: {e}")
    
    return None


out_sql = abrir_novo_arquivo()

for arquivo in arquivos:
    nome_tabela = os.path.splitext(arquivo)[0]
    caminho = os.path.join(pasta, arquivo)

    # Detecta tipo de arquivo
    if arquivo.endswith(".csv"):
        df = ler_csv_corretamente(caminho)
        if df is None:
            print(f"Erro: Não foi possível ler o arquivo '{arquivo}' corretamente")
            continue
    elif arquivo.endswith(".xlsx"):
        df = pd.read_excel(caminho)
    else:
        continue

    if df.empty:
        print(f"Tabela '{nome_tabela}' ignorada (sem registros).")
        continue

    # Verifica se as colunas foram lidas corretamente
    print(f"Processando {nome_tabela}: {len(df.columns)} colunas")
    print(f"Colunas: {list(df.columns)}")

    # CREATE TABLE
    linhas_create = []
    linhas_create.append(f"-- Tabela: {nome_tabela}\n")
    linhas_create.append(f"IF OBJECT_ID(N'{nome_tabela}', N'U') IS NOT NULL DROP TABLE [{nome_tabela}];\n")
    linhas_create.append(f"CREATE TABLE [{nome_tabela}] (\n")

    colunas = []
    for coluna in df.columns:
        # Limpa o nome da coluna
        coluna_limpa = str(coluna).strip().strip('"')
        tipo = tipo_sql(df[coluna])
        colunas.append(f"    [{coluna_limpa}] {tipo}")
    linhas_create.append(",\n".join(colunas))
    linhas_create.append("\n);\n\n")

    for linha in linhas_create:
        linha_bytes = linha.encode("utf-8")
        if tamanho_atual + len(linha_bytes) > LIMITE_TAMANHO:
            out_sql.close()
            out_sql = abrir_novo_arquivo()
        out_sql.write(linha)
        tamanho_atual += len(linha_bytes)

    # INSERT INTO
    for _, row in df.iterrows():
        valores = []
        for v in row:
            if pd.isnull(v):
                valores.append("NULL")
            elif isinstance(v, str):
                # Remove aspas extras e escapa aspas simples
                v_limpo = v.strip().strip('"')
                v_limpo = v_limpo.replace("'", "''")
                valores.append("'" + v_limpo + "'")
            elif isinstance(v, (pd.Timestamp, datetime.datetime, datetime.date)):
                if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime):
                    valores.append(f"'{v.strftime('%Y-%m-%d')}'")
                else:
                    valores.append(f"'{v.strftime('%Y%m%d %H:%M:%S')}'")
            else:
                valores.append(str(v))

        linha_insert = f"INSERT INTO [{nome_tabela}] VALUES ({', '.join(valores)});\n"
        linha_bytes = linha_insert.encode("utf-8")
        if tamanho_atual + len(linha_bytes) > LIMITE_TAMANHO:
            out_sql.close()
            out_sql = abrir_novo_arquivo()
        out_sql.write(linha_insert)
        tamanho_atual += len(linha_bytes)

    out_sql.write("\n")

out_sql.close()