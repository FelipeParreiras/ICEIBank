from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from iceibank.models.caixinha import Caixinha, LoteCaixinha, MovimentoCaixinha
from iceibank.repositories.sqlite_database import SQLiteDatabase


class CaixinhaRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._database.transacao():
            yield

    def _para_modelo(self, linha: sqlite3.Row) -> Caixinha:
        caixinha_id = linha["id"]
        lotes = [
            LoteCaixinha(
                id=UUID(lote["id"]),
                saldo=Decimal(lote["saldo"]),
                proximo_rendimento_em=datetime.fromisoformat(lote["proximo_rendimento_em"]),
            )
            for lote in self._database.fetchall(
                """
                SELECT id, saldo, proximo_rendimento_em
                FROM lotes_caixinha
                WHERE caixinha_id = ?
                ORDER BY id
                """,
                (caixinha_id,),
            )
        ]
        movimentos = [
            MovimentoCaixinha(
                tipo=movimento["tipo"],
                valor=Decimal(movimento["valor"]),
                em=datetime.fromisoformat(movimento["em"]),
            )
            for movimento in self._database.fetchall(
                """
                SELECT tipo, valor, em
                FROM movimentos_caixinha
                WHERE caixinha_id = ?
                ORDER BY id
                """,
                (caixinha_id,),
            )
        ]
        return Caixinha(
            id=UUID(caixinha_id),
            conta_id=linha["conta_id"],
            nome=linha["nome"],
            cor=linha["cor"],
            ordem=linha["ordem"],
            lotes=lotes,
            movimentos=movimentos,
        )

    def _salvar(self, caixinha: Caixinha, *, nova: bool) -> Caixinha:
        parametros = (
            str(caixinha.id),
            caixinha.conta_id,
            caixinha.nome,
            caixinha.cor,
            caixinha.ordem,
        )
        if nova:
            self._database.execute(
                """
                INSERT INTO caixinhas (id, conta_id, nome, cor, ordem)
                VALUES (?, ?, ?, ?, ?)
                """,
                parametros,
            )
        else:
            self._database.execute(
                """
                UPDATE caixinhas
                SET conta_id = ?, nome = ?, cor = ?, ordem = ?
                WHERE id = ?
                """,
                (
                    caixinha.conta_id,
                    caixinha.nome,
                    caixinha.cor,
                    caixinha.ordem,
                    str(caixinha.id),
                ),
            )

        caixinha_id = str(caixinha.id)
        self._database.execute("DELETE FROM lotes_caixinha WHERE caixinha_id = ?", (caixinha_id,))
        self._database.execute(
            "DELETE FROM movimentos_caixinha WHERE caixinha_id = ?", (caixinha_id,)
        )
        for lote in caixinha.lotes:
            self._database.execute(
                """
                INSERT INTO lotes_caixinha (id, caixinha_id, saldo, proximo_rendimento_em)
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(lote.id),
                    caixinha_id,
                    str(lote.saldo),
                    lote.proximo_rendimento_em.isoformat(),
                ),
            )
        for movimento in caixinha.movimentos:
            self._database.execute(
                """
                INSERT INTO movimentos_caixinha (caixinha_id, tipo, valor, em)
                VALUES (?, ?, ?, ?)
                """,
                (
                    caixinha_id,
                    movimento.tipo,
                    str(movimento.valor),
                    movimento.em.isoformat(),
                ),
            )
        return caixinha

    def inserir(self, caixinha: Caixinha) -> Caixinha:
        return self._salvar(caixinha, nova=True)

    def buscar(self, caixinha_id: UUID) -> Caixinha | None:
        linha = self._database.fetchone(
            "SELECT id, conta_id, nome, cor, ordem FROM caixinhas WHERE id = ?",
            (str(caixinha_id),),
        )
        return self._para_modelo(linha) if linha else None

    def listar_por_conta(self, conta_id: int) -> tuple[Caixinha, ...]:
        linhas = self._database.fetchall(
            """
            SELECT id, conta_id, nome, cor, ordem
            FROM caixinhas
            WHERE conta_id = ?
            ORDER BY ordem, lower(nome), id
            """,
            (conta_id,),
        )
        return tuple(self._para_modelo(linha) for linha in linhas)

    def atualizar(self, caixinha: Caixinha) -> Caixinha:
        return self._salvar(caixinha, nova=False)

    def remover(self, caixinha_id: UUID) -> None:
        self._database.execute("DELETE FROM caixinhas WHERE id = ?", (str(caixinha_id),))
