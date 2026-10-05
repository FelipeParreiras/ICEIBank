import pytest

from iceibank.services.relogio_vetorial import RelogioVetorial


def test_evento_local_e_envio_incrementam_posicao_da_agencia() -> None:
    clock = RelogioVetorial(1, 3)
    assert clock.evento_local() == [0, 1, 0]
    assert clock.ao_enviar() == [0, 2, 0]


def test_recebimento_faz_maximo_e_incrementa_posicao_local() -> None:
    clock = RelogioVetorial(0, 3)
    clock.evento_local()
    assert clock.ao_receber([0, 3, 2]) == [2, 3, 2]


def test_rejeita_vetor_incompativel() -> None:
    with pytest.raises(ValueError):
        RelogioVetorial(0, 3).ao_receber([1, 2])
