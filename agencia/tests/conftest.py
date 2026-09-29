from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from iceibank.core.config import Settings
from iceibank.main import create_app


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        agencia_id=0,
        data_dir=tmp_path,
        jwt_secret="segredo-jwt-seguro-para-testes-1234",
        internal_token="token-interno-seguro-para-testes",
    )


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"usuario": "aluno", "senha": "iceibank123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}
