import sqlite3
import pandas as pd

class BancoDeDados:
    def __init__(self, db_path):
        self.db_path = db_path

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabela(self):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                especialidade TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def adicionar_usuario(self, login, nome, especialidade, senha="1234"):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (login, nome, especialidade, senha)
                VALUES (?, ?, ?, ?)
            ''', (login, nome, especialidade, senha))
            conn.commit()
        except sqlite3.IntegrityError:
            # If there's a UNIQUE constraint violation, skip the insertion
            print(f"Usuário {login} já existe. Ignorando a duplicação.")
        finally:
            conn.close()

    def ler_profissionais(self, agenda_db_path):
        conn = sqlite3.connect(agenda_db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        profissionais = []
        for table in tables:
            table_name = table[0]
            if "agenda" in table_name:  # Filter for the agenda tables
                query = f"SELECT profissional, especialidade FROM {table_name}"
                cursor.execute(query)
                dados = cursor.fetchall()
                for row in dados:
                    profissional = row[0]
                    especialidade = row[1]
                    login = profissional.split()[0]  # Use the first name as the login
                    profissionais.append((login, profissional, especialidade))
        conn.close()
        return profissionais

    def transferir_profissionais(self, agenda_db_path):
        profissionais = self.ler_profissionais(agenda_db_path)
        for login, nome, especialidade in profissionais:
            self.adicionar_usuario(login, nome, especialidade)

# Usage example:
# Create a new database and transfer data from the existing one
novo_db = BancoDeDados('novo_banco.db')  # Path for the new database
novo_db._criar_tabela()  # Create the 'usuarios' table

# Transfer data from the agenda professionals database
novo_db.transferir_profissionais('data/agenda_profissionais.db')  # Use the path for your database
