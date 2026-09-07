from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from iceibank.core.config import Settings
from iceibank.core.exceptions import (
    ContaForaDaParticao,
    ContaJaExiste,
    ContaNaoEncontrada,
    SaldoInsuficiente,
)
from iceibank.models.conta import Conta
from iceibank.models.evento import Evento
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_lamport import LamportClock


class ContaService:
    def __init__(
        self,
        repository: ContaRepository,
        clock: LamportClock,
        logger: EventLogger,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.clock = clock
        self.logger = logger
        self.settings = settings

    def validar_particao(self, conta_id: int) -> None:
        responsavel = self.settings.agencia_responsavel(conta_id)
        if responsavel != self.settings.agencia_id:
            raise ContaForaDaParticao(conta_id, responsavel)

    def buscar(self, conta_id: int) -> Conta:
        self.validar_particao(conta_id)
        conta = self.repository.buscar(conta_id)
        if conta is None:
            raise ContaNaoEncontrada()
        return conta

    def criar(self, conta_id: int, nome_aluno: str, saldo_inicial: Decimal) -> Conta:
        self.validar_particao(conta_id)
        with self.repository.transacao():
            if self.repository.buscar(conta_id) is not None:
                raise ContaJaExiste()
            conta = self.repository.inserir(Conta(conta_id, nome_aluno, saldo_inicial))
            self._evento(
                "CRIAR_CONTA",
                {"id": conta.id, "nomeAluno": conta.nome_aluno, "saldoInicial": conta.saldo},
            )
            return conta

    def depositar(self, conta_id: int, valor: Decimal) -> Conta:
        self.validar_particao(conta_id)
        with self.repository.transacao():
            conta = self._buscar_existente(conta_id)
            conta.saldo += valor
            self.repository.atualizar(conta)
            self._evento("DEPOSITO", {"id": conta.id, "valor": valor, "novoSaldo": conta.saldo})
            return conta

    def sacar(self, conta_id: int, valor: Decimal) -> Conta:
        self.validar_particao(conta_id)
        with self.repository.transacao():
            conta = self._buscar_existente(conta_id)
            if conta.saldo < valor:
                raise SaldoInsuficiente()
            conta.saldo -= valor
            self.repository.atualizar(conta)
            self._evento("SAQUE", {"id": conta.id, "valor": valor, "novoSaldo": conta.saldo})
            return conta

    def _buscar_existente(self, conta_id: int) -> Conta:
        conta = self.repository.buscar(conta_id)
        if conta is None:
            raise ContaNaoEncontrada()
        return conta

    def _evento(self, tipo: str, detalhes: dict[str, object]) -> int:
        timestamp = self.clock.ao_enviar()
        self.logger.registrar(
            Evento(
                agencia=self.settings.nome_agencia,
                tipo=tipo,
                timestamp_lamport=timestamp,
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes=detalhes,
            )
        )
        return timestamp
