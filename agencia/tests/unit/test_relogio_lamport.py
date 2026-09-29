from iceibank.services.relogio_lamport import LamportClock


def test_evento_local_incrementa_relogio() -> None:
    clock = LamportClock()

    assert clock.ao_enviar() == 1
    assert clock.ao_enviar() == 2
    assert clock.value == 2


def test_recebimento_usa_maximo_mais_um() -> None:
    clock = LamportClock()
    clock.ao_enviar()
    clock.ao_enviar()

    assert clock.ao_receber(7) == 8
    assert clock.ao_receber(3) == 9
