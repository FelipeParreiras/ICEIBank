from __future__ import annotations

from pydantic import Field, field_validator

from iceibank.schemas.base import ApiSchema


class _MensagemBully(ApiSchema):
    vetor_envio: list[int] = Field(alias="vetorEnvio", min_length=3, max_length=3)

    @field_validator("vetor_envio")
    @classmethod
    def validar_vetor(cls, valor: list[int]) -> list[int]:
        if any(item < 0 for item in valor):
            raise ValueError("O vetor de envio não pode possuir valores negativos.")
        return valor


class EleicaoRequest(_MensagemBully):
    origem_id: int = Field(alias="origemId", ge=0, le=2)


class CoordenadorRequest(_MensagemBully):
    lider_id: int = Field(alias="liderId", ge=0, le=2)


class LiderResponse(ApiSchema):
    id_agencia: int = Field(alias="idAgencia")
    lider_atual: int | None = Field(alias="liderAtual")
