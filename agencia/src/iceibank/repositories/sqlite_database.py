from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any


class SQLiteDatabase:
    """Conexão SQLite compartilhada pelos repositórios de uma agência."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._connection = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._transaction_depth = 0
        self._rollback_only = False
        with self._lock:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS contas (
                    id INTEGER PRIMARY KEY,
                    nome_aluno TEXT NOT NULL,
                    saldo TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS usuarios (
                    usuario TEXT PRIMARY KEY,
                    senha_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS planejamentos (
                    conta_id INTEGER NOT NULL,
                    competencia TEXT NOT NULL,
                    renda_prevista TEXT NOT NULL,
                    meta_economia TEXT NOT NULL,
                    limites_json TEXT NOT NULL,
                    flexiveis_json TEXT NOT NULL,
                    ordenadas_json TEXT NOT NULL,
                    PRIMARY KEY (conta_id, competencia)
                );
                CREATE TABLE IF NOT EXISTS gastos (
                    id TEXT PRIMARY KEY,
                    conta_id INTEGER NOT NULL,
                    descricao TEXT NOT NULL,
                    valor TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    data TEXT NOT NULL,
                    registrado_em TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_gastos_conta_competencia
                    ON gastos (conta_id, data);
                CREATE TABLE IF NOT EXISTS caixinhas (
                    id TEXT PRIMARY KEY,
                    conta_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    cor TEXT NOT NULL,
                    ordem INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_caixinhas_conta_ordem
                    ON caixinhas (conta_id, ordem, nome);
                CREATE TABLE IF NOT EXISTS lotes_caixinha (
                    id TEXT PRIMARY KEY,
                    caixinha_id TEXT NOT NULL REFERENCES caixinhas(id) ON DELETE CASCADE,
                    saldo TEXT NOT NULL,
                    proximo_rendimento_em TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS movimentos_caixinha (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caixinha_id TEXT NOT NULL REFERENCES caixinhas(id) ON DELETE CASCADE,
                    tipo TEXT NOT NULL,
                    valor TEXT NOT NULL,
                    em TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._lock:
            externa = self._transaction_depth == 0
            if externa:
                self._connection.execute("BEGIN IMMEDIATE")
                self._rollback_only = False
            self._transaction_depth += 1
            try:
                yield
            except Exception:
                self._rollback_only = True
                raise
            finally:
                self._transaction_depth -= 1
                if externa:
                    if self._rollback_only:
                        self._connection.rollback()
                    else:
                        self._connection.commit()
                    self._rollback_only = False

    def execute(self, statement: str, parameters: Sequence[Any] = ()) -> None:
        with self._lock:
            self._connection.execute(statement, parameters)

    def fetchone(self, statement: str, parameters: Sequence[Any] = ()) -> sqlite3.Row | None:
        with self._lock:
            return self._connection.execute(statement, parameters).fetchone()

    def fetchall(self, statement: str, parameters: Sequence[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            return self._connection.execute(statement, parameters).fetchall()

    def encerrar(self) -> None:
        with self._lock:
            self._connection.close()
