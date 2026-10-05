# Roadmap da Sprint 2 — ICEIBank

## Estado

Implementação concluída em 04/10/2026. O backend, frontend, testes e documentação
foram atualizados; a conexão à instância RabbitMQ real foi validada. As evidências
PNG seguem pendentes de captura manual, sem alegação de que já existem.

Fonte: `Sprint 2 - ICEIBank.pdf`, fornecido pelo aluno, seções 2 a 11.
O PDF informa entrega em 5 de outubro, às 23h59. Seu cronograma de três semanas
é uma sugestão do roteiro, não um registro do trabalho realizado.

## Objetivo

Evoluir o projeto Python/FastAPI e React existente para comunicação assíncrona
entre agências usando RabbitMQ e relógios vetoriais, preservando particionamento,
JWT, frontend e as funcionalidades existentes.

## Requisitos confirmados no roteiro

- Exchange `iceibank.eventos`, tipo `topic`, durável.
- Filas duráveis `fila-agencia-0`, `fila-agencia-1` e `fila-agencia-2`, vinculadas
  pelas routing keys `agencia.<id>.creditar`; mensagens persistentes.
- Relógio vetorial com três posições e operações local, envio e recebimento.
- Logs com `timestampVetorial` em lugar de `timestampLamport`.
- Transferência remota por publicação e consumo de mensagens; remoção da rota
  HTTP `/contas/{id}/creditar-remoto`.
- Resposta remota HTTP 200 indicando publicação, sem afirmar crédito concluído.
- Reprodução da queda e reinício do destino, incluindo falha de crédito por
  conta ausente: as contas continuam em memória.
- Mesclador identifica eventos concorrentes de agências distintas e distingue
  pares causalmente relacionados. Hora de parede serve para apresentação.
- Regressão de JWT, frontend e particionamento verificada.
- Funcionalidade adicional nova, com commit e evidência próprios; escolha do aluno
  registrada abaixo.
- Três prints obrigatórios em `evidencias/sprint2/`: `transferencia-assincrona.png`,
  `resiliencia-fila.png` e `linha-do-tempo-causal.png`, mais o print do adicional.
- `RESPOSTAS.md` recebe as questões das seções 6.4, 7.5 e 8.3, a descrição do
  adicional e declaração verdadeira do uso de IA. Observações dependem de execução real.

## Funcionalidade adicional escolhida: Caixinha

Requisito informado pelo aluno: guardar dinheiro em uma Caixinha com rendimento
de 10% do valor guardado a cada dois dias. Trata-se de uma regra da simulação
acadêmica. O aluno declarou o escopo funcional fechado. O detalhamento técnico
foi consolidado nos ADRs 006 e 008 e a implementação está disponível no backend
e frontend.

O fluxo inclui CRUD de caixinhas com nome por conta. Para guardar dinheiro,
o usuário seleciona uma caixinha e informa o valor; cada depósito gera um lote
nessa caixinha. Caixinhas com saldo não podem ser excluídas; o resgate deve ocorrer antes.
Cada caixinha é exclusiva da conta criadora, com vínculo imutável e validação
no backend em todas as operações.

Regras confirmadas na [SPEC-003 — Caixinha](docs/specs/SPEC-003-caixinha.md):
guardar reduz o saldo disponível da conta, resgatar devolve o valor à conta e
o rendimento é composto (R$ 100,00 → R$ 110,00 → R$ 121,00). Cada depósito
tem prazo próprio; resgates consomem lotes por FIFO e preservam o prazo do saldo
remanescente, conforme o [ADR-006](docs/decisions/ADR-006-caixinha-lotes-fifo.md).

As regras adotadas são ciclo de 48 horas, `ROUND_HALF_UP`, cálculo sob demanda
com relógio injetável e armazenamento somente em memória. Ver ADR-008.

## Base existente e pontos de integração

