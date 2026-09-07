from pydantic import Field

from iceibank.schemas.base import ApiSchema


class LoginRequest(ApiSchema):
    usuario: str = Field(min_length=1, max_length=100)
    senha: str = Field(min_length=1, max_length=256)


class TokenResponse(ApiSchema):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")
