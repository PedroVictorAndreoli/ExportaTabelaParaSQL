import pandas as pd
import os
import datetime
import csv

# Caminho da pasta com os arquivos CSV
pasta = r"D:\aaaaaa\BKP ANDIARA MATRIZ"
arquivos = [f for f in os.listdir(pasta) if f.endswith('.csv')]

# Limite de 3MB por arquivo SQL
LIMITE_BYTES = 3 * 1024 * 1024

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
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            reader = csv.reader(f, dialect)
            linhas = list(reader)
            if linhas:
                df = pd.DataFrame(linhas[1:], columns=linhas[0])
                return df
    except:
        pass
    
    try:
        return pd.read_csv(caminho, encoding="utf-8", sep=',', quotechar='"', 
                          doublequote=True, escapechar=None, header=0)
    except:
        pass
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            content = f.read()
            linhas = content.strip().split('\n')
            if linhas:
                dados_processados = []
                for linha in linhas:
                    linha_limpa = linha.strip().strip('"')
                    campos = [campo.strip().strip('"') for campo in linha_limpa.split('","')]
                    dados_processados.append(campos)
                df = pd.DataFrame(dados_processados[1:], columns=dados_processados[0])
                return df
    except:
        pass
    
    return None

# Controle de arquivos SQL
arquivos_sql = []
parte_atual = 1
tamanho_atual = 0
arquivo_sql = None

def abrir_novo_arquivo():
    global arquivo_sql, parte_atual, tamanho_atual
    if arquivo_sql:
        arquivo_sql.close()
    nome_arquivo = f"backup_parte_{parte_atual:03d}.sql"
    arquivo_sql = open(nome_arquivo, "w", encoding="utf-8")
    arquivos_sql.append(nome_arquivo)
    tamanho_atual = 0
    print(f"✓ Criado: {nome_arquivo}")
    return arquivo_sql

def escrever_sql(texto):
    global tamanho_atual, parte_atual, arquivo_sql
    
    if arquivo_sql is None:
        abrir_novo_arquivo()
    
    tamanho_texto = len(texto.encode('utf-8'))
    
    if tamanho_atual + tamanho_texto > LIMITE_BYTES:
        parte_atual += 1
        abrir_novo_arquivo()
    
    arquivo_sql.write(texto)
    tamanho_atual += tamanho_texto


# LISTAS PARA CRIAR NA ORDEM CORRETA
creates = []        # Lista de CREATE TABLE
all_inserts = []    # Lista com tuplas (tabela, lista_de_inserts)


print("Iniciando geração dos arquivos SQL...\n")
print(f"Total de arquivos CSV encontrados: {len(arquivos)}\n")

tabelas_processadas = 0

