import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações
INPUT_FOLDER = os.getenv('JSON_INPUT_FOLDER', "C:/Users/Meu Computador/Documents/backup(1)")
OUTPUT_BASE = os.getenv('JSON_OUTPUT_BASE', "output")
OUTPUT_EXT = ".sql"
LIMITE_TAMANHO = int(os.getenv('JSON_LIMITE_TAMANHO', int(2.20 * 1024 * 1024)))

# Variáveis globais
table_definitions = {}
sql_content = ""
file_count = 1

# ---------------- Funções ----------------

def sql_type(value):
    if isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        return "FLOAT"
    elif isinstance(value, bool):
        return "BIT"
    elif isinstance(value, str):
        return "NVARCHAR(MAX)"
    else:
        return "NVARCHAR(MAX)"

def truncar_valor(value):
    """Trunca strings que excedem o limite de bytes"""
    if isinstance(value, str) and len(value.encode("utf-8")) > LIMITE_TAMANHO:
        truncated = value.encode("utf-8")[:LIMITE_TAMANHO]
        return truncated.decode("utf-8", errors="ignore")
    return value

def escrever_sql(texto):
    """Escreve conteúdo SQL no arquivo, criando novo se ultrapassar limite"""
    global sql_content, file_count
    sql_content += texto
    if len(sql_content.encode("utf-8")) > LIMITE_TAMANHO:
        filename = f"{OUTPUT_BASE}_{file_count}{OUTPUT_EXT}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(sql_content)
        print(f"Arquivo gerado: {filename}")
        file_count += 1
        sql_content = ""  # inicia novo arquivo

def collect_columns(data):
    """Coleta todas as chaves de todos os objetos de uma lista JSON"""
    columns = set()
    for obj in data:
        if isinstance(obj, dict):
            columns.update(obj.keys())
    return columns

def ensure_table(name, columns, parent=None):
    """Cria tabela com todas as colunas"""
    if name in table_definitions:
        return
    cols = ["id INT IDENTITY PRIMARY KEY"]
    if parent:
        cols.append(f"{parent}_id INT FOREIGN KEY REFERENCES {parent}(id)")
    for col in columns:
        cols.append(f"[{col}] NVARCHAR(MAX)")
    ddl = f"CREATE TABLE {name} (\n    " + ",\n    ".join(cols) + "\n);\n"
    table_definitions[name] = columns  # guarda as colunas da tabela
    escrever_sql(ddl + "\n")

def handle_object(table, obj, parent=None):
    """Gera INSERTs para o objeto, criando tabelas filhas se necessário"""
    # Garante que a tabela exista
    if table not in table_definitions:
        if isinstance(obj, dict):
            ensure_table(table, obj.keys(), parent)
        else:
            ensure_table(table, {"value"}, parent)

    columns = table_definitions[table]
    cols, vals = [], []

    for key, value in obj.items():
        value = truncar_valor(value)
        if isinstance(value, dict):
            handle_object(f"{table}_{key}", value, table)
        elif isinstance(value, list):
            for item in value:
                item = truncar_valor(item)
                if isinstance(item, dict):
                    handle_object(f"{table}_{key}", item, table)
                else:
                    ensure_table(f"{table}_{key}", {"value"}, table)
                    safe_item = str(item).replace("'", "''")
                    if parent:
                        escrever_sql(f"INSERT INTO {table}_{key} ({table}_id, value) VALUES (SCOPE_IDENTITY(), N'{safe_item}');\n")
                    else:
                        escrever_sql(f"INSERT INTO {table}_{key} (value) VALUES (N'{safe_item}');\n")

    # Preenche todas as colunas da tabela
    for col in columns:
        value = obj.get(col)
        cols.append(f"[{col}]")
        if isinstance(value, str):
            safe_v = value.replace("'", "''")
            vals.append(f"N'{safe_v}'")
        elif value is None:
            vals.append("NULL")
        elif isinstance(value, bool):
            vals.append("1" if value else "0")
        elif isinstance(value, (int, float)):
            vals.append(str(value))
        else:
            vals.append("NULL")

    if cols:
        texto_insert = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(vals)});\n"
        escrever_sql(texto_insert)


# ---------------- Main ----------------

def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".json"):
            table_name = os.path.splitext(filename)[0]
            with open(os.path.join(INPUT_FOLDER, filename), "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list) and data:
                all_columns = collect_columns(data)
                ensure_table(table_name, all_columns)
                for obj in data:
                    handle_object(table_name, obj)
            elif isinstance(data, dict):
                ensure_table(table_name, data.keys())
                handle_object(table_name, data)

    # salva o restante do conteúdo
    if sql_content:
        filename = f"{OUTPUT_BASE}_{file_count}{OUTPUT_EXT}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(sql_content)
        print(f"Arquivo final gerado: {filename}")

if __name__ == "__main__":
    main()
