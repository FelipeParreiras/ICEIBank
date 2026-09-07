from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from iceibank.models.gasto import CategoriaGasto, Gasto
from iceibank.models.planejamento_financeiro import PlanejamentoMensal
from iceibank.services.recomendacao_economia_service import (
    RecomendacaoEconomiaService,
)


def _gasto(categoria: CategoriaGasto, valor: str) -> Gasto:
    return Gasto(
        id=uuid4(),
        conta_id=6,
        descricao=categoria.value,
        valor=Decimal(valor),
        categoria=categoria,
        data=date(2026, 9, 1),
        registrado_em=datetime.now(UTC),
    )


def test_recomendacao_reproduz_exemplo_documentado() -> None:
    planejamento = PlanejamentoMensal(
        conta_id=6,
        competencia="2026-09",
        renda_prevista=Decimal("500.00"),
        meta_economia=Decimal("100.00"),
        limites_por_categoria={
            CategoriaGasto.ALIMENTACAO: Decimal("150.00"),
            CategoriaGasto.TRANSPORTE: Decimal("100.00"),
            CategoriaGasto.DELIVERY: Decimal("80.00"),
            CategoriaGasto.LAZER: Decimal("70.00"),
        },
        categorias_flexiveis=frozenset(
            {
                CategoriaGasto.DELIVERY,
                CategoriaGasto.LAZER,
                CategoriaGasto.COMPRAS,
                CategoriaGasto.ASSINATURAS,
            }
        ),
    )
    gastos = (
        _gasto(CategoriaGasto.ALIMENTACAO, "150.00"),
        _gasto(CategoriaGasto.TRANSPORTE, "80.00"),
        _gasto(CategoriaGasto.DELIVERY, "120.00"),
        _gasto(CategoriaGasto.LAZER, "100.00"),
    )

    recomendacoes, nao_coberto = RecomendacaoEconomiaService().gerar(
        planejamento, gastos, Decimal("50.00")
    )

    assert [(item.categoria, item.reducao_sugerida) for item in recomendacoes] == [
        (CategoriaGasto.DELIVERY, Decimal("40.00")),
        (CategoriaGasto.LAZER, Decimal("10.00")),
    ]
    assert nao_coberto == Decimal("0.00")
