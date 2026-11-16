from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from iceibank.api.dependencies import get_bully_service
from iceibank.schemas.bully import CoordenadorRequest, EleicaoRequest, LiderResponse
from iceibank.services.bully_service import BullyService

router = APIRouter(prefix="/bully", tags=["Consenso"])


@router.post("/eleicao", status_code=200)
async def receber_eleicao(
    dados: EleicaoRequest,
    service: Annotated[BullyService, Depends(get_bully_service)],
) -> None:
    await service.receber_eleicao(dados.origem_id, dados.vetor_envio)


@router.post("/coordenador", status_code=200)
async def receber_coordenador(
    dados: CoordenadorRequest,
    service: Annotated[BullyService, Depends(get_bully_service)],
) -> None:
    service.receber_coordenador(dados.lider_id, dados.vetor_envio)


@router.get("/lider", response_model=LiderResponse)
def obter_lider(service: Annotated[BullyService, Depends(get_bully_service)]) -> LiderResponse:
    return LiderResponse(idAgencia=service.id_agencia, liderAtual=service.lider_atual)
