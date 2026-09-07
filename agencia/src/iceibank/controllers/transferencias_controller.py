from typing import Annotated

from fastapi import APIRouter, Depends, Path

from iceibank.api.dependencies import (
    get_transferencia_service,
    usuario_atual,
    validar_token_interno,
)
from iceibank.schemas.transferencia import (
    CreditoRemotoRequest,
    CreditoRemotoResponse,
    MensagemTransferenciaResponse,
    TransferenciaRequest,
)
from iceibank.services.transferencia_service import TransferenciaService

router = APIRouter(tags=["Transferências"])


@router.post(
    "/transferencias",
    response_model=MensagemTransferenciaResponse,
    dependencies=[Depends(usuario_atual)],
)
def transferir(
    dados: TransferenciaRequest,
    service: Annotated[TransferenciaService, Depends(get_transferencia_service)],
) -> MensagemTransferenciaResponse:
    tipo = service.transferir(dados.id_origem, dados.id_destino, dados.valor)
    if tipo == "LOCAL":
        return MensagemTransferenciaResponse(
            mensagem="Transferência concluída (mesma agência).", tipo="LOCAL"
        )
    return MensagemTransferenciaResponse(
        mensagem="Transferência concluída (entre agências).", tipo="ENTRE_AGENCIAS"
    )


@router.post(
    "/contas/{conta_id}/creditar-remoto",
    response_model=CreditoRemotoResponse,
    dependencies=[Depends(validar_token_interno)],
)
def creditar_remoto(
    conta_id: Annotated[int, Path(ge=0)],
    dados: CreditoRemotoRequest,
    service: Annotated[TransferenciaService, Depends(get_transferencia_service)],
) -> CreditoRemotoResponse:
    conta = service.creditar_remotamente(
        conta_id,
        dados.valor,
        dados.timestamp_lamport,
        dados.origem_agencia,
    )
    return CreditoRemotoResponse(mensagem="Crédito remoto aplicado.", saldoAtual=conta.saldo)
