import sqlite3

from iceibank.core.exceptions import UsuarioJaExiste
from iceibank.models.usuario import Usuario
from iceibank.repositories.sqlite_database import SQLiteDatabase


class UsuarioRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def buscar(self, usuario: str) -> Usuario | None:
        linha = self._database.fetchone(
            "SELECT usuario, senha_hash FROM usuarios WHERE usuario = ?", (usuario,)
        )
        return Usuario(usuario=linha["usuario"], senha_hash=linha["senha_hash"]) if linha else None

    def inserir(self, usuario: Usuario) -> Usuario:
        try:
            self._database.execute(
                "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                (usuario.usuario, usuario.senha_hash),
            )
        except sqlite3.IntegrityError as erro:
            raise UsuarioJaExiste() from erro
        return usuario
