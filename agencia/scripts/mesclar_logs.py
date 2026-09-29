from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def carregar_eventos(arquivos: list[Path]) -> list[dict[str, Any]]:
    eventos: list[dict[str, Any]] = []
    for arquivo in arquivos:
        if not arquivo.exists():
            continue
        for numero_linha, linha in enumerate(
            arquivo.read_text(encoding="utf-8").splitlines(), start=1
        ):
            try:
                evento = json.loads(linha)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido em {arquivo}:{numero_linha}") from exc
            eventos.append(evento)
    return sorted(
        eventos,
        key=lambda evento: (
            evento["timestampLamport"],
            evento["agencia"],
            evento.get("horaParede", ""),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mescla os logs JSONL das agências.")
    parser.add_argument(
        "arquivos",
        nargs="*",
        type=Path,
        default=[Path("data") / f"eventos-agencia-{i}.jsonl" for i in range(3)],
    )
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    linhas = [json.dumps(item, ensure_ascii=False) for item in carregar_eventos(args.arquivos)]
    conteudo = "\n".join(linhas) + ("\n" if linhas else "")
    if args.saida:
        args.saida.write_text(conteudo, encoding="utf-8")
    else:
        print(conteudo, end="")


if __name__ == "__main__":
    main()
