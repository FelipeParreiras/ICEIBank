from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_PASSWORD_HASH = (
    "pbkdf2_sha256$310000$aWNlaWJhbmstZGVtby1zYWx0LXYx$xw855XV2fLp7gvfYsAi0AFbfj8V-vdUJWUrFN8J3UEE="
)


class Settings(BaseSettings):
    agencia_id: int = Field(default=0, ge=0, le=2)
    porta_base: int = Field(default=4045, ge=1, le=65533)
    numero_agencias: int = Field(default=3, ge=1)
    jwt_secret: str = "iceibank-dev-jwt-secret-change-me-2026"
    jwt_expiracao_minutos: int = Field(default=15, ge=1, le=1440)
    jwt_issuer: str = "iceibank"
    auth_username: str = "aluno"
    auth_password_hash: str = DEFAULT_PASSWORD_HASH
    internal_token: str = "iceibank-dev-internal-token-change-me"
    frontend_origin: str = "http://localhost:5173"
    timeout_agencia_segundos: float = Field(default=3.0, gt=0, le=30)
    rabbitmq_url: str | None = None
    data_dir: Path = Path("data")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("numero_agencias")
    @classmethod
    def validar_numero_agencias(cls, valor: int) -> int:
        if valor != 3:
            raise ValueError("A Sprint 1 exige exatamente 3 agências.")
        return valor

    @field_validator("jwt_secret", "internal_token")
    @classmethod
    def validar_segredo(cls, valor: str) -> str:
        if len(valor.strip()) < 16:
            raise ValueError("O segredo deve possuir ao menos 16 caracteres.")
        return valor

    @property
    def porta(self) -> int:
        return self.porta_base + self.agencia_id

    @property
    def database_path(self) -> Path:
        return self.data_dir / f"iceibank-agencia-{self.agencia_id}.sqlite3"

    @property
    def nome_agencia(self) -> str:
        return f"agencia-{self.agencia_id}"

    @property
    def agencias(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {"id": agencia_id, "url": f"http://127.0.0.1:{self.porta_base + agencia_id}"}
            for agencia_id in range(self.numero_agencias)
        )

    def url_agencia(self, agencia_id: int) -> str:
        if agencia_id < 0 or agencia_id >= self.numero_agencias:
            raise ValueError(f"Agência {agencia_id} não configurada.")
        return f"http://127.0.0.1:{self.porta_base + agencia_id}"

    def agencia_responsavel(self, id_conta: int) -> int:
        if id_conta < 0:
            raise ValueError("O ID da conta não pode ser negativo.")
        return id_conta % self.numero_agencias
