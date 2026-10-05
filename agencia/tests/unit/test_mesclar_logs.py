import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from mesclar_logs import RelacaoVetorial, comparar_vetores, pares_concorrentes


def test_comparacao_vetorial_distingue_causalidade_e_concorrencia() -> None:
    assert comparar_vetores([3, 1, 0], [3, 2, 0]) == RelacaoVetorial.ANTES
    assert comparar_vetores([3, 1, 0], [1, 3, 0]) == RelacaoVetorial.CONCORRENTES


def test_pares_concorrentes_ignora_eventos_causais_e_da_mesma_agencia() -> None:
    eventos = [
        {"agencia": "agencia-0", "timestampVetorial": [1, 0, 0]},
        {"agencia": "agencia-1", "timestampVetorial": [0, 1, 0]},
        {"agencia": "agencia-1", "timestampVetorial": [2, 1, 0]},
    ]
    assert pares_concorrentes(eventos) == [(eventos[0], eventos[1])]
