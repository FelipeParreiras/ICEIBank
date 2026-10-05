# ADR-010: Persistência SQLite local por agência

## Status

Aceito e implementado em 05/10/2026.

## Contexto

Contas, usuários cadastrados, planejamentos mensais, gastos e Caixinhas eram
mantidos apenas em memória. Reiniciar um processo apagava o estado operacional
da agência, impedindo continuidade de demonstrações e tornando incoerentes os
históricos de investimento e de gastos.

O projeto continua sendo uma aplicação acadêmica distribuída em três processos,
com partição de contas por `id % 3`, RabbitMQ para transferências remotas e JSONL
para auditoria de eventos. A persistência não deve transformar os arquivos de
log em fonte de verdade nem criar uma falsa transação distribuída entre agências.

## Decisão

Cada processo de agência usa um arquivo SQLite próprio em
`agencia/data/iceibank-agencia-{AGENCIA_ID}.sqlite3`. O objeto
`SQLiteDatabase` é compartilhado pelos repositórios de contas, usuários,
controle financeiro e Caixinhas da mesma agência.

Os repositórios permanecem como fronteira de infraestrutura; serviços e
controladores continuam dependentes de suas interfaces atuais. As tabelas são
criadas de forma idempotente no início da aplicação e armazenam:

- contas e usuários cadastrados;
- planejamento mensal e gastos;
- Caixinhas, ordem, cor, lotes e movimentos.

Operações que mudam conta e Caixinha, ou conta e gasto, compartilham uma única
transação SQLite local. Os arquivos JSONL continuam sendo trilha de auditoria,
não banco transacional. Os arquivos SQLite e seus artefatos WAL/SHM não entram
no Git.

## Alternativas consideradas

### Continuar somente em memória

- Prós: nenhuma infraestrutura adicional.
- Contras: perda integral do estado ao reiniciar e nenhuma continuidade de
  histórico financeiro.
- Rejeitada: não atende à necessidade atual de persistir as operações locais.

### Um banco central compartilhado entre agências

- Prós: visão única dos dados e possibilidade de consistência centralizada.
- Contras: altera a separação por agência, aumenta o escopo operacional e não
  representa a arquitetura distribuída pedida na disciplina.
- Rejeitada: as partições locais permanecem explícitas nesta etapa.

### PostgreSQL ou outro SGBD servidor

- Prós: concorrência e operação multi-processo mais robustas.
- Contras: requer serviço externo, credenciais, provisionamento e migrações
  mais elaboradas para o ambiente acadêmico atual.
- Adiada: SQLite é suficiente para uma instância por agência e um worker.

## Consequências

- Reiniciar uma agência preserva os dados do seu arquivo SQLite local.
- Cada agência continua isolada: não há replicação de banco nem transação
  atômica entre a origem e o destino de uma transferência remota.
- A aplicação deve continuar com um único worker por agência; SQLite não é a
  solução de escalabilidade horizontal do projeto.
- Para reiniciar a massa de demonstração, o operador deve parar a agência e
  remover conscientemente apenas o arquivo SQLite daquela agência, se desejar.
- Não há criptografia em repouso nem migrações versionadas nesta fase; dados
  reais e segredos continuam fora do escopo acadêmico.

## Referências

- [Estado atual do projeto](../ESTADO_ATUAL_DO_PROJETO.md)
- [Configuração e execução](../CONFIGURACAO_E_EXECUCAO.md)
- [SPEC-002 — Controle Financeiro](../specs/SPEC-002-controle-financeiro-mensal.md)
- [SPEC-003 — Caixinha](../specs/SPEC-003-caixinha.md)
