from iceibank.core.config import Settings
from iceibank.core.exceptions import CadastroInvalido, NaoAutenticado, UsuarioJaExiste
from iceibank.core.security import create_access_token, hash_password, verify_password
from iceibank.models.usuario import Usuario
from iceibank.repositories.usuario_repository import UsuarioRepository
from iceibank.services.auth_client import AuthClient


class AuthService:
    def __init__(
        self, settings: Settings, repository: UsuarioRepository, client: AuthClient
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._client = client

    def login(self, usuario: str, senha: str) -> tuple[str, int]:
        if self._settings.agencia_id != 0:
            return self._client.autenticar("login", {"usuario": usuario, "senha": senha})
        cadastrado = self._repository.buscar(usuario)
        demonstracao = usuario == self._settings.auth_username
        senha_hash = cadastrado.senha_hash if cadastrado else self._settings.auth_password_hash
        senha_valida = verify_password(senha, senha_hash)
        if not (demonstracao or cadastrado) or not senha_valida:
            raise NaoAutenticado("Usuário ou senha inválidos.", "CREDENCIAIS_INVALIDAS")
        return create_access_token(usuario, self._settings)

    def cadastrar(self, usuario: str, senha: str, confirmar_senha: str) -> tuple[str, int]:
        if senha != confirmar_senha:
            raise CadastroInvalido("As senhas não coincidem.")
        if not senha.strip():
            raise CadastroInvalido("A senha não pode conter apenas espaços.")
        if self._settings.agencia_id != 0:
            return self._client.autenticar(
                "cadastro", {"usuario": usuario, "senha": senha, "confirmarSenha": confirmar_senha}
            )
        if usuario == self._settings.auth_username:
            raise UsuarioJaExiste()
        self._repository.inserir(Usuario(usuario=usuario, senha_hash=hash_password(senha)))
        return create_access_token(usuario, self._settings)
