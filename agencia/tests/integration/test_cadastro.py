from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient

from iceibank.core.config import Settings
from iceibank.core.exceptions import UsuarioJaExiste
from iceibank.core.security import decode_access_token, verify_password
from iceibank.main import create_app
from iceibank.repositories.usuario_repository import UsuarioRepository
from iceibank.services.auth_client import AuthClient
from iceibank.services.auth_service import AuthService


def dados(usuario: str = "novo.usuario") -> dict[str, str]:
    return {"usuario": usuario, "senha": "senha-teste-123", "confirmarSenha": "senha-teste-123"}


def test_cadastro_login_e_token_em_todas_as_agencias(client: TestClient, settings: Settings):
    response = client.post("/auth/cadastro", json=dados())
    assert response.status_code == 201
    payload = response.json()
    assert set(payload) == {"accessToken", "tokenType", "expiresIn"}
    assert decode_access_token(payload["accessToken"], settings) == "novo.usuario"
    headers = {"Authorization": f"Bearer {payload['accessToken']}"}
    for agencia_id in range(3):
        agencia = TestClient(create_app(settings.model_copy(update={"agencia_id": agencia_id})))
        # Uma conta inexistente retorna 404, demonstrando que o JWT foi aceito.
        assert agencia.get(f"/contas/{agencia_id}", headers=headers).status_code == 404
    assert client.post("/auth/login", json=dados()).status_code == 200
    assert (
        client.post(
            "/auth/login", json={"usuario": "novo.usuario", "senha": "incorreta"}
        ).status_code
        == 401
    )


@pytest.mark.parametrize("usuario", ["novo.usuario", "aluno"])
def test_usuario_duplicado_nao_substitui_senha(client: TestClient, usuario: str):
    if usuario != "aluno":
        assert client.post("/auth/cadastro", json=dados(usuario)).status_code == 201
    response = client.post(
        "/auth/cadastro",
        json={"usuario": usuario, "senha": "outra-senha", "confirmarSenha": "outra-senha"},
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "USUARIO_JA_EXISTE"
    senha = "iceibank123" if usuario == "aluno" else dados()["senha"]
    assert client.post("/auth/login", json={"usuario": usuario, "senha": senha}).status_code == 200


@pytest.mark.parametrize(
    "alteracao,status",
    [
        ({"usuario": "ab"}, 422),
        ({"usuario": "a" * 101}, 422),
        ({"usuario": "   "}, 422),
        ({"usuario": "ana silva"}, 422),
        ({"senha": "curta"}, 422),
        ({"senha": "x" * 257}, 422),
        ({"confirmarSenha": "diferente"}, 400),
        ({"senha": "        ", "confirmarSenha": "        "}, 400),
    ],
)
def test_cadastro_invalido_nao_cria_usuario(client: TestClient, alteracao: dict, status: int):
    body = dados() | alteracao
    response = client.post("/auth/cadastro", json=body)
    assert response.status_code == status
    assert '"input"' not in response.text
    login_status = 422 if len(body["usuario"]) > 100 or len(body["senha"]) > 256 else 401
    assert client.post("/auth/login", json=body).status_code == login_status
    assert client.post("/auth/cadastro", json=dados()).status_code == 201


def test_cadastro_armazena_hash_e_impede_duplicacao_concorrente(settings: Settings):
    repository = UsuarioRepository()
    service = AuthService(settings, repository, AuthClient(settings))

    def cadastrar(_: int) -> str:
        try:
            service.cadastrar("concorrente", "senha-teste-123", "senha-teste-123")
            return "criado"
        except UsuarioJaExiste:
            return "duplicado"

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(cadastrar, range(2))) == ["criado", "duplicado"]
    usuario = repository.buscar("concorrente")
    assert usuario is not None
    assert usuario.senha_hash != "senha-teste-123"
    assert verify_password("senha-teste-123", usuario.senha_hash)


def test_agencias_encaminham_cadastro_login_e_erros_para_agencia_zero(
    client: TestClient, settings: Settings, monkeypatch: pytest.MonkeyPatch
):
    def post(url: str, *, json: dict, timeout: float) -> httpx.Response:
        assert url.startswith(settings.url_agencia(0))
        assert timeout == settings.timeout_agencia_segundos
        return client.post(httpx.URL(url).path, json=json)

    monkeypatch.setattr(httpx, "post", post)
    agencias = [
        TestClient(create_app(settings.model_copy(update={"agencia_id": i}))) for i in (1, 2)
    ]
    assert agencias[0].post("/auth/cadastro", json=dados()).status_code == 201
    assert agencias[1].post("/auth/login", json=dados()).status_code == 200
    assert agencias[1].post("/auth/cadastro", json=dados()).status_code == 409
    response = agencias[1].post("/auth/login", json={"usuario": "novo.usuario", "senha": "errada"})
    assert response.status_code == 401
    assert response.json()["codigo"] == "CREDENCIAIS_INVALIDAS"


def test_autenticacao_remota_indisponivel(settings: Settings, monkeypatch: pytest.MonkeyPatch):
    def post(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "post", post)
    client = TestClient(create_app(settings.model_copy(update={"agencia_id": 1})))
    for rota in ("login", "cadastro"):
        response = client.post(f"/auth/{rota}", json=dados())
        assert response.status_code == 503
        assert response.json()["codigo"] == "AUTENTICACAO_INDISPONIVEL"
