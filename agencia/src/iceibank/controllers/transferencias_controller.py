from typing import Annotated

from fastapi import APIRouter, Depends

from iceibank.api.dependencies import (
    get_transferencia_service,
    usuario_atual,
)
from iceibank.schemas.transferencia import (
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
        mensagem="Transferência publicada para a agência de destino (entrega assíncrona).",
        tipo="ENTRE_AGENCIAS",
    )
