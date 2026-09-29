from pydantic import Field

from iceibank.schemas.base import ApiSchema


class LoginRequest(ApiSchema):
    usuario: str = Field(min_length=1, max_length=100)
    senha: str = Field(min_length=1, max_length=256)


class TokenResponse(ApiSchema):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")


class CadastroRequest(ApiSchema):
    usuario: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    senha: str = Field(min_length=8, max_length=256)
    confirmar_senha: str = Field(alias="confirmarSenha", min_length=8, max_length=256)
