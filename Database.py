import sqlite3

class UsuarioDB:
    def __init__(self, db_name='usuarios.db'):
        self.db_name = db_name
        self._criar_tabela()

    def _conectar(self):
        return sqlite3.connect(self.db_name)

    def _criar_tabela(self):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,  -- Adicionado o campo login
                nome TEXT NOT NULL,
                especialidade TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def adicionar_usuario(self, login, nome, especialidade, senha):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (login, nome, especialidade, senha)
                VALUES (?, ?, ?, ?)
            ''', (login, nome, especialidade, senha))
            conn.commit()
            print(f"Usuário '{nome}' adicionado com sucesso.")
        except sqlite3.IntegrityError:
            print(f"Erro: O login '{login}' já está em uso.")
        conn.close()

    def listar_usuarios(self):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id, login, nome, especialidade FROM usuarios')
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios

    def autenticar_usuario(self, nome, senha):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute(''' 
            SELECT * FROM usuarios WHERE nome = ? AND senha = ?
        ''', (nome, senha))
        usuario = cursor.fetchone()
        conn.close()
        return usuario is not None

# Exemplo de uso
if __name__ == "__main__":
    db = UsuarioDB()
    
    # Adicionar usuários (com login, nome, especialidade e senha)
    db.adicionar_usuario("wyller123", "WYLLER BRAULIO RESENDE SILVA", "terapia ocupacional", "1234")
    db.adicionar_usuario("maria456", "Maria Souza", "fisioterapia", "senha123")

    # Exemplo de listagem de usuários cadastrados
    print("\nUsuários cadastrados:")
    for usuario in db.listar_usuarios():
        print(usuario)

    # Exemplo de tentativa de autenticação
    print("\nTentando autenticar:")
    if db.autenticar_usuario("WYLLER BRAULIO RESENDE SILVA", "1234"):
        print("Autenticação bem-sucedida!")
    else:
        print("Falha na autenticação.")
