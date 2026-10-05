from __future__ import annotations

import json
import logging
from collections.abc import Callable
from threading import Event, Thread
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel

from iceibank.core.config import Settings
from iceibank.core.exceptions import MensageriaIndisponivel

EXCHANGE = "iceibank.eventos"
LOGGER = logging.getLogger(__name__)


class MensageriaRabbitMQ:
    """Adapter AMQP síncrono; o consumo fica em thread própria do processo."""

    def __init__(self, settings: Settings, ao_receber: Callable[[dict[str, Any]], None]) -> None:
        self._settings = settings
        self._ao_receber = ao_receber
        self._thread: Thread | None = None
        self._parar = Event()

    @property
    def habilitada(self) -> bool:
        return bool(self._settings.rabbitmq_url)

    def iniciar(self) -> None:
        if not self.habilitada or self._thread is not None:
            return
        self._thread = Thread(target=self._consumir, name="consumidor-rabbitmq", daemon=True)
        self._thread.start()

    def encerrar(self) -> None:
        self._parar.set()

    def publicar_credito(self, agencia_destino: int, mensagem: dict[str, object]) -> None:
        if not self._settings.rabbitmq_url:
            raise MensageriaIndisponivel()
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self._settings.rabbitmq_url))
            channel = connection.channel()
            self._declarar_exchange(channel)
            channel.confirm_delivery()
            # Com publisher confirms habilitado, ``pika`` sinaliza sucesso pela
            # ausência de NackError/UnroutableError; o retorno é ``None``.
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=f"agencia.{agencia_destino}.creditar",
                body=json.dumps(mensagem, ensure_ascii=False, default=str).encode(),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
                mandatory=True,
            )
            connection.close()
        except (pika.exceptions.AMQPError, OSError, ValueError) as exc:
            raise MensageriaIndisponivel() from exc

    def _declarar_exchange(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    def _consumir(self) -> None:
        if not self._settings.rabbitmq_url:
            return
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self._settings.rabbitmq_url))
            channel = connection.channel()
            self._declarar_exchange(channel)
            fila = f"fila-agencia-{self._settings.agencia_id}"
            channel.queue_declare(queue=fila, durable=True)
            channel.queue_bind(
                queue=fila,
                exchange=EXCHANGE,
                routing_key=f"agencia.{self._settings.agencia_id}.creditar",
            )

            def callback(
                canal: BlockingChannel,
                metodo: pika.spec.Basic.Deliver,
                _props: pika.spec.BasicProperties,
                corpo: bytes,
            ) -> None:
                try:
                    self._ao_receber(json.loads(corpo.decode()))
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
                    LOGGER.exception("Mensagem AMQP inválida descartada após registro local.")
                finally:
                    canal.basic_ack(delivery_tag=metodo.delivery_tag)

            channel.basic_consume(queue=fila, on_message_callback=callback, auto_ack=False)
            while not self._parar.is_set():
                connection.process_data_events(time_limit=1)
            connection.close()
        except (pika.exceptions.AMQPError, OSError, ValueError):
            LOGGER.exception(
                "Consumidor RabbitMQ da agência %s foi interrompido.", self._settings.agencia_id
            )
