"""Camada de serviço: regras de negócio e validações."""
from fastapi import HTTPException

from app.models.registro import RegistroCreate
from app.repositories.registro_repository import RegistroRepository


class RegistroService:
    def __init__(self, repo: RegistroRepository):
        self.repo = repo

    @staticmethod
    def _validar(dados: RegistroCreate) -> None:
        if not dados.titulo.strip():
            raise HTTPException(status_code=400, detail="O título não pode estar em branco.")

    def _obter_ou_404(self, registro_id: int) -> dict:
        registro = self.repo.buscar_por_id(registro_id)
        if registro is None:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        return registro

    def listar(self) -> list[dict]:
        return self.repo.listar()

    def buscar(self, registro_id: int) -> dict:
        return self._obter_ou_404(registro_id)

    def criar(self, dados: RegistroCreate) -> dict:
        self._validar(dados)
        try:
            novo_id = self.repo.criar(dados)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno no banco de dados: {e}")
        return {**dados.model_dump(), "id": novo_id}

    def atualizar(self, registro_id: int, dados: RegistroCreate) -> dict:
        self._validar(dados)
        self._obter_ou_404(registro_id)
        try:
            self.repo.atualizar(registro_id, dados)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
        return {**dados.model_dump(), "id": registro_id}

    def deletar(self, registro_id: int) -> dict:
        self._obter_ou_404(registro_id)
        self.repo.deletar(registro_id)
        return {"mensagem": "Registro removido com sucesso."}
