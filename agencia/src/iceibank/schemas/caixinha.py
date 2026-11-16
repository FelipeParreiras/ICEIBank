from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from iceibank.core.money import normalizar_dinheiro
from iceibank.models.caixinha import CORES_CAIXINHA
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


class AtualizarCaixinhaRequest(ApiSchema):
    nome: str | None = Field(default=None, min_length=1, max_length=80)
    cor: str | None = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome da Caixinha não pode ser vazio.")
        return valor

    @field_validator("cor")
    @classmethod
    def validar_cor(cls, valor: str | None) -> str | None:
        if valor is not None and valor not in CORES_CAIXINHA:
            raise ValueError("Cor de Caixinha inválida.")
        return valor

    @model_validator(mode="after")
    def validar_alteracao(self):
        if self.nome is None and self.cor is None:
            raise ValueError("Informe um nome ou uma cor para atualizar a Caixinha.")
        return self


class MovimentoCaixinhaRequest(ApiSchema):
    valor: Decimal

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)


class ReordenarCaixinhasRequest(ApiSchema):
    caixinhas_ids: list[UUID] = Field(alias="caixinhasIds")


class LoteCaixinhaResponse(ApiSchema):
    id: UUID
    saldo: Decimal
    proximo_rendimento_em: datetime = Field(alias="proximoRendimentoEm")


class HistoricoCaixinhaResponse(ApiSchema):
    tipo: str
    valor: Decimal
    em: datetime


class CaixinhaResponse(ApiSchema):
    id: UUID
    conta_id: int = Field(alias="contaId")
    nome: str
    cor: str
    ordem: int
    saldo: Decimal
    rendimento_total: Decimal = Field(alias="rendimentoTotal")
    lotes: list[LoteCaixinhaResponse]
    movimentos: list[HistoricoCaixinhaResponse]


class MovimentoCaixinhaResponse(ApiSchema):
    caixinha: CaixinhaResponse
    saldo_conta: Decimal = Field(alias="saldoConta")


class ExcluirCaixinhaResponse(ApiSchema):
    mensagem: str
    saldo_conta: Decimal = Field(alias="saldoConta")
    valor_resgatado: Decimal = Field(alias="valorResgatado")
