"""Camada de infraestrutura: conexão e criação das tabelas do SQLite."""
import sqlite3
from collections.abc import Iterator

DB_PATH = "banco_a3.db"


def conectar_banco() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # acesso às colunas por nome
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependência do FastAPI: abre a conexão e garante o fechamento."""
    conn = conectar_banco()
    try:
        yield conn
    finally:
        conn.close()


def criar_tabelas() -> None:
    with conectar_banco() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                ativo BOOLEAN DEFAULT TRUE
            )
            """
        )
