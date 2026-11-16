from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import UTC, datetime

import httpx

from iceibank.core.config import Settings
from iceibank.models.evento import Evento
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_vetorial import RelogioVetorial


class BullyService:
    """Eleição de líder pelo algoritmo Bully entre as três agências."""

    def __init__(
        self,
        settings: Settings,
        clock: RelogioVetorial,
        logger: EventLogger,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._clock = clock
        self._logger = logger
        self._client = client or httpx.AsyncClient(timeout=settings.bully_timeout_segundos)
        self._own_client = client is None
        self._lider_atual: int | None = None
        self._eleicao_em_andamento = False
        self._lock = asyncio.Lock()
        self._heartbeat_task: asyncio.Task[None] | None = None

    @property
    def lider_atual(self) -> int | None:
        return self._lider_atual

    @property
    def id_agencia(self) -> int:
        return self._settings.agencia_id

    def _registrar(self, tipo: str, detalhes: dict[str, object]) -> list[int]:
        vetor = self._clock.evento_local()
        self._logger.registrar(
            Evento(
                agencia=self._settings.nome_agencia,
                tipo=tipo,
                timestamp_vetorial=vetor,
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes=detalhes,
            )
        )
        return vetor

    async def iniciar_eleicao(self) -> None:
        async with self._lock:
            if self._eleicao_em_andamento:
                return
            self._eleicao_em_andamento = True

        try:
            self._registrar("ELEICAO_INICIADA", {"idAgencia": self._settings.agencia_id})
            respondeu_agencia_maior = False
            for agencia in self._settings.agencias:
                agencia_id = int(agencia["id"])
                if agencia_id <= self._settings.agencia_id:
                    continue
                try:
                    vetor_envio = self._clock.ao_enviar()
                    resposta = await self._client.post(
                        f"{agencia['url']}/bully/eleicao",
                        json={"origemId": self._settings.agencia_id, "vetorEnvio": vetor_envio},
                    )
                    resposta.raise_for_status()
                    respondeu_agencia_maior = True
                except httpx.HTTPError:
                    # Uma agência parada ou lenta não participa desta eleição.
                    continue
            if not respondeu_agencia_maior:
                await self._tornar_me_lider()
        finally:
            async with self._lock:
                self._eleicao_em_andamento = False

    async def _tornar_me_lider(self) -> None:
        self._lider_atual = self._settings.agencia_id
        self._registrar("TORNOU_LIDER", {"idAgencia": self._settings.agencia_id})
        for agencia in self._settings.agencias:
            if int(agencia["id"]) == self._settings.agencia_id:
                continue
            try:
                vetor_envio = self._clock.ao_enviar()
                resposta = await self._client.post(
                    f"{agencia['url']}/bully/coordenador",
                    json={"liderId": self._settings.agencia_id, "vetorEnvio": vetor_envio},
                )
                resposta.raise_for_status()
            except httpx.HTTPError:
                continue

    async def receber_eleicao(self, origem_id: int, vetor_recebido: list[int]) -> None:
        vetor = self._clock.ao_receber(vetor_recebido)
        self._logger.registrar(
            Evento(
                agencia=self._settings.nome_agencia,
                tipo="ELEICAO_RECEBIDA",
                timestamp_vetorial=vetor,
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes={"de": origem_id, "minhaId": self._settings.agencia_id},
            )
        )
        # A resposta HTTP é o OK para a agência menor; a maior se candidata.
        asyncio.create_task(self.iniciar_eleicao())

    def receber_coordenador(self, lider_id: int, vetor_recebido: list[int]) -> None:
        vetor = self._clock.ao_receber(vetor_recebido)
        self._logger.registrar(
            Evento(
                agencia=self._settings.nome_agencia,
                tipo="LIDER_ANUNCIADO",
                timestamp_vetorial=vetor,
                hora_parede=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                detalhes={"liderId": lider_id, "agencia": self._settings.agencia_id},
            )
        )
        if lider_id < self._settings.agencia_id:
            # Uma mensagem atrasada de uma agência menor não pode derrubar uma
            # candidata de ID maior. Isso é especialmente importante quando as
            # três instâncias sobem praticamente no mesmo instante.
            asyncio.create_task(self.iniciar_eleicao())
            return
        self._lider_atual = lider_id

    async def verificar_lider(self) -> None:
        lider = self._lider_atual
        if lider is None:
            await self.iniciar_eleicao()
            return
        if lider == self._settings.agencia_id:
            # Se uma agência maior terminou de subir depois de mim, não posso
            # continuar me considerando líder: devo permitir que ela participe.
            for agencia in self._settings.agencias:
                agencia_id = int(agencia["id"])
                if agencia_id <= self._settings.agencia_id:
                    continue
                try:
                    resposta = await self._client.get(f"{agencia['url']}/bully/lider")
                    resposta.raise_for_status()
                except httpx.HTTPError:
                    continue
                self._lider_atual = None
                await self.iniciar_eleicao()
                return
            return
        try:
            resposta = await self._client.get(f"{self._settings.url_agencia(lider)}/bully/lider")
            resposta.raise_for_status()
        except (httpx.HTTPError, ValueError):
            self._registrar(
                "LIDER_NAO_RESPONDEU",
                {"liderAtual": lider, "agencia": self._settings.agencia_id},
            )
            self._lider_atual = None
            await self.iniciar_eleicao()

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self._settings.heartbeat_intervalo_segundos)
            await self.verificar_lider()

    def iniciar_heartbeat(self) -> None:
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat())

    async def encerrar(self) -> None:
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._heartbeat_task
        if self._own_client:
            await self._client.aclose()
