from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def _criar_conta(client: TestClient, headers: dict[str, str], conta_id: int, saldo: int) -> None:
    response = client.post(
        "/contas",
        headers=headers,
        json={"id": conta_id, "nomeAluno": "Ana", "saldoInicial": saldo},
    )
    assert response.status_code == 201


def test_caixinha_crud_guarda_e_resgata(client: TestClient, auth_headers: dict[str, str]) -> None:
    _criar_conta(client, auth_headers, 0, 100)
    criada = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Viagem"})
    caixinha_id = criada.json()["id"]
    assert criada.json()["cor"] == "verde"
    guardada = client.post(
        f"/contas/0/caixinhas/{caixinha_id}/guardar", headers=auth_headers, json={"valor": 40}
    )
    assert guardada.status_code == 200
    assert guardada.json()["saldoConta"] == "60.00"
    assert guardada.json()["caixinha"]["saldo"] == "40.00"
    assert guardada.json()["caixinha"]["movimentos"][0]["tipo"] == "DEPOSITO"
    assert client.get("/contas/0", headers=auth_headers).json()["saldo"] == "60.00"
    resgatada = client.post(
        f"/contas/0/caixinhas/{caixinha_id}/resgatar", headers=auth_headers, json={"valor": 15}
    )
    assert resgatada.status_code == 200
    assert resgatada.json()["saldoConta"] == "75.00"
    assert resgatada.json()["caixinha"]["saldo"] == "25.00"
    assert client.get("/contas/0", headers=auth_headers).json()["saldo"] == "75.00"
    excluida = client.delete(f"/contas/0/caixinhas/{caixinha_id}", headers=auth_headers)
    assert excluida.status_code == 200
    assert excluida.json()["saldoConta"] == "100.00"
    assert excluida.json()["valorResgatado"] == "25.00"
    assert client.get("/contas/0", headers=auth_headers).json()["saldo"] == "100.00"
    assert client.get("/contas/0/caixinhas", headers=auth_headers).json() == []

    nova = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Viagem 2"})
    novo_id = nova.json()["id"]
    assert (
        client.patch(
            f"/contas/0/caixinhas/{novo_id}",
            headers=auth_headers,
            json={"nome": "Férias", "cor": "azul"},
        ).json()["nome"]
        == "Férias"
    )
    atualizada = client.get(f"/contas/0/caixinhas/{novo_id}", headers=auth_headers).json()
    assert atualizada["cor"] == "azul"
    assert (
        client.patch(
            f"/contas/0/caixinhas/{novo_id}", headers=auth_headers, json={"cor": "amarelo"}
        ).status_code
        == 422
    )
    assert (
        client.delete(f"/contas/0/caixinhas/{novo_id}", headers=auth_headers).status_code == 200
    )


def test_caixinha_aplica_juros_compostos_e_fifo(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _criar_conta(client, auth_headers, 0, 500)
    criada = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Reserva"})
    caixinha_id = criada.json()["id"]
    agora = datetime(2026, 1, 1, tzinfo=UTC)
    client.app.state.caixinha_service.agora = lambda: agora
    client.post(
        f"/contas/0/caixinhas/{caixinha_id}/guardar", headers=auth_headers, json={"valor": 100}
    )
    agora += timedelta(hours=48)
    primeiro = client.get(f"/contas/0/caixinhas/{caixinha_id}", headers=auth_headers).json()
    assert primeiro["saldo"] == "110.00"
    assert primeiro["rendimentoTotal"] == "10.00"
    assert primeiro["movimentos"][0]["tipo"] == "RENDIMENTO"
    client.post(
        f"/contas/0/caixinhas/{caixinha_id}/guardar", headers=auth_headers, json={"valor": 220}
    )
    retirada = client.post(
        f"/contas/0/caixinhas/{caixinha_id}/resgatar", headers=auth_headers, json={"valor": 270}
    ).json()["caixinha"]
    assert retirada["saldo"] == "60.00"
    agora += timedelta(hours=48)
    assert (
        client.get(f"/contas/0/caixinhas/{caixinha_id}", headers=auth_headers).json()["saldo"]
        == "66.00"
    )


def test_caixinha_nao_vaza_entre_contas(client: TestClient, auth_headers: dict[str, str]) -> None:
    _criar_conta(client, auth_headers, 0, 100)
    _criar_conta(client, auth_headers, 3, 100)
    criada = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Privada"})
    caixinha_id = criada.json()["id"]
    assert client.get(f"/contas/3/caixinhas/{caixinha_id}", headers=auth_headers).status_code == 404


def test_caixinha_persiste_ordem_personalizada(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _criar_conta(client, auth_headers, 0, 100)
    viagem = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Viagem"})
    reserva = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Reserva"})
    estudos = client.post("/contas/0/caixinhas", headers=auth_headers, json={"nome": "Estudos"})
    ids = [viagem.json()["id"], reserva.json()["id"], estudos.json()["id"]]

    resposta = client.put(
        "/contas/0/caixinhas/ordem",
        headers=auth_headers,
        json={"caixinhasIds": [ids[2], ids[0], ids[1]]},
    )

    assert resposta.status_code == 200
    assert [item["nome"] for item in resposta.json()] == ["Estudos", "Viagem", "Reserva"]
    assert [item["ordem"] for item in resposta.json()] == [0, 1, 2]
    listagem = client.get("/contas/0/caixinhas", headers=auth_headers).json()
    assert [item["nome"] for item in listagem] == [
        "Estudos",
        "Viagem",
        "Reserva",
    ]

    invalida = client.put(
        "/contas/0/caixinhas/ordem",
        headers=auth_headers,
        json={"caixinhasIds": [ids[0], ids[0], ids[1]]},
    )
    assert invalida.status_code == 400
