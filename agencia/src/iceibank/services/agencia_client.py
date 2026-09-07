from __future__ import annotations

from decimal import Decimal

import httpx

from iceibank.core.config import Settings
from iceibank.core.exceptions import AgenciaIndisponivel


class AgenciaClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def creditar(
        self,
        agencia_destino: int,
        conta_destino: int,
        valor: Decimal,
        timestamp_lamport: int,
    ) -> None:
        url = (
            f"{self._settings.url_agencia(agencia_destino)}/contas/{conta_destino}/creditar-remoto"
        )
        try:
            response = httpx.post(
                url,
                json={
                    "valor": str(valor),
                    "timestampLamport": timestamp_lamport,
                    "origemAgencia": self._settings.agencia_id,
                },
                headers={"X-ICEIBANK-INTERNAL-TOKEN": self._settings.internal_token},
                timeout=self._settings.timeout_agencia_segundos,
            )
            response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            raise AgenciaIndisponivel() from exc