for arquivo in arquivos:
    nome_tabela = os.path.splitext(arquivo)[0]
    caminho = os.path.join(pasta, arquivo)
    
    print(f"\n{'='*60}")
    print(f"Arquivo: {arquivo}")
    print(f"{'='*60}")
    
    if arquivo.endswith(".csv"):
        df = ler_csv_corretamente(caminho)
        if df is None:
            print(f"❌ Erro: Não foi possível ler '{arquivo}'")
            continue
        print(f"✓ CSV lido com sucesso: {len(df)} linhas")
    else:
        print(f"⚠ Ignorado (não é CSV)")
        continue
    
    if df.empty:
        print(f"⚠ Tabela ignorada (sem registros)")
        continue
    
    colunas_antes = len(df.columns)
    df = df.dropna(axis=1, how='all')
    colunas_depois = len(df.columns)
    
    if colunas_antes != colunas_depois:
        print(f"⚠ Removidas {colunas_antes - colunas_depois} colunas vazias")
    
    if df.empty or len(df.columns) == 0:
        print(f"⚠ Tabela ignorada (sem colunas válidas)")
        continue
    
    print(f"✓ Processando: {len(df)} registros, {len(df.columns)} colunas")
    
    novas_colunas = []
    contador_vazio = 1
    
    for coluna in df.columns:
        coluna_limpa = str(coluna).strip().strip('"')
        
        if not coluna_limpa:
            coluna_limpa = f"Coluna_{contador_vazio}"
            contador_vazio += 1
        
        coluna_limpa = coluna_limpa.replace('[', '').replace(']', '').replace(' ', '_')
        
        novas_colunas.append(coluna_limpa)
    
    df.columns = novas_colunas
    
    create_sql = f"\n-- Tabela: {nome_tabela}\n"
    create_sql += f"IF OBJECT_ID(N'{nome_tabela}', N'U') IS NOT NULL DROP TABLE [{nome_tabela}];\n"
    create_sql += f"CREATE TABLE [{nome_tabela}] (\n"
    
    colunas_sql = []
    for coluna in df.columns:
        tipo = tipo_sql(df[coluna])
        colunas_sql.append(f"    [{coluna}] {tipo}")
    
    create_sql += ",\n".join(colunas_sql)
    create_sql += "\n);\n\n"
    
    creates.append(create_sql)
    tabelas_processadas += 1
    
    inserts_sql = []
    total_registros = 0
    
    for _, row in df.iterrows():
        total_registros += 1
        valores = []
        
        for v in row:
            if pd.isnull(v) or v == '' or str(v).strip() == '':
                valores.append("NULL")
            elif isinstance(v, (int, float)):
                valores.append(str(v))
            elif isinstance(v, str):
                v_limpo = v.strip().strip('"').replace("'", "''")
                valores.append("'" + v_limpo + "'")
            elif isinstance(v, (pd.Timestamp, datetime.datetime, datetime.date)):
                if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime):
                    valores.append(f"'{v.strftime('%Y-%m-%d')}'")
                else:
                    valores.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
            else:
                valores.append("'" + str(v).replace("'", "''") + "'")
        
        inserts_sql.append(f"INSERT INTO [{nome_tabela}] VALUES ({', '.join(valores)});\n")
    
    all_inserts.append((nome_tabela, inserts_sql))
    print(f"✓ {total_registros} INSERTs preparados")


# ========================
# AGORA ESCREVE OS ARQUIVOS
# ========================

print("\n\nEscrevendo TODOS os CREATE TABLE primeiro...\n")
for create in creates:
    escrever_sql(create)

print("\nEscrevendo TODOS os INSERTs...\n")
for nome_tabela, inserts in all_inserts:
    for ins in inserts:
        escrever_sql(ins)
    escrever_sql(f"-- Total: {len(inserts)} registros da tabela {nome_tabela}\n\n")

if arquivo_sql:
    arquivo_sql.close()

print(f"\n\n{'='*60}")
print("✓ CONCLUÍDO!")
print(f"✓ Tabelas processadas: {tabelas_processadas}")
print(f"✓ Arquivos SQL gerados: {len(arquivos_sql)}")
print(f"{'='*60}\n")


# CRIA SCRIPT MESTRE
print("Gerando script mestre EXECUTAR_TODOS.sql ...\n")

caminho_completo = os.path.abspath(".")

with open("EXECUTAR_TODOS.sql", "w", encoding="utf-8") as master:
    master.write("-- ========================================\n")
    master.write("-- SCRIPT MESTRE - EXECUTA TODOS OS BACKUPS\n")
    master.write("-- ========================================\n\n")
    master.write("USE [SeuBancoDeDados]; -- ALTERE ESTE NOME\nGO\n\n")
    
    for i, arq_sql in enumerate(arquivos_sql, 1):
        caminho_arquivo = os.path.join(caminho_completo, arq_sql)
        master.write(f"-- Parte {i}/{len(arquivos_sql)}\n")
        master.write(f":r \"{caminho_arquivo}\"\nGO\n\n")

print("✓ Criado: EXECUTAR_TODOS.sql")
print(f"\n📁 Caminho dos arquivos: {caminho_completo}")
print("\n" + "="*60)
print("COMO EXECUTAR:")
print("="*60)
print("1. Abra o SQL Server Management Studio (SSMS)")
print("2. Edite o arquivo EXECUTAR_TODOS.sql")
print("3. Altere 'SeuBancoDeDados' para o nome correto")
print("4. Vá em: Query > SQLCMD Mode (ative)")
print("5. Execute o script (F5)")
print("="*60)
