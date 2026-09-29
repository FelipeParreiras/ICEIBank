from __future__ import annotations

from threading import RLock

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from iceibank.api.router import api_router
from iceibank.core.config import Settings
from iceibank.core.exceptions import DomainError
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.repositories.controle_financeiro_repository import (
    ControleFinanceiroRepository,
)
from iceibank.repositories.usuario_repository import UsuarioRepository
from iceibank.services.agencia_client import AgenciaClient
from iceibank.services.auth_client import AuthClient
from iceibank.services.auth_service import AuthService
from iceibank.services.conta_service import ContaService
from iceibank.services.controle_financeiro_service import ControleFinanceiroService
from iceibank.services.recomendacao_economia_service import RecomendacaoEconomiaService
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_lamport import LamportClock
from iceibank.services.transferencia_service import TransferenciaService


def create_app(
    settings: Settings | None = None,
    agencia_client: AgenciaClient | None = None,
    auth_client: AuthClient | None = None,
) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title="ICEIBank",
        version="1.0.0-sprint1",
        description=f"API distribuída da {settings.nome_agencia}",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    state_lock = RLock()
    conta_repository = ContaRepository(state_lock)
    financeiro_repository = ControleFinanceiroRepository(state_lock)
    clock = LamportClock()
    logger = EventLogger(settings.data_dir, settings.agencia_id)
    conta_service = ContaService(conta_repository, clock, logger, settings)
    client = agencia_client or AgenciaClient(settings)

    app.state.settings = settings
    app.state.clock = clock
    app.state.conta_repository = conta_repository
    app.state.financeiro_repository = financeiro_repository
    app.state.auth_service = AuthService(
        settings, UsuarioRepository(), auth_client or AuthClient(settings)
    )
    app.state.conta_service = conta_service
    app.state.transferencia_service = TransferenciaService(
        conta_repository, conta_service, client, clock, logger, settings
    )
    app.state.controle_financeiro_service = ControleFinanceiroService(
        financeiro_repository,
        conta_repository,
        conta_service,
        RecomendacaoEconomiaService(),
        clock,
        logger,
    )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {"erro": exc.message, "codigo": exc.code, "detalhes": exc.details}
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        if _request.url.path.startswith("/auth/"):
            errors = [
                {key: error[key] for key in ("type", "loc", "msg") if key in error}
                for error in errors
            ]
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                {
                    "erro": "Requisição inválida.",
                    "codigo": "REQUISICAO_INVALIDA",
                    "detalhes": errors,
                }
            ),
        )

    @app.get("/", tags=["Sistema"])
    def raiz() -> dict[str, object]:
        return {
            "sistema": "ICEIBank",
            "agencia": settings.agencia_id,
            "porta": settings.porta,
            "documentacao": "/docs",
        }

    app.include_router(api_router)
    return app


app = create_app()
