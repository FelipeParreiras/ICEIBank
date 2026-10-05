from __future__ import annotations

from threading import Lock


class RelogioVetorial:
    """Relógio vetorial de tamanho fixo, um contador para cada agência."""

    def __init__(self, id_agencia: int, numero_agencias: int) -> None:
        if numero_agencias <= 0 or not 0 <= id_agencia < numero_agencias:
            raise ValueError("Configuração inválida para o relógio vetorial.")
        self._id_agencia = id_agencia
        self._vetor = [0] * numero_agencias
        self._lock = Lock()

    @property
    def value(self) -> list[int]:
        with self._lock:
            return list(self._vetor)

    def evento_local(self) -> list[int]:
        with self._lock:
            self._vetor[self._id_agencia] += 1
            return list(self._vetor)

    def ao_enviar(self) -> list[int]:
        return self.evento_local()

    def ao_receber(self, vetor_recebido: list[int]) -> list[int]:
        if len(vetor_recebido) != len(self._vetor) or any(
            not isinstance(item, int) or item < 0 for item in vetor_recebido
        ):
            raise ValueError("Timestamp vetorial inválido.")
        with self._lock:
            self._vetor = [
                max(local, recebido)
                for local, recebido in zip(self._vetor, vetor_recebido, strict=True)
            ]
            self._vetor[self._id_agencia] += 1
            return list(self._vetor)
