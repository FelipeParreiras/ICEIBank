from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from threading import RLock

from iceibank.models.gasto import Gasto
from iceibank.models.planejamento_financeiro import PlanejamentoMensal


class ControleFinanceiroRepository:
    def __init__(self, lock: RLock | None = None) -> None:
        self._planejamentos: dict[tuple[int, str], PlanejamentoMensal] = {}
        self._gastos: dict[tuple[int, str], list[Gasto]] = defaultdict(list)
        self._lock = lock or RLock()

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._lock:
            yield

    def salvar_planejamento(self, planejamento: PlanejamentoMensal) -> PlanejamentoMensal:
        with self._lock:
            chave = (planejamento.conta_id, planejamento.competencia)
            self._planejamentos[chave] = planejamento
            return planejamento

    def buscar_planejamento(self, conta_id: int, competencia: str) -> PlanejamentoMensal | None:
        with self._lock:
            return self._planejamentos.get((conta_id, competencia))

    def inserir_gasto(self, gasto: Gasto) -> Gasto:
        with self._lock:
            self._gastos[(gasto.conta_id, gasto.competencia)].append(gasto)
            return gasto

    def listar_gastos(self, conta_id: int, competencia: str) -> tuple[Gasto, ...]:
        with self._lock:
            return tuple(self._gastos.get((conta_id, competencia), ()))
