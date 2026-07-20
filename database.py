import os
import sqlite3

DB_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "erp.db"))


def conectar():
    conexao = sqlite3.connect(DB_NAME)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                preco REAL NOT NULL CHECK (preco >= 0),
                quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT
            );

            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                data TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );
        """)

        conexao.commit()

    print("Banco de dados criado com sucesso!")


if __name__ == "__main__":
    criar_tabelas()
