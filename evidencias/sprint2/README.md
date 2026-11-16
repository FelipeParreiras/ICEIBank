# Evidências da Sprint 2

As imagens desta pasta devem ser capturas reais, com data/hora visível, feitas
após configurar a instância RabbitMQ do aluno. Não foram sintetizadas pelo
projeto.

Em 04/10/2026 e 05/10/2026, a conexão AMQP, transferência assíncrona,
concorrência causal, resiliência após reinício e a funcionalidade adicional foram
executadas com a instância real. Os registros sem segredos estão em
`validacao-real.md` e `registro-execucao-2026-10-05.md`.

Os registros textuais referenciam as saídas e eventos reais, mas não substituem
as capturas PNG exigidas pelo roteiro. Elas continuam pendentes e devem ser
capturadas sem alterar ou sintetizar resultados.

- `transferencia-assincrona.png`: crédito entre duas agências em execução.
- `resiliencia-fila.png`: destino offline, publicação e retorno com conta ausente.
- `linha-do-tempo-causal.png`: pelo menos um par concorrente e um causal.
- `caixinha.png`: CRUD, guardar/resgatar ou rendimento da funcionalidade adicional.
- `registro-execucao-2026-10-05.md`: resultados, vetores e caminhos dos logs da
  rodada mais recente, sem credenciais.
