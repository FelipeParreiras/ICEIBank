from fastapi.testclient import TestClient


def criar_conta(client: TestClient, auth_headers: dict[str, str], conta_id: int = 0) -> None:
    response = client.post(
        "/contas",
        headers=auth_headers,
        json={"id": conta_id, "nomeAluno": "Ana", "saldoInicial": 100},
    )
    assert response.status_code == 201, response.text


def test_coordenador_atualiza_lider_exposta_pela_api(client: TestClient) -> None:
    response = client.post(
        "/bully/coordenador", json={"liderId": 2, "vetorEnvio": [0, 0, 1]}
    )
    assert response.status_code == 200

    lider = client.get("/bully/lider")
    assert lider.status_code == 200
    assert lider.json() == {"idAgencia": 0, "liderAtual": 2}


def test_sincronizacao_offline_detecta_conflito_e_reaplica_com_vetor_atual(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    criar_conta(client, auth_headers)
    saldo = client.get("/contas/0", headers=auth_headers)
    assert saldo.status_code == 200
    vetor_antigo = saldo.json()["vetorAtual"]

    deposito = client.post("/contas/0/depositar", headers=auth_headers, json={"valor": 30})
    assert deposito.status_code == 200

    conflito = client.post(
        "/contas/0/sincronizar",
        headers=auth_headers,
        json={"tipo": "SAQUE", "valor": 10, "vetorConhecido": vetor_antigo},
    )
    assert conflito.status_code == 409
    detalhes = conflito.json()["detalhes"]
    assert detalhes["contaAtual"]["saldo"] == 130.0

    sincronizada = client.post(
        "/contas/0/sincronizar",
        headers=auth_headers,
        json={"tipo": "SAQUE", "valor": 10, "vetorConhecido": detalhes["vetorAtual"]},
    )
    assert sincronizada.status_code == 200
    assert sincronizada.json()["saldo"] == "120.00"
    assert sincronizada.json()["vetorAtual"] == [3, 0, 0]
