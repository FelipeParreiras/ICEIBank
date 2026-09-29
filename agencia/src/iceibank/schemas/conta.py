from decimal import Decimal

from pydantic import Field, field_validator

from iceibank.core.money import normalizar_dinheiro
from iceibank.schemas.base import ApiSchema


class CriarContaRequest(ApiSchema):
    id: int = Field(ge=0)
    nome_aluno: str = Field(alias="nomeAluno", min_length=1, max_length=120)
    saldo_inicial: Decimal = Field(default=Decimal("0.00"), alias="saldoInicial")

    @field_validator("nome_aluno")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome do aluno não pode ser vazio.")
        return valor

    @field_validator("saldo_inicial")
    @classmethod
    def validar_saldo(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor, permitir_zero=True)


class ValorRequest(ApiSchema):
    valor: Decimal

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)


class ContaResponse(ApiSchema):
    id: int
    nome_aluno: str = Field(alias="nomeAluno")
    saldo: Decimal
