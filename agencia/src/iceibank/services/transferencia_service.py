from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Protocol

from iceibank.core.config import Settings
from iceibank.core.exceptions import ContaNaoEncontrada, ContasIguais, SaldoInsuficiente
from iceibank.models.conta import Conta
from iceibank.models.evento import Evento
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.services.conta_service import ContaService
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_vetorial import RelogioVetorial


class PublicadorCredito(Protocol):
    def publicar_credito(self, agencia_destino: int, mensagem: dict[str, object]) -> None: ...


class TransferenciaService:
    def __init__(
        self,
        repository: ContaRepository,
        conta_service: ContaService,
        publicador: PublicadorCredito,
        clock: RelogioVetorial,
        logger: EventLogger,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.conta_service = conta_service
        self.publicador = publicador
        self.clock = clock
        self.logger = logger
        self.settings = settings

    def transferir(self, id_origem: int, id_destino: int, valor: Decimal) -> str:
        if id_origem == id_destino:
            raise ContasIguais()
        self.conta_service.validar_particao(id_origem)
        agencia_destino = self.settings.agencia_responsavel(id_destino)
        if agencia_destino == self.settings.agencia_id:
            self._transferir_local(id_origem, id_destino, valor)
            return "LOCAL"
        self._transferir_remota(id_origem, id_destino, agencia_destino, valor)
        return "REMOTA_PUBLICADA"

    def processar_credito_remoto(self, mensagem: dict[str, object]) -> Conta | None:
        try:
            id_destino = int(mensagem["idConta"])
            valor = Decimal(str(mensagem["valor"])).quantize(Decimal("0.01"))
            vetor = mensagem["timestampVetorial"]
            origem_agencia = int(mensagem["origemAgencia"])
            if not isinstance(vetor, list) or valor <= 0:
                raise ValueError
            timestamp = self.clock.ao_receber(vetor)
        except (KeyError, ValueError, ArithmeticError):
            raise ValueError("Mensagem de crédito remoto inválida.") from None

        try:
            self.conta_service.validar_particao(id_destino)
            with self.repository.transacao():
                destino = self.repository.buscar(id_destino)
                if destino is None:
                    raise ContaNaoEncontrada("Conta de destino não encontrada nesta agência.")
                destino.saldo += valor
                self.repository.atualizar(destino)
                self._registrar_evento(
                    "TRANSFERENCIA_CREDITO_REMOTO",
                    timestamp,
                    {
                        "idConta": id_destino,
                        "valor": valor,
                        "origemAgencia": origem_agencia,
                        "novoSaldo": destino.saldo,
                    },
                )
                return destino
        except ContaNaoEncontrada:
            self._registrar_evento(
                "CREDITO_REMOTO_FALHOU",
                timestamp,
                {
                    "idConta": id_destino,
                    "valor": valor,
                    "origemAgencia": origem_agencia,
                    "motivo": "CONTA_NAO_ENCONTRADA",
                },
            )
            return None

    def _transferir_local(self, origem_id: int, destino_id: int, valor: Decimal) -> None:
        with self.repository.transacao():
            origem = self.repository.buscar(origem_id)
            destino = self.repository.buscar(destino_id)
            if origem is None:
                raise ContaNaoEncontrada("Conta de origem não encontrada nesta agência.")
            if destino is None:
                raise ContaNaoEncontrada("Conta de destino não encontrada nesta agência.")
            if origem.saldo < valor:
                raise SaldoInsuficiente()
            origem.saldo -= valor
            destino.saldo += valor
            self.repository.atualizar(origem)
            self.repository.atualizar(destino)
            self._evento_local(
                "TRANSFERENCIA_DEBITO",
                {"idOrigem": origem_id, "idDestino": destino_id, "valor": valor},
            )
            self._evento_local(
                "TRANSFERENCIA_CREDITO",
                {"idOrigem": origem_id, "idDestino": destino_id, "valor": valor},
            )

    def _transferir_remota(
        self, origem_id: int, destino_id: int, agencia_destino: int, valor: Decimal
    ) -> None:
        # O broker confirma antes do débito: falha AMQP não remove valor da origem.
        with self.repository.transacao():
            origem = self.repository.buscar(origem_id)
            if origem is None:
                raise ContaNaoEncontrada("Conta de origem não encontrada nesta agência.")
            if origem.saldo < valor:
                raise SaldoInsuficiente()
            vetor_envio = self.clock.ao_enviar()
            self.publicador.publicar_credito(
                agencia_destino,
                {
                    "idConta": destino_id,
                    "valor": str(valor),
                    "timestampVetorial": vetor_envio,
                    "origemAgencia": self.settings.agencia_id,
                },
            )
            origem.saldo -= valor
            self.repository.atualizar(origem)
            self._registrar_evento(
                "TRANSFERENCIA_DEBITO",
                vetor_envio,
                {"idOrigem": origem_id, "idDestino": destino_id, "valor": valor},
            )

    def _evento_local(self, tipo: str, detalhes: dict[str, object]) -> list[int]:
        timestamp = self.clock.evento_local()
        self._registrar_evento(tipo, timestamp, detalhes)
        return timestamp

    def _registrar_evento(
        self, tipo: str, timestamp: list[int], detalhes: dict[str, object]
    ) -> None:
        self.logger.registrar(
            Evento(
                agencia=self.settings.nome_agencia,
                tipo=tipo,
                timestamp_vetorial=timestamp,
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes=detalhes,
            )
        )
