import pytest

from iceibank.services.comparar_vetores import comparar_vetores


@pytest.mark.parametrize(
    ("vetor_a", "vetor_b", "esperado"),
    [
        ([1, 2, 3], [1, 2, 3], "IGUAIS"),
        ([1, 2, 3], [1, 3, 3], "ANTES"),
        ([2, 3, 3], [1, 3, 3], "DEPOIS"),
        ([3, 1, 0], [1, 3, 0], "CONCORRENTES"),
    ],
)
def test_comparar_vetores(vetor_a: list[int], vetor_b: list[int], esperado: str) -> None:
    assert comparar_vetores(vetor_a, vetor_b) == esperado


def test_comparar_vetores_rejeita_tamanhos_diferentes() -> None:
    with pytest.raises(ValueError, match="tamanhos diferentes"):
        comparar_vetores([1, 0], [1, 0, 0])
