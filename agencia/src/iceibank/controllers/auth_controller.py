from typing import Annotated

from fastapi import APIRouter, Depends, status

from iceibank.api.dependencies import get_auth_service
from iceibank.schemas.auth import CadastroRequest, LoginRequest, TokenResponse
from iceibank.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    dados: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    token, expires_in = service.login(dados.usuario, dados.senha)
    return TokenResponse(accessToken=token, expiresIn=expires_in)


@router.post("/cadastro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(
    dados: CadastroRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    token, expires_in = service.cadastrar(dados.usuario, dados.senha, dados.confirmar_senha)
    return TokenResponse(accessToken=token, expiresIn=expires_in)
