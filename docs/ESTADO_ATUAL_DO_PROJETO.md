# Estado atual do ICEIBank

## Status

Referência técnica do estado implementado em 05/10/2026. As Sprints 1 e 2
estão implementadas. O backend possui 43 testes automatizados aprovados; o
frontend passa em lint e no build de produção. Capturas e vídeo de entrega são
atividades separadas e devem ser feitos com dados fictícios.

## Visão do sistema

O ICEIBank é um projeto acadêmico de banco distribuído com três processos de
agência independentes. Cada conta pertence à agência calculada por
`idConta % 3`; portanto, as contas `0, 3, 6` pertencem à agência 0, `1, 4, 7`
à agência 1 e `2, 5, 8` à agência 2.

| Processo | Porta | Responsabilidade |
|---|---:|---|
| Agência 0 | 4045 | partição das contas de resto 0; autoridade de usuários |
| Agência 1 | 4046 | partição das contas de resto 1 |
| Agência 2 | 4047 | partição das contas de resto 2 |
| React/Vite | 5173 | interface e proxy `/api/agencia-{0,1,2}` |

O proxy do Vite mantém as portas exigidas e evita o bloqueio do Chrome à porta
4045. Cada agência deve executar com um único worker, pois seu estado é local
ao processo.

## Funcionalidades disponíveis

### Acesso e contas

- cadastro e login de usuário com JWT; cadastro e login são centralizados na
  agência 0, e as demais encaminham a solicitação;
- logout e limpeza da sessão em resposta HTTP 401;
- criação, listagem e consulta de contas na agência responsável;
- depósito e saque com validação monetária, saldo suficiente e eventos;
- transferência local atômica entre contas da mesma agência;
- transferência entre agências publicada no RabbitMQ e recebida de modo
  assíncrono pela fila da agência de destino.

### Mensageria e observabilidade

- exchange topic durável `iceibank.eventos`;
- uma fila durável `fila-agencia-{id}` por agência, ligada à chave
  `agencia.{id}.creditar`;
- publisher confirms antes de responder sucesso ao envio remoto;
- relógio vetorial de três posições em todos os eventos atuais;
- JSON Lines em `agencia/data/eventos-agencia-{id}.jsonl`, sem segredos;
- comparação causal de eventos no script de mesclagem de logs.

O sucesso de uma transferência entre agências confirma a publicação no broker,
não o crédito já efetivado no destino. Sem `RABBITMQ_URL`, as agências continuam
úteis para desenvolvimento local, mas transferências entre agências retornam
`503 MENSAGERIA_INDISPONIVEL`.

### Reserva financeira: Caixinhas

- criação de várias Caixinhas por conta, com nome único sem diferenciar
  maiúsculas e minúsculas;
- cartões em formato de caixa, com cor inicial verde e paleta controlada
  (`caramelo`, `verde`, `azul`, `roxo`, `coral`);
- modal de detalhes com saldo, rendimento acumulado, operações e histórico;
- depósito debita a conta e cria um lote; saque aplica rendimento vencido,
  consome lotes por FIFO e credita a conta;
- rendimento composto de 10% a cada 48 horas por lote, arredondado em centavos;
- gerenciamento de nome, cor e exclusão; excluir resgata automaticamente todo
  o saldo para a conta;
- modo de organização com arrastar/soltar e botões de seta; a ordem é validada
  pelo backend e armazenada como `ordem` por Caixinha.

### Controle financeiro mensal

- um planejamento por conta e competência `AAAA-MM`;
- renda prevista, meta de economia, limite mensal de gasto e limites opcionais
  por categoria;
- tipos de gastos gerenciáveis: adicionar, remover, marcar como flexível e
  reordenar por prioridade;
- gasto só pode usar categoria configurada no planejamento; seu registro debita
  o saldo da conta na mesma operação local;
- resumo com total gasto, economia projetada, valor de ajuste, totais por
  categoria, histórico e recomendações determinísticas;
- em empates financeiros, as recomendações preservam categorias de maior
  prioridade e sugerem primeiro a redução nas menos importantes.

### Interface React

- conta carregada automaticamente para a agência selecionada; a tela de criação
  é exibida apenas quando a agência não tem conta;
- abas independentes para Movimentações, Reserva financeira e Controle
  financeiro;
- formulário único para depósito ou saque, com seletor de tipo;
- notificações de sucesso, aviso e erro via React Toastify;
- modais de Caixinha com fundo escurecido, navegação de retorno entre detalhes
  e gerenciamento e dimensões padronizadas;
- barra superior sticky, layout vertical e regras responsivas para telas
  estreitas;
- identidade visual baseada em verdes pastéis e dourado para destaques. A
  proposta de paleta está em `paleta-iceibank.html` na visualização da conversa;
  a adoção dos tokens completos ainda é uma evolução de interface.

## Contratos HTTP principais

Todas as rotas de conta, transferência, Caixinha e controle financeiro exigem
`Authorization: Bearer <JWT>`. As rotas de autenticação são públicas.

| Grupo | Operações |
|---|---|
| Autenticação | `POST /auth/cadastro`, `POST /auth/login` |
| Contas | `POST/GET /contas`, `GET /contas/{id}`, `POST /contas/{id}/depositar`, `POST /contas/{id}/sacar` |
| Transferências | `POST /transferencias` |
| Caixinhas | `POST/GET /contas/{id}/caixinhas`, `PUT /contas/{id}/caixinhas/ordem`, `GET/PATCH/DELETE /contas/{id}/caixinhas/{caixinhaId}`, `POST .../guardar`, `POST .../resgatar` |
| Financeiro | `PUT /contas/{id}/controle-financeiro/{competencia}/planejamento`, `POST /contas/{id}/controle-financeiro/gastos`, `GET /contas/{id}/controle-financeiro/{competencia}` |

Os detalhes de corpos, respostas e erros estão em [API Sprint 1](API_SPRINT_1.md)
e [API Sprint 2](API_SPRINT_2.md).

## Persistência e limites conhecidos

- contas, usuários cadastrados, planejamentos, gastos, Caixinhas, ordem,
  lotes e histórico persistem no SQLite local da agência, em
  `agencia/data/iceibank-agencia-{AGENCIA_ID}.sqlite3`;
- os arquivos JSONL são logs locais de auditoria, não a base transacional;
- cada agência mantém seu próprio arquivo SQLite: não há replicação,
  autorização por titularidade, idempotência de mensagens ou confirmação
  reversa do crédito remoto;
- transferências assíncronas não fornecem consistência distribuída atômica;
- o sistema é didático e não deve receber dados financeiros reais.

O SQLite é a fonte de verdade local para o estado operacional; as operações que
alteram conta e gasto, ou conta e Caixinha, usam a mesma transação local.
Migrações versionadas, criptografia em repouso e backup automático continuam
fora do escopo acadêmico atual.

## Fontes de verdade por assunto

- [SPEC-003 — Caixinha](specs/SPEC-003-caixinha.md)
- [SPEC-004 — Mensageria e relógio vetorial](specs/SPEC-004-mensageria-e-relogio-vetorial.md)
- [SPEC-002 — Controle financeiro mensal](specs/SPEC-002-controle-financeiro-mensal.md)
- [Configuração da Sprint 2](CONFIGURACAO_SPRINT_2.md)
- [Segurança](SEGURANCA.md)
- [Plano de testes e evidências](PLANO_DE_TESTES_E_EVIDENCIAS.md)
