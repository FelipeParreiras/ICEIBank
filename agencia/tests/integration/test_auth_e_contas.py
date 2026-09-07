import json
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient


def test_rotas_de_conta_exigem_jwt(client: TestClient) -> None:
    response = client.get("/contas/0")

    assert response.status_code == 401
    assert response.json()["codigo"] == "NAO_AUTENTICADO"


def test_login_rejeita_credenciais_invalidas(client: TestClient) -> None:
    response = client.post("/auth/login", json={"usuario": "aluno", "senha": "incorreta"})

    assert response.status_code == 401
    assert response.json()["codigo"] == "CREDENCIAIS_INVALIDAS"


def test_token_expirado_retorna_codigo_especifico(client: TestClient, settings) -> None:
    agora = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "aluno",
            "iss": settings.jwt_issuer,
            "iat": agora - timedelta(minutes=2),
            "exp": agora - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )

    response = client.get("/contas/0", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["codigo"] == "TOKEN_EXPIRADO"


def test_criar_depositar_sacar_e_consultar(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/contas",
        headers=auth_headers,
        json={"id": 0, "nomeAluno": "Ana", "saldoInicial": 200},
    )
    deposited = client.post("/contas/0/depositar", headers=auth_headers, json={"valor": 25.5})
    withdrawn = client.post("/contas/0/sacar", headers=auth_headers, json={"valor": 20})
    found = client.get("/contas/0", headers=auth_headers)

    assert created.status_code == 201
    assert deposited.json()["saldo"] == "225.50"
    assert withdrawn.json()["saldo"] == "205.50"
    assert found.json() == {"id": 0, "nomeAluno": "Ana", "saldo": "205.50"}


def test_particao_e_saldo_sao_validados(client: TestClient, auth_headers: dict[str, str]) -> None:
    wrong_partition = client.post(
        "/contas",
        headers=auth_headers,
        json={"id": 1, "nomeAluno": "Bia", "saldoInicial": 10},
    )
    client.post(
        "/contas",
        headers=auth_headers,
        json={"id": 0, "nomeAluno": "Ana", "saldoInicial": 10},
    )
    insufficient = client.post("/contas/0/sacar", headers=auth_headers, json={"valor": 11})

    assert wrong_partition.status_code == 400
    assert wrong_partition.json()["detalhes"] == {"agenciaResponsavel": 1}
    assert insufficient.status_code == 400
    assert insufficient.json()["codigo"] == "SALDO_INSUFICIENTE"


def test_mutacoes_geram_jsonl(client: TestClient, auth_headers: dict[str, str], settings) -> None:
    client.post(
        "/contas",
        headers=auth_headers,
        json={"id": 0, "nomeAluno": "Ana", "saldoInicial": 10},
    )
    client.post("/contas/0/depositar", headers=auth_headers, json={"valor": 5})

    linhas = (
        settings.data_dir.joinpath("eventos-agencia-0.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    eventos = [json.loads(linha) for linha in linhas]
    assert [evento["tipo"] for evento in eventos] == ["CRIAR_CONTA", "DEPOSITO"]
    assert [evento["timestampLamport"] for evento in eventos] == [1, 2]
