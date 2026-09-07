from typing import Annotated

from fastapi import APIRouter, Depends

from iceibank.api.dependencies import get_auth_service
from iceibank.schemas.auth import LoginRequest, TokenResponse
from iceibank.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    dados: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    token, expires_in = service.login(dados.usuario, dados.senha)
    return TokenResponse(accessToken=token, expiresIn=expires_in)
