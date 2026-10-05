# SPEC-004: Mensageria assíncrona e relógio vetorial

## Status

Implementado e validado por testes automatizados e RabbitMQ real em 04/10/2026.
As capturas PNG exigidas permanecem pendentes; não foram sintetizadas.

## Objetivo

Substituir o crédito remoto HTTP da Sprint 1 por Publish/Subscribe via RabbitMQ
e registrar causalidade com relógios vetoriais de três posições.

## Escopo

- Exchange durável `iceibank.eventos`, do tipo `topic`.
- Filas duráveis `fila-agencia-0`, `fila-agencia-1` e `fila-agencia-2`, com
  routing key `agencia.<id>.creditar`.
- Mensagens persistentes de crédito remoto e confirmação de publicação pelo broker.
- Um consumidor em thread por processo FastAPI.
- Campo JSONL `timestampVetorial`; `timestampLamport` não é mais emitido.
- Linha do tempo ordenada por hora de parede e análise de pares concorrentes.

Não inclui persistência das contas, autorização por titularidade, confirmação de
crédito ao remetente ou dead-letter queue.

## Comportamento funcional

Uma transferência local permanece atômica na agência. Para uma transferência
remota, a agência valida a origem e o saldo, incrementa o vetor de envio,
publica uma mensagem persistente e só então debita a conta. A resposta HTTP 200
informa que a mensagem foi publicada, não que o crédito terminou.

O consumidor combina cada posição do vetor recebido com o vetor local usando
o máximo e incrementa sua própria posição antes de aplicar o crédito. Se a
conta não existir, registra `CREDITO_REMOTO_FALHOU` e confirma a mensagem para
evitar reentrega infinita. A ausência pode decorrer de uma conta nunca criada
ou da remoção consciente do SQLite local da agência.

## Design técnico

`MensageriaRabbitMQ` é o adaptador de infraestrutura baseado em `pika`.
`TransferenciaService` contém a regra bancária e recebe uma porta
`PublicadorCredito`, o que permite testes sem broker. O ciclo de vida FastAPI
inicia e sinaliza o encerramento do consumidor. Sem `RABBITMQ_URL`, a aplicação
continua disponível para regressões locais, mas uma transferência remota retorna
`503 MENSAGERIA_INDISPONIVEL` e não debita a origem.

`RelogioVetorial` é sincronizado, devolve cópias imutáveis para o chamador e
rejeita vetores de tamanho ou valores inválidos. Dois vetores incomparáveis são
concorrentes; um vetor menor ou igual em todas as posições aconteceu antes.

## Validação

- Testes unitários cobrem evento local, envio, recebimento e comparação vetorial.
- Testes de integração cobrem publicação, crédito consumido, conta ausente e
  ausência da rota HTTP legada.
- A validação real deve iniciar as três agências com `RABBITMQ_URL`, verificar
  a topologia no Manager e executar o cenário de resiliência do roteiro.
- Em 04/10/2026, a execução real confirmou publicação e crédito de R$ 30,00
  (origem R$ 200,00 para R$ 170,00; destino R$ 10,00 para R$ 40,00). Após o
  reinício do destino, a mensagem pendente foi consumida e registrou
  `CREDITO_REMOTO_FALHOU` por `CONTA_NAO_ENCONTRADA`.

## Referências

- [ADR-007](../decisions/ADR-007-mensageria-rabbitmq-e-relogio-vetorial.md)
- [API Sprint 2](../API_SPRINT_2.md)
- [Configuração Sprint 2](../CONFIGURACAO_SPRINT_2.md)
