from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from iceibank.models.conta import Conta
from iceibank.repositories.sqlite_database import SQLiteDatabase


class ContaRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._database.transacao():
            yield

    @staticmethod
    def _para_modelo(linha: sqlite3.Row) -> Conta:
        return Conta(
            id=linha["id"],
            nome_aluno=linha["nome_aluno"],
            saldo=Decimal(linha["saldo"]),
        )

    def buscar(self, conta_id: int) -> Conta | None:
        linha = self._database.fetchone(
            "SELECT id, nome_aluno, saldo FROM contas WHERE id = ?", (conta_id,)
        )
        return self._para_modelo(linha) if linha else None

    def inserir(self, conta: Conta) -> Conta:
        self._database.execute(
            "INSERT INTO contas (id, nome_aluno, saldo) VALUES (?, ?, ?)",
            (conta.id, conta.nome_aluno, str(conta.saldo)),
        )
        return conta

    def atualizar(self, conta: Conta) -> Conta:
        self._database.execute(
            """
            INSERT INTO contas (id, nome_aluno, saldo) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nome_aluno = excluded.nome_aluno,
                saldo = excluded.saldo
            """,
            (conta.id, conta.nome_aluno, str(conta.saldo)),
        )
        return conta

    def listar(self) -> tuple[Conta, ...]:
        linhas = self._database.fetchall(
            "SELECT id, nome_aluno, saldo FROM contas ORDER BY id"
        )
        return tuple(self._para_modelo(linha) for linha in linhas)
