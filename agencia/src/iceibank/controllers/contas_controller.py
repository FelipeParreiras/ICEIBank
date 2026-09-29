from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from iceibank.api.dependencies import get_conta_service, usuario_atual
from iceibank.models.conta import Conta
from iceibank.schemas.conta import ContaResponse, CriarContaRequest, ValorRequest
from iceibank.services.conta_service import ContaService

router = APIRouter(
    prefix="/contas",
    tags=["Contas"],
    dependencies=[Depends(usuario_atual)],
)


def _response(conta: Conta) -> ContaResponse:
    return ContaResponse(id=conta.id, nomeAluno=conta.nome_aluno, saldo=conta.saldo)


@router.post("", response_model=ContaResponse, status_code=status.HTTP_201_CREATED)
def criar_conta(
    dados: CriarContaRequest,
    service: Annotated[ContaService, Depends(get_conta_service)],
) -> ContaResponse:
    return _response(service.criar(dados.id, dados.nome_aluno, dados.saldo_inicial))


@router.get("", response_model=list[ContaResponse])
def listar_contas(
    service: Annotated[ContaService, Depends(get_conta_service)],
) -> list[ContaResponse]:
    return [_response(conta) for conta in service.listar()]


@router.get("/{conta_id}", response_model=ContaResponse)
def buscar_conta(
    conta_id: Annotated[int, Path(ge=0)],
    service: Annotated[ContaService, Depends(get_conta_service)],
) -> ContaResponse:
    return _response(service.buscar(conta_id))


@router.post("/{conta_id}/depositar", response_model=ContaResponse)
def depositar(
    conta_id: Annotated[int, Path(ge=0)],
    dados: ValorRequest,
    service: Annotated[ContaService, Depends(get_conta_service)],
) -> ContaResponse:
    return _response(service.depositar(conta_id, dados.valor))


@router.post("/{conta_id}/sacar", response_model=ContaResponse)
def sacar(
    conta_id: Annotated[int, Path(ge=0)],
    dados: ValorRequest,
    service: Annotated[ContaService, Depends(get_conta_service)],
) -> ContaResponse:
    return _response(service.sacar(conta_id, dados.valor))
