"""Camada de acesso a dados: apenas SQL, sem regra de negócio."""
import sqlite3

from app.models.registro import RegistroCreate


class RegistroRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def listar(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM registros").fetchall()
        return [dict(r) for r in rows]

    def buscar_por_id(self, registro_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM registros WHERE id = ?", (registro_id,)
        ).fetchone()
        return dict(row) if row else None

    def criar(self, dados: RegistroCreate) -> int:
        cur = self.conn.execute(
            "INSERT INTO registros (titulo, descricao, ativo) VALUES (?, ?, ?)",
            (dados.titulo, dados.descricao, dados.ativo),
        )
        self.conn.commit()
        return cur.lastrowid

    def atualizar(self, registro_id: int, dados: RegistroCreate) -> None:
        self.conn.execute(
            "UPDATE registros SET titulo = ?, descricao = ?, ativo = ? WHERE id = ?",
            (dados.titulo, dados.descricao, dados.ativo, registro_id),
        )
        self.conn.commit()

    def deletar(self, registro_id: int) -> None:
        self.conn.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
        self.conn.commit()
