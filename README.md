# ExportaTabelaParaSQL

Ferramentas Python para conversão de arquivos CSV e JSON em scripts SQL compatíveis com SQL Server.

## 📋 Descrição

Este projeto contém scripts que automatizam a conversão de dados estruturados (CSV e JSON) em arquivos SQL com comandos `CREATE TABLE` e `INSERT INTO`, prontos para serem executados em bancos de dados SQL Server. Inclui também utilitários para pré-processamento de arquivos CSV.

## 🚀 Funcionalidades

### `main.py` - Conversor de CSV para SQL
- Converte arquivos CSV para scripts SQL
- Detecta automaticamente tipos de dados (INT, BIGINT, FLOAT, BIT, DATETIME, NVARCHAR)
- Lida com diferentes formatos de CSV (delimitadores, aspas, escape characters)
- Divide arquivos SQL em múltiplos arquivos quando ultrapassam 3 MB
- Trata valores nulos e caracteres especiais
- Remove automaticamente colunas vazias
- Renomeia colunas sem nome automaticamente
- Organiza comandos SQL: todos os CREATE TABLE primeiro, depois todos os INSERT
- Gera script mestre `EXECUTAR_TODOS.sql` para facilitar execução no SSMS
- Interface com feedback visual detalhado do processamento

### `jsons.py` - Conversor de JSON para SQL

- Converte arquivos JSON para scripts SQL
- Suporta estruturas JSON complexas (objetos aninhados e arrays)
- Cria tabelas relacionadas automaticamente para dados hierárquicos
- Gera chaves primárias e estrangeiras
- Divide arquivos SQL em múltiplos arquivos quando ultrapassam 2.2 MB
- Trunca valores muito grandes automaticamente

### Utilitários CSV (pasta `Util/`)

#### `converteCSV_para_urf8.py` - Conversor de Encoding
- Detecta automaticamente o encoding de arquivos CSV
- Converte arquivos CSV para UTF-8
- Usa detecção inteligente com a biblioteca `chardet`
- Gera arquivos com sufixo `_utf8.csv`

#### `limpa_null.py` - Limpeza de Valores NULL
- Remove strings "NULL" de arquivos CSV
- Substitui valores "NULL" por campos vazios
- Útil para limpeza de dados antes da conversão SQL
- Gera arquivos com sufixo `_limpo.csv`

## 📦 Requisitos

### Instalação Rápida

```bash
pip install -r requirements.txt
```

### Pacotes Necessários

- `pandas>=2.0.0` - Manipulação de dados CSV
- `python-dotenv>=1.0.0` - Gerenciamento de variáveis de ambiente
- `chardet>=5.0.0` - Detecção de encoding de arquivos

## 🔧 Configuração

### Arquivo .env

O projeto usa variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configurações do main.py - Conversor de CSV para SQL
CSV_PASTA=D:\aaaaaa\BKP ANDIARA MATRIZ
CSV_LIMITE_BYTES=3145728

# Configurações do jsons.py - Conversor de JSON para SQL
JSON_INPUT_FOLDER=C:/Users/Meu Computador/Documents/backup(1)
JSON_OUTPUT_BASE=output
JSON_LIMITE_TAMANHO=2306867

