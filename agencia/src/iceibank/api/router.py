from fastapi import APIRouter

from iceibank.controllers import (
    auth_controller,
    caixinhas_controller,
    contas_controller,
    controle_financeiro_controller,
    transferencias_controller,
)

api_router = APIRouter()
api_router.include_router(auth_controller.router)
api_router.include_router(contas_controller.router)
api_router.include_router(caixinhas_controller.router)
api_router.include_router(transferencias_controller.router)
api_router.include_router(controle_financeiro_controller.router)
