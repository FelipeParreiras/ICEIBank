# ADR-009: Exclusão da Caixinha com resgate automático

## Status

Aceito e implementado em 05/10/2026; revisado em 11/10/2026. Substitui apenas a decisão de exclusão
protegida do ADR-008.

## Contexto

A interface passou a tratar a Caixinha como uma reserva gerenciada por cartões,
com histórico e uma ação explícita de gerenciamento. Exigir que o usuário faça
um resgate manual antes de excluir cria uma etapa extra e deixa a exclusão sem
conclusão direta.

## Decisão

Ao excluir uma Caixinha, o serviço aplica os rendimentos vencidos, resgata todo
o saldo para a conta vinculada e remove a Caixinha na mesma transação local. A
resposta informa o valor resgatado e o saldo atualizado da conta. O frontend
explica o resgate automático antes de apresentar a ação de exclusão.

## Alternativas consideradas

### Bloquear exclusão com saldo

- Prós: evita movimentação financeira durante a exclusão.
- Contras: exige duas ações para concluir uma intenção única do usuário.
- Rejeitada: o novo fluxo torna a consequência visível e a operação é atômica.

### Excluir e descartar o saldo

- Prós: implementação simples.
- Contras: perde dinheiro simulado e viola a conservação do saldo.
- Rejeitada: o saldo sempre deve retornar à conta vinculada.

## Consequências

- A exclusão passa a alterar o saldo da conta, mesmo quando iniciada na gestão
  da Caixinha.
- O histórico persistido registra depósitos, retiradas e rendimentos enquanto a
  Caixinha existe; após a exclusão, o evento vetorial registra o resgate final.
- A operação é limitada ao SQLite local da agência e não cria transação distribuída.

## Referências

- [ADR-008](ADR-008-caixinha-tempo-arredondamento-e-exclusao.md)
- [SPEC-003](../specs/SPEC-003-caixinha.md)
- [Contrato da API Sprint 2](../API_SPRINT_2.md)
