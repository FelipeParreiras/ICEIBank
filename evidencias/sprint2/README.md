# Evidências da Sprint 2

As imagens desta pasta devem ser capturas reais, com data/hora visível, feitas
após configurar a instância RabbitMQ do aluno. Não foram sintetizadas pelo
projeto.

Em 04/10/2026, a conexão AMQP, transferência assíncrona, concorrência causal e
resiliência após reinício foram executadas com a instância real. O registro sem
segredos está em `validacao-real.md`; as capturas abaixo ainda precisam ser feitas.

- `transferencia-assincrona.png`: crédito entre duas agências em execução.
- `resiliencia-fila.png`: destino offline, publicação e retorno com conta ausente.
- `linha-do-tempo-causal.png`: pelo menos um par concorrente e um causal.
- `caixinha.png`: CRUD, guardar/resgatar ou rendimento da funcionalidade adicional.
