from fastapi.testclient import TestClient

PLANEJAMENTO = {
    "rendaPrevista": 500,
    "metaEconomia": 100,
    "limitesPorCategoria": {
        "ALIMENTACAO": 150,
        "TRANSPORTE": 100,
        "DELIVERY": 80,
        "LAZER": 70,
    },
    "categoriasFlexiveis": ["DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"],
}


def _criar_conta(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(
        "/contas",
        headers=headers,
        json={"id": 6, "nomeAluno": "Felipe", "saldoInicial": 1000},
    )
    assert response.status_code == 201, response.text


def test_planejamento_gastos_resumo_e_recomendacoes(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _criar_conta(client, auth_headers)
    planejamento = client.put(
        "/contas/6/controle-financeiro/2026-09/planejamento",
        headers=auth_headers,
        json=PLANEJAMENTO,
    )
    assert planejamento.status_code == 200, planejamento.text
    assert planejamento.json()["limiteGastoMensal"] == "400.00"

    gastos = [
        ("Mercado", 150, "ALIMENTACAO"),
        ("Ônibus", 80, "TRANSPORTE"),
        ("Pedidos", 120, "DELIVERY"),
        ("Cinema", 100, "LAZER"),
    ]
    for descricao, valor, categoria in gastos:
        response = client.post(
            "/contas/6/controle-financeiro/gastos",
            headers=auth_headers,
            json={
                "descricao": descricao,
                "valor": valor,
                "categoria": categoria,
                "data": "2026-09-10",
            },
        )
        assert response.status_code == 201, response.text

    resumo = client.get("/contas/6/controle-financeiro/2026-09", headers=auth_headers)

    assert resumo.status_code == 200
    body = resumo.json()
    assert body["totalGasto"] == "450.00"
    assert body["economiaProjetada"] == "50.00"
    assert body["valorAjuste"] == "50.00"
    assert body["status"] == "AJUSTE_NECESSARIO"
    assert body["categoriasOrdenadas"] == [
        "ALIMENTACAO", "TRANSPORTE", "DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"
    ]
    assert [(item["categoria"], item["reducaoSugerida"]) for item in body["recomendacoes"]] == [
        ("DELIVERY", "40.00"),
        ("LAZER", "10.00"),
    ]
    assert client.get("/contas/6", headers=auth_headers).json()["saldo"] == "550.00"


def test_planejamento_aceita_categoria_personalizada_e_preserva_prioridade(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _criar_conta(client, auth_headers)
    planejamento = client.put(
        "/contas/6/controle-financeiro/2026-10/planejamento",
        headers=auth_headers,
        json={
            "rendaPrevista": 1000,
            "metaEconomia": 200,
            "limitesPorCategoria": {"Pets": 180, "Cursos": 120},
            "categoriasFlexiveis": ["Pets"],
            "categoriasOrdenadas": ["Cursos", "Pets"],
        },
    )
    assert planejamento.status_code == 200, planejamento.text
    assert planejamento.json()["categoriasOrdenadas"] == ["Cursos", "Pets"]

    gasto = client.post(
        "/contas/6/controle-financeiro/gastos",
        headers=auth_headers,
        json={"descricao": "Veterinário", "valor": 80, "categoria": "Pets", "data": "2026-10-10"},
    )
    assert gasto.status_code == 201, gasto.text
    assert gasto.json()["gasto"]["categoria"] == "Pets"


def test_gasto_sem_planejamento_nao_debita(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _criar_conta(client, auth_headers)

    response = client.post(
        "/contas/6/controle-financeiro/gastos",
        headers=auth_headers,
        json={
            "descricao": "Teste",
            "valor": 10,
            "categoria": "OUTROS",
            "data": "2026-09-10",
        },
    )

    assert response.status_code == 404
    assert response.json()["codigo"] == "PLANEJAMENTO_NAO_ENCONTRADO"
    assert client.get("/contas/6", headers=auth_headers).json()["saldo"] == "1000.00"