# Configurações dos Utilitários CSV
UTIL_PASTA=D:\
```


### Variáveis de Ambiente Disponíveis

#### main.py

- `CSV_PASTA`: Caminho da pasta com arquivos CSV (padrão: `D:\aaaaaa\BKP ANDIARA MATRIZ`)
- `CSV_LIMITE_BYTES`: Tamanho máximo por arquivo SQL em bytes (padrão: `3145728` = 3 MB)

#### jsons.py

- `JSON_INPUT_FOLDER`: Pasta com arquivos JSON (padrão: `C:/Users/Meu Computador/Documents/backup(1)`)
- `JSON_OUTPUT_BASE`: Nome base dos arquivos de saída (padrão: `output`)
- `JSON_LIMITE_TAMANHO`: Tamanho máximo por arquivo SQL em bytes (padrão: `2306867` ≈ 2.2 MB)

#### Utilitários CSV

- `UTIL_PASTA`: Pasta com arquivos CSV para processamento (padrão: `D:\`)

### Configuração Manual (Alternativa)

Se preferir não usar o arquivo `.env`, você pode editar diretamente as variáveis nos arquivos Python:

#### main.py
```python
pasta = r"D:\aaaaaa\BKP ANDIARA MATRIZ"  # Pasta com arquivos CSV
LIMITE_BYTES = 3 * 1024 * 1024  # Tamanho máximo por arquivo SQL (3 MB)
```

#### jsons.py

```python
INPUT_FOLDER = "C:/Users/Meu Computador/Documents/backup(1)"  # Pasta com arquivos JSON
OUTPUT_BASE = "output"  # Nome base dos arquivos de saída
LIMITE_TAMANHO = int(2.20 * 1024 * 1024)  # Tamanho máximo por arquivo SQL (2.2 MB)
```

#### Utilitários CSV (converteCSV_para_urf8.py e limpa_null.py)

```python
pasta = r"D:\"  # Pasta com arquivos CSV
```

## 💻 Uso

### Convertendo arquivos CSV

```bash
python main.py
```

```bash
python main.py
```

O script irá:
1. Ler todos os arquivos `.csv` da pasta configurada
2. Gerar arquivos `backup_parte_001.sql`, `backup_parte_002.sql`, etc.
3. Criar um arquivo mestre `EXECUTAR_TODOS.sql` para facilitar a execução
4. Todos os CREATE TABLE são gerados primeiro, seguidos pelos INSERT INTO
5. Exibir feedback detalhado do processamento no console

### Convertendo arquivos JSON:

```bash
python jsons.py
```

O script irá:
1. Ler todos os arquivos `.json` da pasta configurada
2. Gerar arquivos `output_1.sql`, `output_2.sql`, etc.
3. Criar tabelas relacionadas para estruturas hierárquicas

### Pré-processando arquivos CSV:

#### Convertendo para UTF-8:
```bash
cd Util
python converteCSV_para_urf8.py
```

O script irá:
1. Detectar automaticamente o encoding de cada arquivo CSV
2. Converter para UTF-8
3. Gerar arquivos com sufixo `_utf8.csv`

#### Limpando valores NULL:
```bash
cd Util
python limpa_null.py
```

O script irá:
1. Ler todos os arquivos CSV da pasta configurada
2. Substituir strings "NULL" por campos vazios
3. Gerar arquivos com sufixo `_limpo.csv`

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

## ⚙️ Tratamento de Erros e Recursos Especiais

### main.py
- **CSV mal formatados**: Tenta múltiplas estratégias de leitura (csv.Sniffer, leitura manual)
- **Valores nulos ou vazios**: Convertidos para `NULL` em SQL
- **Aspas simples**: Escapadas automaticamente (`'` → `''`)
- **Tabelas vazias**: Ignoradas durante a conversão
- **Colunas vazias**: Removidas automaticamente
- **Colunas sem nome**: Renomeadas automaticamente para `Coluna_1`, `Coluna_2`, etc.
- **Caracteres especiais em nomes**: Colchetes `[]` removidos, espaços substituídos por underscore
- **Feedback visual**: Mostra progresso com ícones (✓, ❌, ⚠) e contadores detalhados

### jsons.py
- **Valores nulos**: Convertidos para `NULL` em SQL
- **Aspas simples**: Escapadas automaticamente
- **Valores muito grandes**: Truncados automaticamente

## 📂 Arquivos de Saída

### main.py
Os arquivos SQL gerados:
- **`backup_parte_001.sql`, `backup_parte_002.sql`, etc.**: Arquivos divididos automaticamente ao atingir 3 MB
- **`EXECUTAR_TODOS.sql`**: Script mestre que executa todos os arquivos de backup em ordem
- Incluem comandos `DROP TABLE IF EXISTS` para recriação limpa
- Usam codificação UTF-8
- Contêm comentários identificando cada tabela
- Organização: todos os CREATE TABLE primeiro, depois todos os INSERT INTO

### Como Executar no SQL Server:
1. Abra o SQL Server Management Studio (SSMS)
2. Edite o arquivo `EXECUTAR_TODOS.sql`
3. Altere `SeuBancoDeDados` para o nome correto do banco
4. Ative o modo SQLCMD: **Query > SQLCMD Mode**
5. Execute o script (F5)

### jsons.py
Os arquivos SQL gerados:
- São divididos automaticamente ao atingir 2.2 MB
- Criam tabelas relacionadas para estruturas hierárquicas
- Geram chaves primárias e estrangeiras automaticamente

## 🔄 Fluxo de Trabalho Recomendado

Para melhor resultado na conversão de arquivos CSV para SQL, siga esta ordem:

1. **Configuração Inicial**:
   - Copie `.env.example` para `.env`
   - Configure as variáveis de ambiente com seus caminhos
   - Instale as dependências: `pip install -r requirements.txt`

2. **Pré-processamento (Opcional, mas recomendado)**:
   - Use `converteCSV_para_urf8.py` para padronizar encoding
   - Use `limpa_null.py` para limpar valores NULL indesejados

3. **Conversão para SQL**:
   - Execute `main.py` para gerar os scripts SQL
   - Verifique os arquivos gerados (`backup_parte_001.sql`, etc.)

4. **Execução no Banco de Dados**:
   - Edite `EXECUTAR_TODOS.sql` com o nome do banco correto
   - Execute no SSMS com modo SQLCMD ativado

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
