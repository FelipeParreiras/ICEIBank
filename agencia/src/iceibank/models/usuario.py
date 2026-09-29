from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Usuario:
    usuario: str
    senha_hash: str
