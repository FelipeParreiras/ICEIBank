import httpx

from iceibank.core.config import Settings
from iceibank.core.exceptions import AutenticacaoIndisponivel, DomainError
from iceibank.schemas.auth import TokenResponse


class AuthClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def autenticar(self, operacao: str, dados: dict[str, str]) -> tuple[str, int]:
        try:
            response = httpx.post(
                f"{self._settings.url_agencia(0)}/auth/{operacao}",
                json=dados,
                timeout=self._settings.timeout_agencia_segundos,
            )
            if response.status_code in (400, 401, 409, 422):
                payload = response.json()
                raise DomainError(
                    payload["erro"],
                    payload["codigo"],
                    response.status_code,
                    payload.get("detalhes"),
                )
            response.raise_for_status()
            token = TokenResponse.model_validate(response.json())
            return token.access_token, token.expires_in
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise AutenticacaoIndisponivel() from exc
