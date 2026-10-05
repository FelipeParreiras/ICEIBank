from __future__ import annotations

import argparse
import json
from enum import StrEnum
from pathlib import Path
from typing import Any


class RelacaoVetorial(StrEnum):
    ANTES = "ANTES"
    DEPOIS = "DEPOIS"
    IGUAIS = "IGUAIS"
    CONCORRENTES = "CONCORRENTES"


def comparar_vetores(primeiro: list[int], segundo: list[int]) -> RelacaoVetorial:
    if len(primeiro) != len(segundo):
        raise ValueError("Vetores de tamanhos diferentes não podem ser comparados.")
    primeiro_menor = all(a <= b for a, b in zip(primeiro, segundo))
    segundo_menor = all(b <= a for a, b in zip(primeiro, segundo))
    if primeiro_menor and segundo_menor:
        return RelacaoVetorial.IGUAIS
    if primeiro_menor:
        return RelacaoVetorial.ANTES
    if segundo_menor:
        return RelacaoVetorial.DEPOIS
    return RelacaoVetorial.CONCORRENTES


def carregar_eventos(arquivos: list[Path]) -> list[dict[str, Any]]:
    eventos: list[dict[str, Any]] = []
    for arquivo in arquivos:
        if not arquivo.exists():
            continue
        for numero_linha, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                evento = json.loads(linha)
                vetor = evento["timestampVetorial"]
                if not isinstance(vetor, list) or any(not isinstance(item, int) for item in vetor):
                    raise ValueError("timestampVetorial inválido")
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                raise ValueError(f"Evento inválido em {arquivo}:{numero_linha}") from exc
            eventos.append(evento)
    return sorted(eventos, key=lambda evento: (evento.get("horaParede", ""), evento["agencia"]))


def pares_concorrentes(eventos: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [
        (primeiro, segundo)
        for indice, primeiro in enumerate(eventos)
        for segundo in eventos[indice + 1 :]
        if primeiro["agencia"] != segundo["agencia"]
        and comparar_vetores(primeiro["timestampVetorial"], segundo["timestampVetorial"])
        == RelacaoVetorial.CONCORRENTES
    ]


def formatar_linha_do_tempo(eventos: list[dict[str, Any]]) -> str:
    linhas = ["=== Linha do tempo (ordenada por hora de parede) ==="]
    linhas.extend(
        f"[{evento['agencia']}] vetor={evento['timestampVetorial']} {evento['tipo']} {json.dumps(evento['detalhes'], ensure_ascii=False, default=str)}"
        for evento in eventos
    )
    linhas.append("\n=== Pares de eventos CONCORRENTES entre agências diferentes ===")
    pares = pares_concorrentes(eventos)
    if not pares:
        linhas.append("(nenhum par concorrente encontrado nesta execução - gere eventos independentes e rode novamente)")
    for primeiro, segundo in pares:
        linhas.append(f"[{primeiro['agencia']}] {primeiro['tipo']} ({primeiro['timestampVetorial']}) x [{segundo['agencia']}] {segundo['tipo']} ({segundo['timestampVetorial']})")
    return "\n".join(linhas) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mescla logs e identifica concorrência causal.")
    parser.add_argument("arquivos", nargs="*", type=Path, default=[Path("data") / f"eventos-agencia-{i}.jsonl" for i in range(3)])
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    conteudo = formatar_linha_do_tempo(carregar_eventos(args.arquivos))
    if args.saida:
        args.saida.write_text(conteudo, encoding="utf-8")
    else:
        print(conteudo, end="")


if __name__ == "__main__":
    main()
