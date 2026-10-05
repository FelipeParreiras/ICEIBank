# ADR-008: Ciclo de 48 horas e exclusão protegida da Caixinha

## Status

Aceito e implementado em 04/10/2026. A regra de exclusão foi substituída pelo
[ADR-009](ADR-009-exclusao-caixinha-com-resgate-automatico.md); as regras de
tempo e arredondamento permanecem aceitas.

## Contexto

O ADR-006 definiu lotes, rendimento composto e resgate FIFO, mas deixou abertas
a medição de dois dias, o arredondamento e a exclusão com saldo.

## Decisão

- Um período é de 48 horas completas, contado individualmente a partir de cada
  depósito ou do vencimento anterior do mesmo lote.
- O saldo de cada lote é multiplicado por 1,10 a cada período vencido e o
  resultado é quantizado para centavos com `ROUND_HALF_UP`.
- Rendimento vencido é aplicado sob demanda antes de listar, consultar, guardar,
  resgatar ou excluir; cada lote guarda seu próximo vencimento, impedindo dupla
  aplicação no mesmo período.
- A exclusão com saldo era bloqueada nesta decisão original. Foi substituída em
  05/10/2026 pelo resgate automático descrito no ADR-009.
- O relógio é injetável no serviço para testes determinísticos. A persistência
  SQLite local passou a preservar Caixinhas e lotes após o ADR-010.

## Alternativas consideradas

### Regra por dias do calendário

- Prós: descrição familiar ao usuário.
- Contras: ambígua em horário de verão e depósitos no meio do dia.
- Rejeitada: 48 horas é verificável e preserva a regra do roteiro.

### Excluir com resgate automático

- Prós: menos passos na interface.
- Contras: produz uma movimentação financeira inesperada.
- Rejeitada: exclusão deve ser segura e não alterar saldo silenciosamente.

## Consequências

- Leitura pode materializar rendimento vencido e registrar evento vetorial.
- Valores compostos são estáveis em centavos, mas acumulam os efeitos naturais
  de arredondamento a cada ciclo.
- Persistência será necessária antes de tratar reinício como cenário bancário real.

## Referências

- [ADR-006](ADR-006-caixinha-lotes-fifo.md)
- [SPEC-003](../specs/SPEC-003-caixinha.md)
