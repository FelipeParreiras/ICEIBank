from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Evento:
    agencia: str
    tipo: str
    timestamp_vetorial: list[int]
    hora_parede: str
    detalhes: dict[str, Any]

    def para_dict(self) -> dict[str, Any]:
        return {
            "agencia": self.agencia,
            "tipo": self.tipo,
            "timestampVetorial": self.timestamp_vetorial,
            "horaParede": self.hora_parede,
            "detalhes": self.detalhes,
        }
