# ADR-002: Health-check como funcionalidade adicional

## Status

Substituído por ADR-004. Revisado em 11/10/2026 como registro histórico.

## Data

2026-09-07

## Contexto

O roteiro exige pelo menos uma funcionalidade adicional em cada sprint. Ela precisa adicionar comportamento observável, ter evidência, documentação e commit próprio. Autenticação, frontend, refatoração e testes isoladamente não contam como extra.

A Sprint 1 já possui risco de prazo por combinar backend, comunicação distribuída, JWT e frontend. A funcionalidade escolhida deve ser útil sem disputar esforço com os itens de maior pontuação.

## Decisão

Implementar `GET /health` por agência, protegido por JWT, retornando:

- status da instância;
- ID e porta da agência;
- valor atual do relógio de Lamport;
- quantidade de contas sob responsabilidade da instância;
- tempo de atividade.

O frontend mostrará o resultado da agência selecionada. A entrega terá `evidencias/sprint1/funcionalidade-adicional.png` e commit exclusivo.

## Alternativas consideradas

### Histórico de transações por conta

- Prós: valor funcional maior e forte ligação com os eventos.
- Contras: exige definir a relação entre logs persistidos e contas que são apenas mantidas em memória.
- Motivo da rejeição: aumenta a complexidade de consistência nesta sprint.

### Limite de saque ou transferência

- Prós: implementação pequena e regra de negócio clara.
- Contras: oferece menos apoio para operar e demonstrar as três instâncias.
- Motivo da rejeição: o health-check reforça melhor o conceito de processos independentes.

### Idempotência de transferências

- Prós: prepara o sistema para repetição de mensagens e falhas.
- Contras: exige armazenamento de IDs processados e mais decisões sobre ciclo de vida do estado.
- Motivo da rejeição: é valiosa, mas arriscaria o cronograma da Sprint 1.

## Consequências

- A funcionalidade é simples de testar e demonstrar.
- O endpoint facilita verificar agência, partição e relógio durante o desenvolvimento.
- O retorno não deve expor contas, credenciais ou segredos.
- A leitura do contador precisa ser sincronizada e não deve incrementá-lo.
- A proposta não foi implementada e foi substituída quando o aluno escolheu um sistema de controle financeiro mensal como funcionalidade adicional.

## Referências

- [SPEC-001](../specs/SPEC-001-arquitetura-sprint-1.md)
- [ADR-004](ADR-004-controle-financeiro-mensal.md)
- Seção 2.1 do roteiro da Sprint 1.

