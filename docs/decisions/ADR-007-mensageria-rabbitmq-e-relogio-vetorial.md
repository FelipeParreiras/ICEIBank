# ADR-007: RabbitMQ durável e relógio vetorial para créditos remotos

## Status

Aceito e implementado em 04/10/2026.

## Contexto

O crédito remoto da Sprint 1 dependia de HTTP síncrono. A Sprint 2 requer
comunicação indireta, retenção de mensagem quando o destino está offline e a
capacidade de identificar concorrência com certeza.

## Decisão

- Usar `pika` e RabbitMQ com exchange `iceibank.eventos` do tipo `topic`.
- Declarar exchange, filas e bindings como duráveis e publicar com `delivery_mode=2`.
- Manter o consumidor em uma thread daemon por agência, iniciada pelo ciclo de
  vida FastAPI.
- Remover a rota HTTP interna `/contas/{id}/creditar-remoto`.
- Substituir Lamport por `RelogioVetorial` de três posições em todos os eventos.
- Exigir confirmação do broker antes de aplicar o débito remoto. Falha de
  publicação retorna 503 sem retirar o saldo da origem.
- Confirmar mensagem cuja conta de destino não existe após registrar
  `CREDITO_REMOTO_FALHOU`; não há DLQ no escopo atual.

## Alternativas consideradas

### Manter HTTP entre agências

- Prós: menos infraestrutura.
- Contras: destino offline falha no momento da transferência.
- Rejeitada: não atende a comunicação indireta exigida.

### Debitar antes de confirmar a publicação

- Prós: segue literalmente o fluxo simplificado do exemplo didático.
- Contras: indisponibilidade do broker remove dinheiro sem mensagem confirmada.
- Rejeitada: a confirmação do publisher reduz essa falha local sem prometer
  atomicidade distribuída.

### Reenfileirar crédito para conta ausente indefinidamente

- Prós: tenta novamente após uma criação tardia.
- Contras: cria poison message e esconde a limitação de memória do roteiro.
- Rejeitada: o cenário deve ser observável e encerrado de forma determinística.

## Consequências

- O HTTP 200 remoto significa publicação, não crédito concluído.
- RabbitMQ continua sendo uma dependência operacional para transferências remotas.
- Ainda existe janela de consistência eventual entre publicação e consumo; não
  há entrega exatamente uma vez, idempotência persistida nem confirmação reversa.
- Vetores crescem linearmente com o número de agências, aceitável para três e
  custoso em sistemas com muitos participantes.

## Referências

- [SPEC-004](../specs/SPEC-004-mensageria-e-relogio-vetorial.md)
- [ADR-003](ADR-003-autenticacao-e-comunicacao-interna.md)
- Roteiro da Sprint 2, partes B, C e D.
