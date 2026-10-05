from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from iceibank.api.router import api_router
from iceibank.core.config import Settings
from iceibank.core.exceptions import DomainError
from iceibank.repositories.caixinha_repository import CaixinhaRepository
from iceibank.repositories.conta_repository import ContaRepository
from iceibank.repositories.controle_financeiro_repository import (
    ControleFinanceiroRepository,
)
from iceibank.repositories.sqlite_database import SQLiteDatabase
from iceibank.repositories.usuario_repository import UsuarioRepository
from iceibank.services.auth_client import AuthClient
from iceibank.services.auth_service import AuthService
from iceibank.services.caixinha_service import CaixinhaService
from iceibank.services.conta_service import ContaService
from iceibank.services.controle_financeiro_service import ControleFinanceiroService
from iceibank.services.mensageria import MensageriaRabbitMQ
from iceibank.services.recomendacao_economia_service import RecomendacaoEconomiaService
from iceibank.services.registro_eventos import EventLogger
from iceibank.services.relogio_vetorial import RelogioVetorial
from iceibank.services.transferencia_service import PublicadorCredito, TransferenciaService


def create_app(
    settings: Settings | None = None,
    publicador: PublicadorCredito | None = None,
    auth_client: AuthClient | None = None,
) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app_lifespan: FastAPI):
        mensageria = getattr(app_lifespan.state, "mensageria", None)
        if mensageria is not None:
            mensageria.iniciar()
        yield
        if mensageria is not None:
            mensageria.encerrar()
        database = getattr(app_lifespan.state, "database", None)
        if database is not None:
            database.encerrar()

    app = FastAPI(
        title="ICEIBank",
        version="2.0.0-sprint2",
        description=f"API distribuída da {settings.nome_agencia}",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    database = SQLiteDatabase(settings.database_path)
    conta_repository = ContaRepository(database)
    caixinha_repository = CaixinhaRepository(database)
    financeiro_repository = ControleFinanceiroRepository(database)
    clock = RelogioVetorial(settings.agencia_id, settings.numero_agencias)
    logger = EventLogger(settings.data_dir, settings.agencia_id)
    conta_service = ContaService(conta_repository, clock, logger, settings)
    mensageria = None
    if publicador is None:
        mensageria = MensageriaRabbitMQ(
            settings,
            lambda mensagem: app.state.transferencia_service.processar_credito_remoto(mensagem),
        )
        publicador = mensageria

    app.state.settings = settings
    app.state.clock = clock
    app.state.mensageria = mensageria
    app.state.database = database
    app.state.conta_repository = conta_repository
    app.state.caixinha_repository = caixinha_repository
    app.state.financeiro_repository = financeiro_repository
    app.state.auth_service = AuthService(
        settings, UsuarioRepository(database), auth_client or AuthClient(settings)
    )
    app.state.conta_service = conta_service
    app.state.transferencia_service = TransferenciaService(
        conta_repository, conta_service, publicador, clock, logger, settings
    )
    app.state.controle_financeiro_service = ControleFinanceiroService(
        financeiro_repository,
        conta_repository,
        conta_service,
        RecomendacaoEconomiaService(),
        clock,
        logger,
    )
    app.state.caixinha_service = CaixinhaService(
        caixinha_repository, conta_repository, conta_service, clock, logger, settings
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
