# ADR-006: Caixinha por lotes com rendimento composto e resgate FIFO

## Status

Aceito e implementado. Revisado em 11/10/2026. A especificação vigente inclui
também cor, gerenciamento, resgate automático na exclusão, ordenação
personalizada e persistência SQLite local das Caixinhas.

## Data

2026-09-28

## Contexto

A Caixinha é o adicional escolhido para a Sprint 2. Cada depósito deve cumprir
seu próprio prazo para render 10% a cada dois dias. Um saldo agregado isolado
não preserva a idade dos depósitos nem determina qual prazo sobrevive ao resgate.

## Decisão

- Representar cada depósito como um lote com data/hora e saldo próprios.
- Guardar transfere valor do saldo disponível da conta para a Caixinha;
  resgatar faz o movimento inverso.
- Incorporar rendimentos ao saldo do mesmo lote, com juros compostos.
- Consumir os lotes em ordem do mais antigo ao mais recente (FIFO).
- Consumir principal e rendimentos como saldo único de cada lote.
- Preservar o prazo do lote parcialmente resgatado: o próximo rendimento incide
  sobre o saldo remanescente, sem reiniciar a contagem por causa do resgate.
- Rejeitar resgate acima do saldo disponível sem movimentação parcial.
- Aplicar os rendimentos vencidos até o instante do resgate antes de validar
  o saldo e consumir lotes, incluindo vencimentos exatamente naquele instante.
  Não reaplicar períodos já remunerados.

A decisão registra as regras explicitamente confirmadas pelo aluno. À época ela
não definia persistência, agendamento, endpoints ou arredondamento. O estado
implementado resolveu esses pontos na SPEC-003: SQLite local, atualização de
rendimento sob demanda, contratos HTTP próprios e `ROUND_HALF_UP`.

Complemento de escopo informado pelo aluno: haverá várias caixinhas nomeadas
por conta, com CRUD completo e seleção da caixinha no depósito. Cada lote
pertence a uma caixinha; o FIFO se aplica dentro dela. Esse detalhamento está
na SPEC-003; a política de exclusão com saldo permanece aberta.

O aluno definiu também que cada caixinha é exclusiva da conta criadora. O
vínculo é imutável e deve ser validado pelo backend em toda operação. Depósito
e saque movimentam somente essa conta. Essa regra não altera, por si só, a
limitação existente de autorização por titularidade do usuário autenticado.

## Alternativas consideradas

### Saldo único com prazo comum

- Prós: menos estado para armazenar.
- Contras: mistura depósitos de idades diferentes.
- Motivo da rejeição: não atende ao prazo individual escolhido pelo aluno.

### Resgate proporcional entre lotes

- Prós: distribui a retirada por todos os depósitos.
- Contras: exige alterar vários lotes mesmo para retiradas pequenas.
- Motivo da rejeição: não corresponde à cascata do mais antigo ao mais recente.

### Reiniciar o prazo após resgate parcial

- Prós: inicia um novo ciclo a partir da movimentação.
- Contras: descarta o tempo já cumprido pelo saldo remanescente.
- Motivo da rejeição: o aluno confirmou preservar o prazo do lote restante.

## Consequências

- Será necessário controlar lotes e períodos já remunerados, além do saldo total.
- O resgate precisa considerar rendimentos devidos mesmo se o processamento
  automático estiver atrasado; sua execução não pode determinar o valor recebido.
- Resgates precisam validar o total antes de consumir os lotes e atualizar a conta
  atomicamente com a Caixinha, seguindo a sincronização local do projeto.
- A implementação deverá definir um desempate estável para depósitos com a mesma
  data/hora e testar resgates que atravessam vários lotes.
- O mecanismo implementado é sob demanda: `proximo_rendimento_em` persiste por
  lote e avança a cada ciclo aplicado, impedindo dupla remuneração no período.

## Referências

- [SPEC-003 — Caixinha](../specs/SPEC-003-caixinha.md)
- [Roadmap da Sprint 2](../../ROADMAP_SPRINT_2.md)
- Confirmações do aluno durante a mentoria sobre juros compostos, prazo individual
  e consumo do saldo completo de cada lote em cascata.
