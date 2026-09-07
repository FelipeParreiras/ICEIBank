from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from iceibank.core.exceptions import (
    PlanejamentoInvalido,
    PlanejamentoNaoEncontrado,
    SaldoInsuficiente,
)
from iceibank.models.evento import Evento
from iceibank.models.gasto import CategoriaGasto, Gasto
from iceibank.models.planejamento_financeiro import (
    PlanejamentoMensal,
    ResumoFinanceiro,
)
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.repositories.controle_financeiro_repository import (
    ControleFinanceiroRepository,
)
from iceibank.services.conta_service import ContaService
from iceibank.services.recomendacao_economia_service import (
    RecomendacaoEconomiaService,
)
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_lamport import LamportClock

ZERO = Decimal("0.00")


class ControleFinanceiroService:
    def __init__(
        self,
        repository: ControleFinanceiroRepository,
        conta_repository: ContaRepository,
        conta_service: ContaService,
        recomendacao_service: RecomendacaoEconomiaService,
        clock: LamportClock,
        logger: EventLogger,
    ) -> None:
        self.repository = repository
        self.conta_repository = conta_repository
        self.conta_service = conta_service
        self.recomendacao_service = recomendacao_service
        self.clock = clock
        self.logger = logger

    def definir_planejamento(
        self,
        conta_id: int,
        competencia: str,
        renda_prevista: Decimal,
        meta_economia: Decimal,
        limites_por_categoria: dict[CategoriaGasto, Decimal],
        categorias_flexiveis: set[CategoriaGasto],
    ) -> PlanejamentoMensal:
        self._validar_competencia(competencia)
        self.conta_service.buscar(conta_id)
        if meta_economia > renda_prevista:
            raise PlanejamentoInvalido("A meta não pode ser maior que a renda prevista.")
        limite_mensal = renda_prevista - meta_economia
        if sum(limites_por_categoria.values(), ZERO) > limite_mensal:
            raise PlanejamentoInvalido("A soma dos limites por categoria excede o limite mensal.")
        planejamento = PlanejamentoMensal(
            conta_id=conta_id,
            competencia=competencia,
            renda_prevista=renda_prevista,
            meta_economia=meta_economia,
            limites_por_categoria=dict(limites_por_categoria),
            categorias_flexiveis=frozenset(categorias_flexiveis),
        )
        with self.repository.transacao():
            self.repository.salvar_planejamento(planejamento)
            self._evento(
                "DEFINIR_PLANEJAMENTO_MENSAL",
                {
                    "contaId": conta_id,
                    "competencia": competencia,
                    "rendaPrevista": renda_prevista,
                    "metaEconomia": meta_economia,
                },
            )
        return planejamento

    def registrar_gasto(
        self,
        conta_id: int,
        descricao: str,
        valor: Decimal,
        categoria: CategoriaGasto,
        data_gasto: date,
    ) -> tuple[Gasto, Decimal]:
        competencia = data_gasto.strftime("%Y-%m")
        self.conta_service.validar_particao(conta_id)
        with self.repository.transacao():
            planejamento = self.repository.buscar_planejamento(conta_id, competencia)
            if planejamento is None:
                raise PlanejamentoNaoEncontrado()
            conta = self.conta_repository.buscar(conta_id)
            if conta is None:
                self.conta_service.buscar(conta_id)
                raise AssertionError("Conta deveria existir")
            if conta.saldo < valor:
                raise SaldoInsuficiente()
            gasto = Gasto(
                id=uuid4(),
                conta_id=conta_id,
                descricao=descricao,
                valor=valor,
                categoria=categoria,
                data=data_gasto,
                registrado_em=datetime.now(UTC),
            )
            conta.saldo -= valor
            self.conta_repository.atualizar(conta)
            self.repository.inserir_gasto(gasto)
            self._evento(
                "REGISTRAR_GASTO",
                {
                    "gastoId": gasto.id,
                    "contaId": conta_id,
                    "competencia": competencia,
                    "categoria": categoria,
                    "valor": valor,
                    "novoSaldo": conta.saldo,
                },
            )
            return gasto, conta.saldo

    def obter_resumo(self, conta_id: int, competencia: str) -> ResumoFinanceiro:
        self._validar_competencia(competencia)
        self.conta_service.buscar(conta_id)
        planejamento = self.repository.buscar_planejamento(conta_id, competencia)
        if planejamento is None:
            raise PlanejamentoNaoEncontrado()
        gastos = self.repository.listar_gastos(conta_id, competencia)
        totais: dict[CategoriaGasto, Decimal] = {}
        for gasto in gastos:
            totais[gasto.categoria] = totais.get(gasto.categoria, ZERO) + gasto.valor
        total_gasto = sum(totais.values(), ZERO)
        economia_projetada = planejamento.renda_prevista - total_gasto
        saldo_para_gastar = max(ZERO, planejamento.limite_gasto_mensal - total_gasto)
        valor_ajuste = max(ZERO, planejamento.meta_economia - economia_projetada)
        if total_gasto > planejamento.renda_prevista:
            status = "RENDA_EXCEDIDA"
        elif valor_ajuste > ZERO:
            status = "AJUSTE_NECESSARIO"
        else:
            status = "META_ATINGIVEL"
        recomendacoes, valor_nao_coberto = self.recomendacao_service.gerar(
            planejamento, gastos, valor_ajuste
        )
        return ResumoFinanceiro(
            planejamento=planejamento,
            total_gasto=total_gasto,
            economia_projetada=economia_projetada,
            saldo_para_gastar=saldo_para_gastar,
            valor_ajuste=valor_ajuste,
            status=status,
            totais_por_categoria=totais,
            recomendacoes=recomendacoes,
            valor_nao_coberto=valor_nao_coberto,
            gastos=gastos,
        )

    @staticmethod
    def _validar_competencia(competencia: str) -> None:
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", competencia):
            raise PlanejamentoInvalido("Competência deve seguir o formato AAAA-MM.")

    def _evento(self, tipo: str, detalhes: dict[str, object]) -> None:
        self.logger.registrar(
            Evento(
                agencia=self.conta_service.settings.nome_agencia,
                tipo=tipo,
                timestamp_lamport=self.clock.ao_enviar(),
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes=detalhes,
            )
        )
