from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from iceibank.core.money import normalizar_dinheiro
from iceibank.schemas.base import ApiSchema


class TransferenciaRequest(ApiSchema):
    id_origem: int = Field(alias="idOrigem", ge=0)
    id_destino: int = Field(alias="idDestino", ge=0)
    valor: Decimal

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)

    @model_validator(mode="after")
    def validar_contas(self) -> "TransferenciaRequest":
        if self.id_origem == self.id_destino:
            raise ValueError("As contas devem ser diferentes.")
        return self


class CreditoRemotoRequest(ApiSchema):
    valor: Decimal
    timestamp_lamport: int = Field(alias="timestampLamport", ge=0)
    origem_agencia: int = Field(alias="origemAgencia", ge=0, le=2)

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)


class MensagemTransferenciaResponse(ApiSchema):
    mensagem: str
    tipo: str | None = None


class CreditoRemotoResponse(ApiSchema):
    mensagem: str
    saldo_atual: Decimal = Field(alias="saldoAtual")
