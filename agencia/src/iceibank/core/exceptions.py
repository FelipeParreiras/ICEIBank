from __future__ import annotations

from typing import Any


class DomainError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ContaForaDaParticao(DomainError):
    def __init__(self, id_conta: int, agencia_esperada: int) -> None:
        super().__init__(
            f"Conta {id_conta} não pertence a esta agência.",
            "CONTA_FORA_DA_PARTICAO",
            400,
            {"agenciaResponsavel": agencia_esperada},
        )


class ContaNaoEncontrada(DomainError):
    def __init__(self, message: str = "Conta não encontrada nesta agência.") -> None:
        super().__init__(message, "CONTA_NAO_ENCONTRADA", 404)


class ContaJaExiste(DomainError):
    def __init__(self) -> None:
        super().__init__("Conta já existe.", "CONTA_JA_EXISTE", 409)


class ValorInvalido(DomainError):
    def __init__(self, message: str = "O valor informado é inválido.") -> None:
        super().__init__(message, "VALOR_INVALIDO", 400)


class SaldoInsuficiente(DomainError):
    def __init__(self) -> None:
        super().__init__("Saldo insuficiente.", "SALDO_INSUFICIENTE", 400)


class ContasIguais(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "As contas de origem e destino devem ser diferentes.",
            "CONTAS_IGUAIS",
            400,
        )


class AgenciaIndisponivel(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Falha ao contatar agência de destino. Débito já aplicado — "
            "inconsistência conhecida da Sprint 1.",
            "AGENCIA_DESTINO_INDISPONIVEL",
            502,
            {"debitoRevertido": False},
        )


class NaoAutenticado(DomainError):
    def __init__(self, message: str, code: str = "NAO_AUTENTICADO") -> None:
        super().__init__(message, code, 401)


class PlanejamentoInvalido(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "PLANEJAMENTO_INVALIDO", 400)


class PlanejamentoNaoEncontrado(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Planejamento financeiro não encontrado para a competência.",
            "PLANEJAMENTO_NAO_ENCONTRADO",
            404,
        )
