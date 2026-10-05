from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from threading import RLock
from uuid import UUID

from iceibank.models.caixinha import Caixinha


class CaixinhaRepository:
    def __init__(self, lock: RLock | None = None) -> None:
        self._caixinhas: dict[UUID, Caixinha] = {}
        self._lock = lock or RLock()

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._lock:
            yield

    def inserir(self, caixinha: Caixinha) -> Caixinha:
        with self._lock:
            self._caixinhas[caixinha.id] = deepcopy(caixinha)
            return deepcopy(caixinha)

    def buscar(self, caixinha_id: UUID) -> Caixinha | None:
        with self._lock:
            caixinha = self._caixinhas.get(caixinha_id)
            return deepcopy(caixinha) if caixinha else None

    def listar_por_conta(self, conta_id: int) -> tuple[Caixinha, ...]:
        with self._lock:
            return tuple(
                deepcopy(caixinha)
                for caixinha in sorted(
                    self._caixinhas.values(),
                    key=lambda item: (item.ordem, item.nome.casefold(), str(item.id)),
                )
                if caixinha.conta_id == conta_id
            )

    def atualizar(self, caixinha: Caixinha) -> Caixinha:
        with self._lock:
            self._caixinhas[caixinha.id] = deepcopy(caixinha)
            return deepcopy(caixinha)

    def remover(self, caixinha_id: UUID) -> None:
        with self._lock:
            self._caixinhas.pop(caixinha_id, None)
