from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from iceibank.core.money import normalizar_dinheiro
from iceibank.models.gasto import CategoriaGasto
from iceibank.schemas.base import ApiSchema


class PlanejamentoMensalRequest(ApiSchema):
    renda_prevista: Decimal = Field(alias="rendaPrevista")
    meta_economia: Decimal = Field(alias="metaEconomia")
    limites_por_categoria: dict[CategoriaGasto, Decimal] = Field(
        default_factory=dict, alias="limitesPorCategoria"
    )
    categorias_flexiveis: set[CategoriaGasto] = Field(
        default_factory=set, alias="categoriasFlexiveis"
    )

    @field_validator("renda_prevista")
    @classmethod
    def validar_renda(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)

    @field_validator("meta_economia")
    @classmethod
    def validar_meta(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor, permitir_zero=True)

    @field_validator("limites_por_categoria")
    @classmethod
    def validar_limites(
        cls, valores: dict[CategoriaGasto, Decimal]
    ) -> dict[CategoriaGasto, Decimal]:
        return {
            categoria: normalizar_dinheiro(valor, permitir_zero=True)
            for categoria, valor in valores.items()
        }

    @model_validator(mode="after")
    def validar_planejamento(self) -> "PlanejamentoMensalRequest":
        if self.meta_economia > self.renda_prevista:
            raise ValueError("A meta não pode ser maior que a renda prevista.")
        limite = self.renda_prevista - self.meta_economia
        if sum(self.limites_por_categoria.values(), Decimal("0.00")) > limite:
            raise ValueError("A soma dos limites por categoria excede o limite mensal.")
        return self


class PlanejamentoMensalResponse(ApiSchema):
    conta_id: int = Field(alias="contaId")
    competencia: str
    renda_prevista: Decimal = Field(alias="rendaPrevista")
    meta_economia: Decimal = Field(alias="metaEconomia")
    limite_gasto_mensal: Decimal = Field(alias="limiteGastoMensal")
    limites_por_categoria: dict[CategoriaGasto, Decimal] = Field(alias="limitesPorCategoria")
    categorias_flexiveis: set[CategoriaGasto] = Field(alias="categoriasFlexiveis")


class RegistrarGastoRequest(ApiSchema):
    descricao: str = Field(min_length=1, max_length=200)
    valor: Decimal
    categoria: CategoriaGasto
    data: date

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("A descrição não pode ser vazia.")
        return valor

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, valor: Decimal) -> Decimal:
        return normalizar_dinheiro(valor)


class GastoResponse(ApiSchema):
    id: UUID
    conta_id: int = Field(alias="contaId")
    descricao: str
    valor: Decimal
    categoria: CategoriaGasto
    data: date
    competencia: str
    registrado_em: datetime = Field(alias="registradoEm")


class RegistrarGastoResponse(ApiSchema):
    gasto: GastoResponse
    saldo_conta: Decimal = Field(alias="saldoConta")


class RecomendacaoResponse(ApiSchema):
    categoria: CategoriaGasto
    total_gasto: Decimal = Field(alias="totalGasto")
    limite_configurado: Decimal | None = Field(alias="limiteConfigurado")
    reducao_sugerida: Decimal = Field(alias="reducaoSugerida")
    motivo: str


class ResumoFinanceiroResponse(ApiSchema):
    conta_id: int = Field(alias="contaId")
    competencia: str
    renda_prevista: Decimal = Field(alias="rendaPrevista")
    meta_economia: Decimal = Field(alias="metaEconomia")
    limite_gasto_mensal: Decimal = Field(alias="limiteGastoMensal")
    total_gasto: Decimal = Field(alias="totalGasto")
    economia_projetada: Decimal = Field(alias="economiaProjetada")
    saldo_para_gastar: Decimal = Field(alias="saldoParaGastar")
    valor_ajuste: Decimal = Field(alias="valorAjuste")
    status: str
    totais_por_categoria: dict[CategoriaGasto, Decimal] = Field(alias="totaisPorCategoria")
    recomendacoes: list[RecomendacaoResponse]
    valor_nao_coberto: Decimal = Field(alias="valorNaoCoberto")
    gastos: list[GastoResponse]
