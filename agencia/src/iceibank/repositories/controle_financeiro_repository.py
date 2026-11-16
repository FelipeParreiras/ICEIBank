from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from iceibank.models.gasto import Gasto
from iceibank.models.planejamento_financeiro import PlanejamentoMensal
from iceibank.repositories.sqlite_database import SQLiteDatabase


class ControleFinanceiroRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    @contextmanager
    def transacao(self) -> Iterator[None]:
        with self._database.transacao():
            yield

    @staticmethod
    def _planejamento_para_modelo(linha: sqlite3.Row) -> PlanejamentoMensal:
        limites = {
            categoria: Decimal(valor)
            for categoria, valor in json.loads(linha["limites_json"]).items()
        }
        return PlanejamentoMensal(
            conta_id=linha["conta_id"],
            competencia=linha["competencia"],
            renda_prevista=Decimal(linha["renda_prevista"]),
            meta_economia=Decimal(linha["meta_economia"]),
            limites_por_categoria=limites,
            categorias_flexiveis=frozenset(json.loads(linha["flexiveis_json"])),
            categorias_ordenadas=tuple(json.loads(linha["ordenadas_json"])),
        )

    @staticmethod
    def _gasto_para_modelo(linha: sqlite3.Row) -> Gasto:
        return Gasto(
            id=UUID(linha["id"]),
            conta_id=linha["conta_id"],
            descricao=linha["descricao"],
            valor=Decimal(linha["valor"]),
            categoria=linha["categoria"],
            data=date.fromisoformat(linha["data"]),
            registrado_em=datetime.fromisoformat(linha["registrado_em"]),
        )

    def salvar_planejamento(self, planejamento: PlanejamentoMensal) -> PlanejamentoMensal:
        limites_json = json.dumps(
            {
                categoria: str(valor)
                for categoria, valor in planejamento.limites_por_categoria.items()
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        self._database.execute(
            """
            INSERT INTO planejamentos (
                conta_id, competencia, renda_prevista, meta_economia,
                limites_json, flexiveis_json, ordenadas_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(conta_id, competencia) DO UPDATE SET
                renda_prevista = excluded.renda_prevista,
                meta_economia = excluded.meta_economia,
                limites_json = excluded.limites_json,
                flexiveis_json = excluded.flexiveis_json,
                ordenadas_json = excluded.ordenadas_json
            """,
            (
                planejamento.conta_id,
                planejamento.competencia,
                str(planejamento.renda_prevista),
                str(planejamento.meta_economia),
                limites_json,
                json.dumps(sorted(planejamento.categorias_flexiveis), ensure_ascii=False),
                json.dumps(list(planejamento.categorias_ordenadas), ensure_ascii=False),
            ),
        )
        return planejamento

    def buscar_planejamento(self, conta_id: int, competencia: str) -> PlanejamentoMensal | None:
        linha = self._database.fetchone(
            """
            SELECT conta_id, competencia, renda_prevista, meta_economia,
                   limites_json, flexiveis_json, ordenadas_json
            FROM planejamentos
            WHERE conta_id = ? AND competencia = ?
            """,
            (conta_id, competencia),
        )
        return self._planejamento_para_modelo(linha) if linha else None

    def inserir_gasto(self, gasto: Gasto) -> Gasto:
        self._database.execute(
            """
            INSERT INTO gastos (
                id, conta_id, descricao, valor, categoria, data, registrado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(gasto.id),
                gasto.conta_id,
                gasto.descricao,
                str(gasto.valor),
                gasto.categoria,
                gasto.data.isoformat(),
                gasto.registrado_em.isoformat(),
            ),
        )
        return gasto

    def listar_gastos(self, conta_id: int, competencia: str) -> tuple[Gasto, ...]:
        linhas = self._database.fetchall(
            """
            SELECT id, conta_id, descricao, valor, categoria, data, registrado_em
            FROM gastos
            WHERE conta_id = ? AND substr(data, 1, 7) = ?
            ORDER BY registrado_em, id
            """,
            (conta_id, competencia),
        )
        return tuple(self._gasto_para_modelo(linha) for linha in linhas)
