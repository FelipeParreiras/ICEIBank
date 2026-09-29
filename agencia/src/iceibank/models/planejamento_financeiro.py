from dataclasses import dataclass, field
from decimal import Decimal

from iceibank.models.gasto import CategoriaGasto, Gasto


@dataclass(frozen=True, slots=True)
class PlanejamentoMensal:
    conta_id: int
    competencia: str
    renda_prevista: Decimal
    meta_economia: Decimal
    limites_por_categoria: dict[CategoriaGasto, Decimal] = field(default_factory=dict)
    categorias_flexiveis: frozenset[CategoriaGasto] = field(default_factory=frozenset)

    @property
    def limite_gasto_mensal(self) -> Decimal:
        return self.renda_prevista - self.meta_economia


@dataclass(frozen=True, slots=True)
class RecomendacaoEconomia:
    categoria: CategoriaGasto
    total_gasto: Decimal
    limite_configurado: Decimal | None
    reducao_sugerida: Decimal
    motivo: str


@dataclass(frozen=True, slots=True)
class ResumoFinanceiro:
    planejamento: PlanejamentoMensal
    total_gasto: Decimal
    economia_projetada: Decimal
    saldo_para_gastar: Decimal
    valor_ajuste: Decimal
    status: str
    totais_por_categoria: dict[CategoriaGasto, Decimal]
    recomendacoes: tuple[RecomendacaoEconomia, ...]
    valor_nao_coberto: Decimal
    gastos: tuple[Gasto, ...]
