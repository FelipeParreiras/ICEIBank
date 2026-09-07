from iceibank.core.config import Settings
from iceibank.core.exceptions import NaoAutenticado
from iceibank.core.security import create_access_token, verify_password


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def login(self, usuario: str, senha: str) -> tuple[str, int]:
        usuario_valido = usuario == self._settings.auth_username
        senha_valida = verify_password(senha, self._settings.auth_password_hash)
        if not usuario_valido or not senha_valida:
            raise NaoAutenticado("Usuário ou senha inválidos.", "CREDENCIAIS_INVALIDAS")
        return create_access_token(usuario, self._settings)
