from __future__ import annotations

from decimal import Decimal, InvalidOperation

from iceibank.core.exceptions import ValorInvalido

CENTAVOS = Decimal("0.01")


def normalizar_dinheiro(valor: object, *, permitir_zero: bool = False) -> Decimal:
    try:
        decimal = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValorInvalido() from exc

    if not decimal.is_finite():
        raise ValorInvalido("O valor deve ser finito.")
    if decimal < 0 or (decimal == 0 and not permitir_zero):
        raise ValorInvalido("O valor deve ser maior que zero.")
    if decimal.as_tuple().exponent < -2:
        raise ValorInvalido("O valor deve possuir no máximo duas casas decimais.")
    return decimal.quantize(CENTAVOS)
