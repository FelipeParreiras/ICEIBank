from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import UUID

from iceibank.models.evento import Evento


def _json_default(value: Any) -> str:
    if isinstance(value, (Decimal, UUID, date, datetime, Enum)):
        return str(value)
    raise TypeError(f"Tipo não serializável: {type(value).__name__}")


class EventLogger:
    def __init__(self, data_dir: Path, agencia_id: int) -> None:
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / f"eventos-agencia-{agencia_id}.jsonl"
        self._lock = Lock()

    def registrar(self, evento: Evento) -> None:
        linha = json.dumps(
            evento.para_dict(), ensure_ascii=False, default=_json_default, sort_keys=True
        )
        with self._lock, self.path.open("a", encoding="utf-8") as arquivo:
            arquivo.write(linha + "\n")
