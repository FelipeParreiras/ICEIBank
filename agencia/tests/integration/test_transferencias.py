from fastapi.testclient import TestClient

from iceibank.core.config import Settings
from iceibank.core.exceptions import MensageriaIndisponivel
from iceibank.main import create_app


class FakePublicador:
    def __init__(self, falhar: bool = False) -> None:
        self.falhar = falhar
        self.mensagens: list[tuple[int, dict[str, object]]] = []

    def publicar_credito(self, agencia: int, mensagem: dict[str, object]) -> None:
        if self.falhar:
            raise MensageriaIndisponivel()
        self.mensagens.append((agencia, mensagem))


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


def test_transferencia_remota_publica_vetor_e_debita_origem(settings: Settings) -> None:
    publicador = FakePublicador()
    client = TestClient(create_app(settings, publicador))
    headers = _token(client)
    _criar(client, headers, 0, 100)
    response = client.post(
        "/transferencias",
        headers=headers,
        json={"idOrigem": 0, "idDestino": 1, "valor": 30},
    )
    assert response.status_code == 200
    assert response.json()["tipo"] == "ENTRE_AGENCIAS"
    assert "publicada" in response.json()["mensagem"]
    assert publicador.mensagens == [
        (
            1,
            {"idConta": 1, "valor": "30.00", "timestampVetorial": [2, 0, 0], "origemAgencia": 0},
        )
    ]
    assert client.get("/contas/0", headers=headers).json()["saldo"] == "70.00"


def test_falha_na_publicacao_nao_debita_origem(settings: Settings) -> None:
    client = TestClient(create_app(settings, FakePublicador(falhar=True)))
    headers = _token(client)
    _criar(client, headers, 0, 100)
    response = client.post(
        "/transferencias",
        headers=headers,
        json={"idOrigem": 0, "idDestino": 1, "valor": 30},
    )
    assert response.status_code == 503
    assert response.json()["codigo"] == "MENSAGERIA_INDISPONIVEL"
    assert client.get("/contas/0", headers=headers).json()["saldo"] == "100.00"


def test_consumidor_aplica_credito_e_registra_vetor(settings: Settings) -> None:
    app = create_app(settings, FakePublicador())
    client = TestClient(app)
    headers = _token(client)
    _criar(client, headers, 0, 10)
    resultado = app.state.transferencia_service.processar_credito_remoto(
        {"idConta": 0, "valor": "5.00", "timestampVetorial": [3, 2, 0], "origemAgencia": 1}
    )
    assert resultado is not None
    assert resultado.saldo == 15
    assert app.state.clock.value == [4, 2, 0]
    assert client.get("/contas/0", headers=headers).json()["saldo"] == "15.00"


def test_consumidor_registra_conta_ausente_sem_reentrega(settings: Settings) -> None:
    app = create_app(settings, FakePublicador())
    assert (
        app.state.transferencia_service.processar_credito_remoto(
            {"idConta": 0, "valor": "5.00", "timestampVetorial": [1, 2, 0], "origemAgencia": 1}
        )
        is None
    )
    eventos = settings.data_dir.joinpath("eventos-agencia-0.jsonl").read_text(encoding="utf-8")
    assert "CREDITO_REMOTO_FALHOU" in eventos


def test_rota_http_interna_foi_removida(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.post("/contas/0/creditar-remoto", headers=auth_headers).status_code == 404
