from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class CategoriaGasto(StrEnum):
    MORADIA = "MORADIA"
    ALIMENTACAO = "ALIMENTACAO"
    TRANSPORTE = "TRANSPORTE"
    SAUDE = "SAUDE"
    EDUCACAO = "EDUCACAO"
    LAZER = "LAZER"
    DELIVERY = "DELIVERY"
    ASSINATURAS = "ASSINATURAS"
    COMPRAS = "COMPRAS"
    OUTROS = "OUTROS"


@dataclass(frozen=True, slots=True)
class Gasto:
    id: UUID
    conta_id: int
    descricao: str
    valor: Decimal
    categoria: CategoriaGasto
    data: date
    registrado_em: datetime

    @property
    def competencia(self) -> str:
        return self.data.strftime("%Y-%m")
