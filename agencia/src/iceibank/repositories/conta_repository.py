from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from threading import RLock

from iceibank.models.conta import Conta


class ContaRepository:
    def __init__(self, lock: RLock | None = None) -> None:
        self._contas: dict[int, Conta] = {}
        self._lock = lock or RLock()

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._lock:
            yield

    def buscar(self, conta_id: int) -> Conta | None:
        with self._lock:
            conta = self._contas.get(conta_id)
            return replace(conta) if conta else None

    def inserir(self, conta: Conta) -> Conta:
        with self._lock:
            self._contas[conta.id] = replace(conta)
            return replace(conta)

    def atualizar(self, conta: Conta) -> Conta:
        with self._lock:
            self._contas[conta.id] = replace(conta)
            return replace(conta)

    def listar(self) -> tuple[Conta, ...]:
        with self._lock:
            return tuple(replace(conta) for conta in self._contas.values())
