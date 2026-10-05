from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from iceibank.core.config import Settings
from iceibank.core.exceptions import (
    CaixinhaComSaldo,
    CaixinhaInvalida,
    CaixinhaNaoEncontrada,
    ContaNaoEncontrada,
    SaldoInsuficiente,
)
from iceibank.models.caixinha import Caixinha, LoteCaixinha
from iceibank.models.evento import Evento
from iceibank.repositories.caixinha_repository import CaixinhaRepository
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.services.conta_service import ContaService
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_vetorial import RelogioVetorial

PERIODO_RENDIMENTO = timedelta(hours=48)
TAXA_RENDIMENTO = Decimal("1.10")
CENTAVOS = Decimal("0.01")


class CaixinhaService:
    def __init__(
        self,
        repository: CaixinhaRepository,
        conta_repository: ContaRepository,
        conta_service: ContaService,
        clock: RelogioVetorial,
        logger: EventLogger,
        settings: Settings,
        agora: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.conta_repository = conta_repository
        self.conta_service = conta_service
        self.clock = clock
        self.logger = logger
        self.settings = settings
        self.agora = agora or (lambda: datetime.now(UTC))

    def criar(self, conta_id: int, nome: str) -> Caixinha:
        self._validar_conta(conta_id)
        with self.repository.transacao():
            if any(
                item.nome.casefold() == nome.casefold()
                for item in self.repository.listar_por_conta(conta_id)
            ):
                raise CaixinhaInvalida("Já existe uma Caixinha com este nome nesta conta.")
            caixinha = self.repository.inserir(Caixinha(conta_id=conta_id, nome=nome))
            self._evento(
                "CRIAR_CAIXINHA", {"contaId": conta_id, "caixinhaId": caixinha.id, "nome": nome}
            )
            return caixinha

    def listar(self, conta_id: int) -> tuple[Caixinha, ...]:
        self._validar_conta(conta_id)
        with self.repository.transacao():
            caixinhas = self.repository.listar_por_conta(conta_id)
            return tuple(self._atualizar_rendimento(item) for item in caixinhas)

    def buscar(self, conta_id: int, caixinha_id: UUID) -> Caixinha:
        self._validar_conta(conta_id)
        with self.repository.transacao():
            return self._atualizar_rendimento(self._buscar_da_conta(conta_id, caixinha_id))

    def renomear(self, conta_id: int, caixinha_id: UUID, nome: str) -> Caixinha:
        self._validar_conta(conta_id)
        with self.repository.transacao():
            caixinha = self._buscar_da_conta(conta_id, caixinha_id)
            if any(
                item.id != caixinha_id and item.nome.casefold() == nome.casefold()
                for item in self.repository.listar_por_conta(conta_id)
            ):
                raise CaixinhaInvalida("Já existe uma Caixinha com este nome nesta conta.")
            caixinha.nome = nome
            caixinha = self.repository.atualizar(caixinha)
            self._evento(
                "RENOMEAR_CAIXINHA", {"contaId": conta_id, "caixinhaId": caixinha.id, "nome": nome}
            )
            return caixinha

    def excluir(self, conta_id: int, caixinha_id: UUID) -> None:
        self._validar_conta(conta_id)
        with self.repository.transacao():
            caixinha = self._atualizar_rendimento(self._buscar_da_conta(conta_id, caixinha_id))
            if caixinha.saldo > 0:
                raise CaixinhaComSaldo()
            self.repository.remover(caixinha_id)
            self._evento("EXCLUIR_CAIXINHA", {"contaId": conta_id, "caixinhaId": caixinha_id})

    def guardar(self, conta_id: int, caixinha_id: UUID, valor: Decimal) -> tuple[Caixinha, Decimal]:
        self._validar_conta(conta_id)
        with self.repository.transacao(), self.conta_repository.transacao():
            caixinha = self._atualizar_rendimento(self._buscar_da_conta(conta_id, caixinha_id))
            conta = self._conta_existente(conta_id)
            if conta.saldo < valor:
                raise SaldoInsuficiente()
            conta.saldo -= valor
            caixinha.lotes.append(
                LoteCaixinha(saldo=valor, proximo_rendimento_em=self.agora() + PERIODO_RENDIMENTO)
            )
            caixinha = self.repository.atualizar(caixinha)
            conta = self.conta_repository.atualizar(conta)
            self._evento(
                "GUARDAR_CAIXINHA",
                {
                    "contaId": conta_id,
                    "caixinhaId": caixinha.id,
                    "valor": valor,
                    "saldoConta": conta.saldo,
                },
            )
            return caixinha, conta.saldo

    def resgatar(
        self, conta_id: int, caixinha_id: UUID, valor: Decimal
    ) -> tuple[Caixinha, Decimal]:
        self._validar_conta(conta_id)
        with self.repository.transacao(), self.conta_repository.transacao():
            caixinha = self._atualizar_rendimento(self._buscar_da_conta(conta_id, caixinha_id))
            if caixinha.saldo < valor:
                raise SaldoInsuficiente()
            restante = valor
            lotes_restantes: list[LoteCaixinha] = []
            for lote in caixinha.lotes:
                consumido = min(lote.saldo, restante)
                lote.saldo -= consumido
                restante -= consumido
                if lote.saldo > 0:
                    lotes_restantes.append(lote)
            caixinha.lotes = lotes_restantes
            conta = self._conta_existente(conta_id)
            conta.saldo += valor
            caixinha = self.repository.atualizar(caixinha)
            conta = self.conta_repository.atualizar(conta)
            self._evento(
                "RESGATAR_CAIXINHA",
                {
                    "contaId": conta_id,
                    "caixinhaId": caixinha.id,
                    "valor": valor,
                    "saldoConta": conta.saldo,
                },
            )
            return caixinha, conta.saldo

    def _atualizar_rendimento(self, caixinha: Caixinha) -> Caixinha:
        agora = self.agora()
        rendimento = Decimal("0.00")
        for lote in caixinha.lotes:
            while agora >= lote.proximo_rendimento_em:
                anterior = lote.saldo
                lote.saldo = (lote.saldo * TAXA_RENDIMENTO).quantize(
                    CENTAVOS, rounding=ROUND_HALF_UP
                )
                rendimento += lote.saldo - anterior
                lote.proximo_rendimento_em += PERIODO_RENDIMENTO
        if rendimento:
            caixinha = self.repository.atualizar(caixinha)
            self._evento(
                "RENDIMENTO_CAIXINHA",
                {
                    "contaId": caixinha.conta_id,
                    "caixinhaId": caixinha.id,
                    "rendimento": rendimento,
                    "saldoCaixinha": caixinha.saldo,
                },
            )
        return caixinha

    def _buscar_da_conta(self, conta_id: int, caixinha_id: UUID) -> Caixinha:
        caixinha = self.repository.buscar(caixinha_id)
        if caixinha is None or caixinha.conta_id != conta_id:
            raise CaixinhaNaoEncontrada()
        return caixinha

    def _validar_conta(self, conta_id: int) -> None:
        self.conta_service.validar_particao(conta_id)
        self._conta_existente(conta_id)

    def _conta_existente(self, conta_id: int):
        conta = self.conta_repository.buscar(conta_id)
        if conta is None:
            raise ContaNaoEncontrada()
        return conta

    def _evento(self, tipo: str, detalhes: dict[str, object]) -> None:
        self.logger.registrar(
            Evento(
                agencia=self.settings.nome_agencia,
                tipo=tipo,
                timestamp_vetorial=self.clock.evento_local(),
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes=detalhes,
            )
        )
