from __future__ import annotations

from decimal import Decimal

from iceibank.models.gasto import Gasto
from iceibank.models.planejamento_financeiro import (
    PlanejamentoMensal,
    RecomendacaoEconomia,
)

ZERO = Decimal("0.00")


class RecomendacaoEconomiaService:
    def gerar(
        self,
        planejamento: PlanejamentoMensal,
        gastos: tuple[Gasto, ...],
        valor_ajuste: Decimal,
    ) -> tuple[tuple[RecomendacaoEconomia, ...], Decimal]:
        if valor_ajuste <= ZERO:
            return (), ZERO

        totais = self._totais(gastos)
        recomendados: dict[str, Decimal] = {}
        motivos: dict[str, str] = {}
        restante = valor_ajuste
        prioridades = {
            categoria: indice
            for indice, categoria in enumerate(planejamento.categorias_ordenadas)
        }

        excessos: list[tuple[str, Decimal]] = []
        for categoria in planejamento.categorias_flexiveis:
            limite = planejamento.limites_por_categoria.get(categoria)
            if limite is None:
                continue
            excesso = max(ZERO, totais.get(categoria, ZERO) - limite)
            if excesso > ZERO:
                excessos.append((categoria, excesso))

        for categoria, excesso in sorted(
            excessos,
            key=lambda item: (
                -item[1],
                -prioridades.get(str(item[0]), -1),
                str(item[0]),
            ),
        ):
            reducao = min(excesso, restante)
            recomendados[categoria] = reducao
            motivos[categoria] = "ACIMA_DO_LIMITE"
            restante -= reducao
            if restante <= ZERO:
                break

        if restante > ZERO:
            flexiveis = sorted(
                planejamento.categorias_flexiveis,
                key=lambda categoria: (
                    -totais.get(categoria, ZERO),
                    -prioridades.get(str(categoria), -1),
                    str(categoria),
                ),
            )
            for categoria in flexiveis:
                total = totais.get(categoria, ZERO)
                ja_recomendado = recomendados.get(categoria, ZERO)
                capacidade = max(ZERO, (total * Decimal("0.20")) - ja_recomendado)
                reducao = min(capacidade, restante)
                if reducao <= ZERO:
                    continue
                recomendados[categoria] = ja_recomendado + reducao
                motivos.setdefault(categoria, "MAIOR_GASTO_FLEXIVEL")
                restante -= reducao
                if restante <= ZERO:
                    break

        recomendacoes = tuple(
            RecomendacaoEconomia(
                categoria=categoria,
                total_gasto=totais.get(categoria, ZERO),
                limite_configurado=planejamento.limites_por_categoria.get(categoria),
                reducao_sugerida=reducao.quantize(Decimal("0.01")),
                motivo=motivos[categoria],
            )
            for categoria, reducao in recomendados.items()
        )
        return recomendacoes, max(ZERO, restante).quantize(Decimal("0.01"))

    @staticmethod
    def _totais(gastos: tuple[Gasto, ...]) -> dict[str, Decimal]:
        totais: dict[str, Decimal] = {}
        for gasto in gastos:
            totais[gasto.categoria] = totais.get(gasto.categoria, ZERO) + gasto.valor
        return totais
