from iceibank.core.config import Settings
from iceibank.services.mensageria import MensageriaRabbitMQ


class CanalConfirmado:
    def __init__(self) -> None:
        self.publicacoes: list[dict[str, object]] = []

    def exchange_declare(self, **_kwargs: object) -> None:
        pass

    def confirm_delivery(self) -> None:
        pass

    def basic_publish(self, **kwargs: object) -> None:
        self.publicacoes.append(kwargs)


class ConexaoConfirmada:
    def __init__(self, canal: CanalConfirmado) -> None:
        self.canal_confirmado = canal
        self.fechada = False

    def channel(self) -> CanalConfirmado:
        return self.canal_confirmado

    def close(self) -> None:
        self.fechada = True


def test_publicacao_confirmada_por_pika_nao_depende_de_retorno_booleano(monkeypatch) -> None:
    canal = CanalConfirmado()
    conexao = ConexaoConfirmada(canal)
    monkeypatch.setattr(
        "iceibank.services.mensageria.pika.BlockingConnection", lambda _url: conexao
    )
    settings = Settings(rabbitmq_url="amqps://usuario:senha@host/vhost")
    mensageria = MensageriaRabbitMQ(settings, lambda _mensagem: None)

    mensageria.publicar_credito(1, {"idConta": 1})

    assert conexao.fechada
    assert canal.publicacoes[0]["routing_key"] == "agencia.1.creditar"
    assert canal.publicacoes[0]["properties"].delivery_mode == 2
