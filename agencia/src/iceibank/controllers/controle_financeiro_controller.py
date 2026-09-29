from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from iceibank.api.dependencies import (
    get_controle_financeiro_service,
    usuario_atual,
)
from iceibank.models.gasto import Gasto
from iceibank.models.planejamento_financeiro import (
    PlanejamentoMensal,
    ResumoFinanceiro,
)
from iceibank.schemas.controle_financeiro import (
    GastoResponse,
    PlanejamentoMensalRequest,
    PlanejamentoMensalResponse,
    RecomendacaoResponse,
    RegistrarGastoRequest,
    RegistrarGastoResponse,
    ResumoFinanceiroResponse,
)
from iceibank.services.controle_financeiro_service import ControleFinanceiroService

router = APIRouter(
    prefix="/contas/{conta_id}/controle-financeiro",
    tags=["Controle financeiro"],
    dependencies=[Depends(usuario_atual)],
)


def _planejamento_response(
    planejamento: PlanejamentoMensal,
) -> PlanejamentoMensalResponse:
    return PlanejamentoMensalResponse(
        contaId=planejamento.conta_id,
        competencia=planejamento.competencia,
        rendaPrevista=planejamento.renda_prevista,
        metaEconomia=planejamento.meta_economia,
        limiteGastoMensal=planejamento.limite_gasto_mensal,
        limitesPorCategoria=planejamento.limites_por_categoria,
        categoriasFlexiveis=planejamento.categorias_flexiveis,
    )


def _gasto_response(gasto: Gasto) -> GastoResponse:
    return GastoResponse(
        id=gasto.id,
        contaId=gasto.conta_id,
        descricao=gasto.descricao,
        valor=gasto.valor,
        categoria=gasto.categoria,
        data=gasto.data,
        competencia=gasto.competencia,
        registradoEm=gasto.registrado_em,
    )


@router.put("/{competencia}/planejamento", response_model=PlanejamentoMensalResponse)
def definir_planejamento(
    conta_id: Annotated[int, Path(ge=0)],
    competencia: str,
    dados: PlanejamentoMensalRequest,
    service: Annotated[ControleFinanceiroService, Depends(get_controle_financeiro_service)],
) -> PlanejamentoMensalResponse:
    planejamento = service.definir_planejamento(
        conta_id,
        competencia,
        dados.renda_prevista,
        dados.meta_economia,
        dados.limites_por_categoria,
        dados.categorias_flexiveis,
    )
    return _planejamento_response(planejamento)


@router.post(
    "/gastos",
    response_model=RegistrarGastoResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_gasto(
    conta_id: Annotated[int, Path(ge=0)],
    dados: RegistrarGastoRequest,
    service: Annotated[ControleFinanceiroService, Depends(get_controle_financeiro_service)],
) -> RegistrarGastoResponse:
    gasto, saldo = service.registrar_gasto(
        conta_id, dados.descricao, dados.valor, dados.categoria, dados.data
    )
    return RegistrarGastoResponse(gasto=_gasto_response(gasto), saldoConta=saldo)


@router.get("/{competencia}", response_model=ResumoFinanceiroResponse)
def obter_resumo(
    conta_id: Annotated[int, Path(ge=0)],
    competencia: str,
    service: Annotated[ControleFinanceiroService, Depends(get_controle_financeiro_service)],
) -> ResumoFinanceiroResponse:
    resumo: ResumoFinanceiro = service.obter_resumo(conta_id, competencia)
    return ResumoFinanceiroResponse(
        contaId=resumo.planejamento.conta_id,
        competencia=resumo.planejamento.competencia,
        rendaPrevista=resumo.planejamento.renda_prevista,
        metaEconomia=resumo.planejamento.meta_economia,
        limiteGastoMensal=resumo.planejamento.limite_gasto_mensal,
        totalGasto=resumo.total_gasto,
        economiaProjetada=resumo.economia_projetada,
        saldoParaGastar=resumo.saldo_para_gastar,
        valorAjuste=resumo.valor_ajuste,
        status=resumo.status,
        totaisPorCategoria=resumo.totais_por_categoria,
        recomendacoes=[
            RecomendacaoResponse(
                categoria=item.categoria,
                totalGasto=item.total_gasto,
                limiteConfigurado=item.limite_configurado,
                reducaoSugerida=item.reducao_sugerida,
                motivo=item.motivo,
            )
            for item in resumo.recomendacoes
        ],
        valorNaoCoberto=resumo.valor_nao_coberto,
        gastos=[_gasto_response(gasto) for gasto in resumo.gastos],
    )
