import pandas as pd
import sqlite3
import unicodedata
import os

# Função para remover acentos e padronizar nomes
import re


def normalizar(texto):
    if pd.isna(texto):
        return "desconhecido"
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.strip().lower().replace(" ", "_").replace(".", "")
    texto = re.sub(r'\W+', '_', texto)  # Remove tudo que não for letra, número ou underscore
    return texto

# Caminho do arquivo CSV e nome do banco
csv_path = "Relatorio/relatorio.csv"
db_dir = "dados"
db_path = os.path.join(db_dir, "agenda_profissionais.db")

# Criar diretório se não existir
os.makedirs(db_dir, exist_ok=True)

# Leitura do CSV
df = pd.read_csv(csv_path, sep=';')

# Normalizar nomes das colunas
df.columns = [normalizar(col) for col in df.columns]

# Conectar ao banco SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabelas por profissional
for profissional in df["profissional"].unique():
    df_prof = df[df["profissional"] == profissional]

    # Nome da tabela limpo
    table_name = "agenda_" + normalizar(profissional)

    # Criar a tabela com as colunas atuais
    colunas = df_prof.columns
    colunas_def = ",\n    ".join([f"{col} TEXT" for col in colunas])
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {colunas_def}
    )
    """
    cursor.execute(create_table_sql)

    # Inserir os dados
    df_prof.to_sql(table_name, conn, if_exists='append', index=False)

# Finalizar
conn.commit()
conn.close()

print("Todas as tabelas foram criadas e preenchidas com sucesso.")