| Responsabilidade | Arquivos atuais |
|---|---|
| Composição dos serviços | `agencia/src/iceibank/main.py` |
| Configuração e partição | `agencia/src/iceibank/core/config.py` |
| Transferências | `agencia/src/iceibank/services/transferencia_service.py` |
| Mensageria | `agencia/src/iceibank/services/mensageria.py` |
| Relógio e logs | `agencia/src/iceibank/services/relogio_vetorial.py`, `registro_eventos.py` e `agencia/src/iceibank/models/evento.py` |
| Linha do tempo | `agencia/scripts/mesclar_logs.py` |
| Estado das contas | `agencia/src/iceibank/repositories/conta_repository.py` |

Manter controllers finos, regras nos serviços, armazenamento nos repositórios,
`Decimal` para dinheiro e sincronização do estado. Adaptar os exemplos Node.js
do roteiro às camadas existentes, preservando Python.

## Etapas da mentoria

Em cada etapa: aluno propõe, discutimos a solução, registramos a decisão e o
comportamento esperado, implementamos um incremento, verificamos e registramos
o resultado. Commits seguem incrementais, após revisão do diff.

| Etapa | Trabalho | Critério para concluir |
|---|---|---|
| 1 | Entender fluxo atual e definir ambiente RabbitMQ | Aluno explica produtor, exchange, fila e consumidor; acesso ao broker verificado |
| 2 | Projetar e testar relógio vetorial isoladamente | Regras local/envio/recebimento e comparação cobertas por testes |
| 3 | Integrar vetor aos eventos e serviços | Operações existentes registram vetores; regressão executada |
| 4 | Projetar e integrar mensageria | Transferência real entre agências via broker; frontend informa publicação |
| 5 | Reproduzir indisponibilidade e reinício | Evidência da fila e do crédito rejeitado por conta ausente |
| 6 | Atualizar análise causal | Par concorrente identificado e par débito/crédito não classificado como concorrente |
| 7 | Implementar Caixinha com rendimento | Regras definidas na mentoria, teste, documentação e evidência próprios |
| 8 | Consolidar entrega | Regressão, respostas, evidências e instruções reproduzíveis revisadas |

## Documentação incremental

- [SPEC-003](docs/specs/SPEC-003-caixinha.md): regra funcional, implementação e
  validação automatizada da Caixinha.
- [SPEC-004](docs/specs/SPEC-004-mensageria-e-relogio-vetorial.md): arquitetura
  da mensageria e do relógio vetorial implementada e validada no broker real.
- [ADR-007](docs/decisions/ADR-007-mensageria-rabbitmq-e-relogio-vetorial.md):
  decisões, alternativas e consequências da mensageria.
- Preservar os documentos da Sprint 1 como histórico, indicando a evolução
  nos novos documentos e atualizando os índices.
- Distinguir planejado, implementado e validado. Não reutilizar números de
  testes antigos como comprovação da Sprint 2.

## Pendências externas

- Capturar os quatro PNGs reais exigidos em `evidencias/sprint2/`.
- Revisar visualmente o frontend com a execução das três agências aberta.

## Registro de acompanhamento

| Data | Avanço | Verificação | Próximo passo |
|---|---|---|---|
| 28/09/2026 | Leitura do roteiro e inspeção da arquitetura; roadmap inicial | Comparação documental com configuração, repositório de contas e serviços; testes não executados | Aluno propor como o fluxo remoto muda com a fila |
| 28/09/2026 | Instância CloudAMQP RabbitMQ criada no plano Little Lemur | Confirmação do aluno; acesso ao Manager e conexão da aplicação pendentes | Abrir RabbitMQ Manager e identificar painel de exchanges/filas |
| 04/10/2026 | Relógio vetorial, RabbitMQ, mesclador causal e Caixinha implementados | 41 testes, lint backend/frontend, build e RabbitMQ real aprovados | Capturar evidências PNG reais |

## Referências

- [Documentação](docs/README.md)
- [Guia de desenvolvimento](docs/GUIA_DE_DESENVOLVIMENTO.md)
- [Índice de ADRs](docs/decisions/README.md)
- [Arquitetura da Sprint 1](docs/specs/SPEC-001-arquitetura-sprint-1.md)
