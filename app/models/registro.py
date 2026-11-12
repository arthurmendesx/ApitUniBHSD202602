"""Camada de modelos: contratos de entrada/saída (Pydantic)."""
from pydantic import BaseModel


class RegistroBase(BaseModel):
    titulo: str
    descricao: str | None = None
    ativo: bool = True


class RegistroCreate(RegistroBase):
    pass


class RegistroResponse(RegistroBase):
    id: int
