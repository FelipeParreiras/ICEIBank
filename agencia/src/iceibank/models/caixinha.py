from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(slots=True)
class LoteCaixinha:
    saldo: Decimal
    proximo_rendimento_em: datetime
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class Caixinha:
    conta_id: int
    nome: str
    id: UUID = field(default_factory=uuid4)
    lotes: list[LoteCaixinha] = field(default_factory=list)

    @property
    def saldo(self) -> Decimal:
        return sum((lote.saldo for lote in self.lotes), Decimal("0.00"))
