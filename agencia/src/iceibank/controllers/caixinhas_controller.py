from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from iceibank.api.dependencies import get_caixinha_service, usuario_atual
from iceibank.models.caixinha import Caixinha
from iceibank.schemas.caixinha import (
    AtualizarCaixinhaRequest,
    CaixinhaResponse,
    CriarCaixinhaRequest,
    LoteCaixinhaResponse,
    MovimentoCaixinhaRequest,
    MovimentoCaixinhaResponse,
)
from iceibank.services.caixinha_service import CaixinhaService

router = APIRouter(
    prefix="/contas/{conta_id}/caixinhas", tags=["Caixinhas"], dependencies=[Depends(usuario_atual)]
)


def _response(caixinha: Caixinha) -> CaixinhaResponse:
    return CaixinhaResponse(
        id=caixinha.id,
        contaId=caixinha.conta_id,
        nome=caixinha.nome,
        saldo=caixinha.saldo,
        lotes=[
            LoteCaixinhaResponse(
                id=lote.id, saldo=lote.saldo, proximoRendimentoEm=lote.proximo_rendimento_em
            )
            for lote in caixinha.lotes
        ],
    )


@router.post("", response_model=CaixinhaResponse, status_code=status.HTTP_201_CREATED)
def criar(
    conta_id: Annotated[int, Path(ge=0)],
    dados: CriarCaixinhaRequest,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> CaixinhaResponse:
    return _response(service.criar(conta_id, dados.nome))


@router.get("", response_model=list[CaixinhaResponse])
def listar(
    conta_id: Annotated[int, Path(ge=0)],
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> list[CaixinhaResponse]:
    return [_response(caixinha) for caixinha in service.listar(conta_id)]


@router.get("/{caixinha_id}", response_model=CaixinhaResponse)
def buscar(
    conta_id: Annotated[int, Path(ge=0)],
    caixinha_id: UUID,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> CaixinhaResponse:
    return _response(service.buscar(conta_id, caixinha_id))


@router.patch("/{caixinha_id}", response_model=CaixinhaResponse)
def renomear(
    conta_id: Annotated[int, Path(ge=0)],
    caixinha_id: UUID,
    dados: AtualizarCaixinhaRequest,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> CaixinhaResponse:
    return _response(service.renomear(conta_id, caixinha_id, dados.nome))


@router.delete("/{caixinha_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(
    conta_id: Annotated[int, Path(ge=0)],
    caixinha_id: UUID,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> None:
    service.excluir(conta_id, caixinha_id)


@router.post("/{caixinha_id}/guardar", response_model=MovimentoCaixinhaResponse)
def guardar(
    conta_id: Annotated[int, Path(ge=0)],
    caixinha_id: UUID,
    dados: MovimentoCaixinhaRequest,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> MovimentoCaixinhaResponse:
    caixinha, saldo_conta = service.guardar(conta_id, caixinha_id, dados.valor)
    return MovimentoCaixinhaResponse(caixinha=_response(caixinha), saldoConta=saldo_conta)


@router.post("/{caixinha_id}/resgatar", response_model=MovimentoCaixinhaResponse)
def resgatar(
    conta_id: Annotated[int, Path(ge=0)],
    caixinha_id: UUID,
    dados: MovimentoCaixinhaRequest,
    service: Annotated[CaixinhaService, Depends(get_caixinha_service)],
) -> MovimentoCaixinhaResponse:
    caixinha, saldo_conta = service.resgatar(conta_id, caixinha_id, dados.valor)
    return MovimentoCaixinhaResponse(caixinha=_response(caixinha), saldoConta=saldo_conta)
