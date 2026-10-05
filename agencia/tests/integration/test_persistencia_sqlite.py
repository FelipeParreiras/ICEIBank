from fastapi.testclient import TestClient

from iceibank.core.config import Settings
from iceibank.main import create_app


def _headers(client: TestClient) -> dict[str, str]:
    resposta = client.post("/auth/login", json={"usuario": "aluno", "senha": "iceibank123"})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['accessToken']}"}


def test_dados_financeiros_persistem_apos_reiniciar_agencia(settings: Settings) -> None:
    with TestClient(create_app(settings)) as primeira_agencia:
        headers = _headers(primeira_agencia)
        assert primeira_agencia.post(
            "/contas",
            headers=headers,
            json={"id": 9, "nomeAluno": "Ana", "saldoInicial": 500},
        ).status_code == 201
        caixinha = primeira_agencia.post(
            "/contas/9/caixinhas", headers=headers, json={"nome": "Reserva"}
        )
        assert caixinha.status_code == 201
        caixinha_id = caixinha.json()["id"]
        assert primeira_agencia.post(
            f"/contas/9/caixinhas/{caixinha_id}/guardar",
            headers=headers,
            json={"valor": 100},
        ).status_code == 200
        assert primeira_agencia.put(
            "/contas/9/controle-financeiro/2026-10/planejamento",
            headers=headers,
            json={
                "rendaPrevista": 1000,
                "metaEconomia": 200,
                "limitesPorCategoria": {"ALIMENTACAO": 300},
                "categoriasFlexiveis": [],
            },
        ).status_code == 200
        assert primeira_agencia.post(
            "/contas/9/controle-financeiro/gastos",
            headers=headers,
            json={
                "descricao": "Mercado",
                "valor": 50,
                "categoria": "ALIMENTACAO",
                "data": "2026-10-10",
            },
        ).status_code == 201

    with TestClient(create_app(settings)) as agencia_reiniciada:
        headers = _headers(agencia_reiniciada)
        conta = agencia_reiniciada.get("/contas/9", headers=headers)
        caixinhas = agencia_reiniciada.get("/contas/9/caixinhas", headers=headers)
        resumo = agencia_reiniciada.get(
            "/contas/9/controle-financeiro/2026-10", headers=headers
        )

    assert conta.json()["saldo"] == "350.00"
    assert caixinhas.json()[0]["saldo"] == "100.00"
    assert caixinhas.json()[0]["cor"] == "verde"
    assert resumo.json()["totalGasto"] == "50.00"


def test_usuario_cadastrado_persiste_apos_reiniciar_agencia_zero(settings: Settings) -> None:
    cadastro = {
        "usuario": "ana.sqlite",
        "senha": "senha-teste-123",
        "confirmarSenha": "senha-teste-123",
    }
    with TestClient(create_app(settings)) as primeira_agencia:
        assert primeira_agencia.post("/auth/cadastro", json=cadastro).status_code == 201

    with TestClient(create_app(settings)) as agencia_reiniciada:
        resposta = agencia_reiniciada.post(
            "/auth/login", json={"usuario": cadastro["usuario"], "senha": cadastro["senha"]}
        )

    assert resposta.status_code == 200
