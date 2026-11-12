"""Camada de apresentação: rotas HTTP. Só recebe a requisição e delega ao serviço."""
import sqlite3

from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.models.registro import RegistroCreate, RegistroResponse
from app.repositories.registro_repository import RegistroRepository
from app.services.registro_service import RegistroService

router = APIRouter(prefix="/registros", tags=["Registros"])


def get_service(conn: sqlite3.Connection = Depends(get_db)) -> RegistroService:
    return RegistroService(RegistroRepository(conn))


@router.post("", response_model=RegistroResponse, status_code=201)
def criar_registro(registro: RegistroCreate, service: RegistroService = Depends(get_service)):
    return service.criar(registro)


@router.get("", response_model=list[RegistroResponse])
def listar_registros(service: RegistroService = Depends(get_service)):
    return service.listar()


@router.get("/{registro_id}", response_model=RegistroResponse)
def buscar_registro(registro_id: int, service: RegistroService = Depends(get_service)):
    return service.buscar(registro_id)


@router.put("/{registro_id}", response_model=RegistroResponse)
def atualizar_registro(registro_id: int, registro: RegistroCreate,
                       service: RegistroService = Depends(get_service)):
    return service.atualizar(registro_id, registro)


@router.delete("/{registro_id}")
def deletar_registro(registro_id: int, service: RegistroService = Depends(get_service)):
    return service.deletar(registro_id)
