from threading import RLock

from iceibank.core.exceptions import UsuarioJaExiste
from iceibank.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._lock = RLock()

    def buscar(self, usuario: str) -> Usuario | None:
        with self._lock:
            return self._usuarios.get(usuario)

    def inserir(self, usuario: Usuario) -> Usuario:
        with self._lock:
            if usuario.usuario in self._usuarios:
                raise UsuarioJaExiste()
            self._usuarios[usuario.usuario] = usuario
            return usuario
