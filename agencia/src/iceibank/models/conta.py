from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Conta:
    id: int
    nome_aluno: str
    saldo: Decimal
