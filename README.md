# ExportaTabelaParaSQL

Ferramentas Python para conversão de arquivos CSV e JSON em scripts SQL compatíveis com SQL Server.

## 📋 Descrição

Este projeto contém dois scripts principais que automatizam a conversão de dados estruturados (CSV e JSON) em arquivos SQL com comandos `CREATE TABLE` e `INSERT INTO`, prontos para serem executados em bancos de dados SQL Server.

## 🚀 Funcionalidades

### `main.py` - Conversor de CSV para SQL
- Converte arquivos CSV para scripts SQL
- Suporta arquivos Excel (.xlsx)
- Detecta automaticamente tipos de dados (INT, BIGINT, FLOAT, BIT, DATETIME, NVARCHAR)
- Lida com diferentes formatos de CSV (delimitadores, aspas, escape characters)
- Divide arquivos SQL em múltiplos arquivos quando ultrapassam 2.2 MB
- Trata valores nulos e caracteres especiais

### `jsons.py` - Conversor de JSON para SQL
- Converte arquivos JSON para scripts SQL
- Suporta estruturas JSON complexas (objetos aninhados e arrays)
- Cria tabelas relacionadas automaticamente para dados hierárquicos
- Gera chaves primárias e estrangeiras
- Divide arquivos SQL em múltiplos arquivos quando ultrapassam 2.2 MB
- Trunca valores muito grandes automaticamente

## 📦 Requisitos

```bash
pip install pandas
```

## 🔧 Configuração

### main.py
Edite as seguintes variáveis no início do arquivo:

```python
pasta = r"C:\Users\Meu Computador\Documents\DADOS\anexos"  # Pasta com arquivos CSV
LIMITE_TAMANHO = int(2.2 * 1024 * 1024)  # Tamanho máximo por arquivo SQL (2.2 MB)
```

### jsons.py
Edite as seguintes variáveis no início do arquivo:

```python
INPUT_FOLDER = "C:/Users/Meu Computador/Documents/backup(1)"  # Pasta com arquivos JSON
OUTPUT_BASE = "output"  # Nome base dos arquivos de saída
LIMITE_TAMANHO = int(2.20 * 1024 * 1024)  # Tamanho máximo por arquivo SQL (2.2 MB)
```

## 💻 Uso

### Convertendo arquivos CSV:

```bash
python main.py
```

O script irá:
1. Ler todos os arquivos `.csv` da pasta configurada
2. Gerar arquivos `backup_1.sql`, `backup_2.sql`, etc.
3. Cada arquivo conterá comandos CREATE TABLE e INSERT INTO

### Convertendo arquivos JSON:

```bash
python jsons.py
```

O script irá:
1. Ler todos os arquivos `.json` da pasta configurada
2. Gerar arquivos `output_1.sql`, `output_2.sql`, etc.
3. Criar tabelas relacionadas para estruturas hierárquicas

## 📝 Exemplos

### Estrutura CSV de Entrada
```csv
id,nome,idade,salario
1,"João Silva",30,5000.50
2,"Maria Santos",25,4500.00
```

### Saída SQL Gerada
```sql
-- Tabela: exemplo
IF OBJECT_ID(N'exemplo', N'U') IS NOT NULL DROP TABLE [exemplo];
CREATE TABLE [exemplo] (
    [id] INT,
    [nome] NVARCHAR(MAX),
    [idade] INT,
    [salario] FLOAT
);

INSERT INTO [exemplo] VALUES (1, 'João Silva', 30, 5000.5);
INSERT INTO [exemplo] VALUES (2, 'Maria Santos', 25, 4500.0);
```

## 🔍 Detecção de Tipos de Dados

O script `main.py` detecta automaticamente os tipos SQL:

| Tipo Python/Pandas | Tipo SQL |
|-------------------|----------|
| Inteiros (até 2^31) | INT |
| Inteiros (> 2^31) | BIGINT |
| Float | FLOAT |
| Boolean | BIT |
| Datetime | DATETIME |
| String | NVARCHAR(MAX) |

## ⚙️ Tratamento de Erros

- **CSV mal formatados**: O script tenta múltiplas estratégias de leitura
- **Valores nulos**: Convertidos para `NULL` em SQL
- **Aspas simples**: Escapadas automaticamente (`'` → `''`)
- **Tabelas vazias**: Ignoradas durante a conversão

## 📂 Arquivos de Saída

Os arquivos SQL gerados:
- São divididos automaticamente ao atingir 2.2 MB
- Incluem comandos `DROP TABLE IF EXISTS` para recriação limpa
- Usam codificação UTF-8
- Contêm comentários identificando cada tabela

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novos recursos
- Enviar pull requests

## 📄 Licença

Este projeto é de código aberto e está disponível para uso livre.

## ✨ Autor

PedroVictorAndreoli

---

**Nota**: Sempre verifique os scripts SQL gerados antes de executá-los em ambientes de produção.
