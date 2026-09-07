from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Evento:
    agencia: str
    tipo: str
    timestamp_lamport: int
    hora_parede: str
    detalhes: dict[str, Any]

    def para_dict(self) -> dict[str, Any]:
        return {
            "agencia": self.agencia,
            "tipo": self.tipo,
            "timestampLamport": self.timestamp_lamport,
            "horaParede": self.hora_parede,
            "detalhes": self.detalhes,
        }
