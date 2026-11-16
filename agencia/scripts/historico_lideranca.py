"""Reconstrói o histórico de eleição Bully a partir dos JSONL das agências."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TIPOS_BULLY = {
    "ELEICAO_INICIADA",
    "ELEICAO_RECEBIDA",
    "TORNOU_LIDER",
    "LIDER_ANUNCIADO",
    "LIDER_NAO_RESPONDEU",
}


def carregar_eventos(data_dir: Path) -> list[dict[str, Any]]:
    eventos: list[dict[str, Any]] = []
    for arquivo in sorted(data_dir.glob("eventos-agencia-*.jsonl")):
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                evento = json.loads(linha)
                if evento.get("tipo") in TIPOS_BULLY:
                    eventos.append(evento)
    return sorted(eventos, key=lambda evento: str(evento["horaParede"]))


def imprimir_historico(eventos: list[dict[str, Any]]) -> None:
    print("=== Histórico de eventos de eleição ===")
    for evento in eventos:
        print(
            f"({evento['horaParede']}) [{evento['agencia']}] {evento['tipo']} "
            f"{json.dumps(evento['detalhes'], ensure_ascii=False)}"
        )
    print("\n=== Linha do tempo de líderes ===")
    for evento in eventos:
        if evento["tipo"] == "TORNOU_LIDER":
            print(
                f"A partir de {evento['horaParede']}: "
                f"Agência {evento['detalhes']['idAgencia']} é a líder"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    argumentos = parser.parse_args()
    imprimir_historico(carregar_eventos(argumentos.data_dir))
