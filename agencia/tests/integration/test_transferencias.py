from decimal import Decimal

from fastapi.testclient import TestClient

from iceibank.core.config import Settings
from iceibank.core.exceptions import AgenciaIndisponivel
from iceibank.main import create_app


class FakeAgenciaClient:
    def __init__(self, falhar: bool = False) -> None:
        self.falhar = falhar
        self.chamadas: list[tuple[int, int, Decimal, int]] = []

    def creditar(self, agencia: int, conta: int, valor: Decimal, timestamp: int) -> None:
        self.chamadas.append((agencia, conta, valor, timestamp))
        if self.falhar:
            raise AgenciaIndisponivel()


def _token(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"usuario": "aluno", "senha": "iceibank123"})
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def _criar(client: TestClient, headers: dict[str, str], conta_id: int, saldo: int) -> None:
    response = client.post(
        "/contas",
        headers=headers,
        json={"id": conta_id, "nomeAluno": f"Aluno {conta_id}", "saldoInicial": saldo},
    )
    assert response.status_code == 201, response.text


def test_transferencia_local_e_atomica(client: TestClient, auth_headers: dict[str, str]) -> None:
    _criar(client, auth_headers, 0, 100)
    _criar(client, auth_headers, 3, 20)

    response = client.post(
        "/transferencias",
        headers=auth_headers,
        json={"idOrigem": 0, "idDestino": 3, "valor": 30},
    )

    assert response.status_code == 200
    assert response.json()["tipo"] == "LOCAL"
    assert client.get("/contas/0", headers=auth_headers).json()["saldo"] == "70.00"
    assert client.get("/contas/3", headers=auth_headers).json()["saldo"] == "50.00"


def test_transferencia_remota_envia_timestamp_e_debita_origem(
    settings: Settings,
) -> None:
    fake = FakeAgenciaClient()
    client = TestClient(create_app(settings, fake))
    headers = _token(client)
    _criar(client, headers, 0, 100)

    response = client.post(
        "/transferencias",
        headers=headers,
        json={"idOrigem": 0, "idDestino": 1, "valor": 30},
    )

    assert response.status_code == 200
    assert response.json()["tipo"] == "ENTRE_AGENCIAS"
    assert fake.chamadas == [(1, 1, Decimal("30.00"), 3)]
    assert client.get("/contas/0", headers=headers).json()["saldo"] == "70.00"


def test_falha_remota_retorna_502_sem_estornar(settings: Settings) -> None:
    client = TestClient(create_app(settings, FakeAgenciaClient(falhar=True)))
    headers = _token(client)
    _criar(client, headers, 0, 100)

    response = client.post(
        "/transferencias",
        headers=headers,
        json={"idOrigem": 0, "idDestino": 1, "valor": 30},
    )

    assert response.status_code == 502
    assert response.json()["detalhes"] == {"debitoRevertido": False}
    assert client.get("/contas/0", headers=headers).json()["saldo"] == "70.00"


def test_credito_remoto_exige_token_interno(
    client: TestClient, auth_headers: dict[str, str], settings: Settings
) -> None:
    _criar(client, auth_headers, 0, 10)
    denied = client.post(
        "/contas/0/creditar-remoto",
        json={"valor": 5, "timestampLamport": 8, "origemAgencia": 1},
    )
    accepted = client.post(
        "/contas/0/creditar-remoto",
        headers={"X-ICEIBANK-INTERNAL-TOKEN": settings.internal_token},
        json={"valor": 5, "timestampLamport": 8, "origemAgencia": 1},
    )

    assert denied.status_code == 401
    assert denied.json()["codigo"] == "TOKEN_INTERNO_INVALIDO"
    assert accepted.status_code == 200
    assert accepted.json()["saldoAtual"] == "15.00"
    assert client.app.state.clock.value == 9
