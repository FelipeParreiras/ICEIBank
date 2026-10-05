from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from iceibank.core.money import normalizar_dinheiro
from iceibank.schemas.base import ApiSchema


class CriarCaixinhaRequest(ApiSchema):
    nome: str = Field(min_length=1, max_length=80)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome da Caixinha não pode ser vazio.")
        return valor


class AtualizarCaixinhaRequest(CriarCaixinhaRequest):
    pass


class MovimentoCaixinhaRequest(ApiSchema):
    valor: Decimal

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)


class LoteCaixinhaResponse(ApiSchema):
    id: UUID
    saldo: Decimal
    proximo_rendimento_em: datetime = Field(alias="proximoRendimentoEm")


class CaixinhaResponse(ApiSchema):
    id: UUID
    conta_id: int = Field(alias="contaId")
    nome: str
    saldo: Decimal
    lotes: list[LoteCaixinhaResponse]


class MovimentoCaixinhaResponse(ApiSchema):
    caixinha: CaixinhaResponse
    saldo_conta: Decimal = Field(alias="saldoConta")
