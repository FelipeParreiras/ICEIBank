from __future__ import annotations

from collections.abc import Sequence


def comparar_vetores(vetor_a: Sequence[int], vetor_b: Sequence[int]) -> str:
    """Compara dois vetores com a semântica causal da Sprint 2.

    O resultado descreve a posição de ``vetor_a`` em relação a ``vetor_b``.
    """
    if len(vetor_a) != len(vetor_b):
        raise ValueError("Vetores de tamanhos diferentes não podem ser comparados.")
    if any(item < 0 for item in (*vetor_a, *vetor_b)):
        raise ValueError("Timestamp vetorial inválido.")

    a_menor_ou_igual = all(a <= b for a, b in zip(vetor_a, vetor_b, strict=True))
    b_menor_ou_igual = all(b <= a for a, b in zip(vetor_a, vetor_b, strict=True))
    if a_menor_ou_igual and b_menor_ou_igual:
        return "IGUAIS"
    if a_menor_ou_igual:
        return "ANTES"
    if b_menor_ou_igual:
        return "DEPOIS"
    return "CONCORRENTES"
