from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from iceibank.core.config import Settings
from iceibank.core.exceptions import NaoAutenticado
from iceibank.core.security import decode_access_token
from iceibank.services.auth_service import AuthService
from iceibank.services.caixinha_service import CaixinhaService
from iceibank.services.conta_service import ContaService
from iceibank.services.controle_financeiro_service import ControleFinanceiroService
from iceibank.services.transferencia_service import TransferenciaService

bearer_scheme = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_conta_service(request: Request) -> ContaService:
    return request.app.state.conta_service


def get_transferencia_service(request: Request) -> TransferenciaService:
    return request.app.state.transferencia_service


def get_caixinha_service(request: Request) -> CaixinhaService:
    return request.app.state.caixinha_service


def get_controle_financeiro_service(request: Request) -> ControleFinanceiroService:
    return request.app.state.controle_financeiro_service


def usuario_atual(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise NaoAutenticado("Token de acesso ausente.")
    return decode_access_token(credentials.credentials, settings)


def validar_token_interno(
    settings: Annotated[Settings, Depends(get_settings)],
    token: Annotated[str | None, Header(alias="X-ICEIBANK-INTERNAL-TOKEN")] = None,
) -> None:
    if token is None or not hmac.compare_digest(token, settings.internal_token):
        raise NaoAutenticado("Token interno inválido.", "TOKEN_INTERNO_INVALIDO")
