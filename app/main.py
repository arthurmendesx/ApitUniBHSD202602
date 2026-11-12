"""Ponto de entrada: cria o app FastAPI e registra as rotas."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import criar_tabelas
from app.routes.registro_routes import router as registro_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    criar_tabelas()  # substitui o @app.on_event("startup"), que está depreciado
    yield


app = FastAPI(
    title="API de Gerenciamento - Projeto A4 (Multicamadas)",
    description="FastAPI + SQLite organizada em camadas: rotas → serviço → repositório → banco.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(registro_router)
