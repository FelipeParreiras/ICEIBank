# Plano de commits — Sprint 1

## Status

Planejado. **Nenhum comando de staging ou commit foi executado ao criar este documento.**

## Objetivo

Definir antecipadamente como o trabalho será dividido em commits incrementais, quais arquivos pertencem a cada intenção e quais verificações precisam passar antes de o aluno criar o commit.

O plano segue o roteiro acadêmico, mantém a funcionalidade adicional isolada e evita um único commit grande ao final da sprint.

## Legenda

- **Novo:** arquivo criado nesse marco.
- **Modificado:** arquivo criado anteriormente e evoluído nesse marco.
- **Evidência:** arquivo produzido por teste real; nunca deve ser criado antes da execução.
- **Condicional:** depende da confirmação de uma decisão ou de uma divergência encontrada durante a implementação.

Um mesmo arquivo pode aparecer em vários commits. Isso significa que ele evolui junto das funcionalidades, não que sua versão final deva ser antecipada no primeiro commit.

## Regras gerais

1. Não executar `git add .`.
2. Selecionar apenas os arquivos listados para a intenção atual.
3. Revisar `git diff -- <arquivo>` antes de colocar em staging.
4. Confirmar com `git diff --cached` exatamente o que entrará no commit.
5. Não misturar correções ou documentação sem relação com a intenção.
6. Testes da funcionalidade entram no mesmo commit do código correspondente.
7. Evidências entram no commit da parte demonstrada.
8. `RESPOSTAS.md` é atualizado junto da parte que gerou a observação.
9. O extra tem commit próprio.
10. Nunca versionar `.env`, `.venv`, `node_modules`, logs JSONL ou segredos.

## Visão resumida

| Ordem | Mensagem prevista | Entrega principal |
|---:|---|---|
| 00 | `docs(sprint1): define planejamento e arquitetura do ICEIBank` | pacote documental inicial |
| 01 | `chore(backend): cria estrutura inicial da agencia FastAPI` | projeto Python executável mínimo |
| 02 | `feat(config): define particionamento de contas entre 3 agencias` | configuração e offset 45 |
| 03 | `feat(lamport): implementa relogio logico e registro de eventos` | Lamport e JSONL |
| 04 | `feat(contas): implementa API REST/MVC de contas` | criar, consultar, depositar e sacar |
| 05 | `feat(transferencias): implementa transferencias locais e entre agencias` | comunicação REST e falha conhecida |
| 06 | `feat(observabilidade): adiciona linha do tempo unificada` | mesclador dos logs |
| 07 | `feat(auth): protege a API com autenticacao JWT` | login, JWT e token interno |
| 08 | `chore(frontend): cria aplicacao React com Vite` | base do frontend |
| 09 | `feat(frontend): implementa login e selecao de agencia` | sessão e cliente HTTP |
| 10 | `feat(frontend): implementa operacoes bancarias` | dashboard e erros visíveis |
| 11 | `feat(extra): adiciona controle financeiro mensal` | funcionalidade adicional isolada |
| 12 | `docs(sprint1): finaliza respostas e validacao da entrega` | auditoria, estados e instruções finais |

O commit 11 implementa o Controle Financeiro Mensal escolhido pelo aluno. Seu escopo deve permanecer limitado à SPEC-002.

## Commit 00 — Planejamento e arquitetura

### Mensagem

```text
docs(sprint1): define planejamento e arquitetura do ICEIBank
```

### Objetivo

Registrar o contexto conhecido antes do código, sem alegar que requisitos já foram implementados ou validados.

### Arquivos

**Modificado:**

- `README.md`

**Novos:**

- `ROADMAP_SPRINT_1.md`
- `RESPOSTAS.md`
- `docs/README.md`
- `docs/API_SPRINT_1.md`
- `docs/BACKEND_FASTAPI.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/ENTREGA_E_VIDEO.md`
- `docs/FRONTEND_REACT.md`
- `docs/GLOSSARIO.md`
- `docs/GUIA_DE_DESENVOLVIMENTO.md`
- `docs/LAMPORT_E_OBSERVABILIDADE.md`
- `docs/PLANO_DE_COMMITS_SPRINT_1.md`
- `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`
- `docs/SEGURANCA.md`
- `docs/decisions/README.md`
- `docs/decisions/ADR-001-stack-python-fastapi-react.md`
- `docs/decisions/ADR-002-funcionalidade-adicional-health-check.md`
- `docs/decisions/ADR-003-autenticacao-e-comunicacao-interna.md`
- `docs/decisions/ADR-004-controle-financeiro-mensal.md`
- `docs/specs/SPEC-001-arquitetura-sprint-1.md`
- `docs/specs/SPEC-002-controle-financeiro-mensal.md`
- `evidencias/sprint1/README.md`

### Não incluir

- qualquer PNG ainda não produzido;
- arquivos vazios que fingem uma implementação;
- código FastAPI ou React incompleto sem relação com a documentação.

### Verificação antes do commit

- links Markdown locais válidos;
- ADR-001 aceito e ADRs 002/003 com estado correto;
- documentos indicam que o código ainda não existe;
- nenhuma resposta empírica preenchida sem teste.

## Commit 01 — Estrutura inicial do backend

### Mensagem

```text
chore(backend): cria estrutura inicial da agencia FastAPI
```

### Objetivo

Criar um projeto Python instalável e uma aplicação FastAPI mínima que inicia sem implementar ainda regras de conta.

### Arquivos

**Novos:**

- `.gitignore`
- `agencia/pyproject.toml`
- `agencia/.env.example`
- `agencia/data/.gitkeep`
- `agencia/src/iceibank/__init__.py`
- `agencia/src/iceibank/main.py`
- `agencia/src/iceibank/api/__init__.py`
- `agencia/src/iceibank/api/router.py`
- `agencia/src/iceibank/controllers/__init__.py`
- `agencia/src/iceibank/core/__init__.py`
- `agencia/src/iceibank/models/__init__.py`
- `agencia/src/iceibank/repositories/__init__.py`
- `agencia/src/iceibank/schemas/__init__.py`
- `agencia/src/iceibank/schemas/base.py`
- `agencia/src/iceibank/services/__init__.py`
- `agencia/tests/conftest.py`

**Modificados:**

- `README.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

### Conteúdo esperado

- dependências diretas e de desenvolvimento declaradas;
- endpoint técnico mínimo somente se necessário para confirmar inicialização, sem contar como extra;
- aplicação cria e agrega o router;
- `.gitignore` cobre Python, React, `.env` e JSONL;
- README possui comandos realmente testados.

### Verificação antes do commit

- instalação em ambiente virtual limpo;
- importação de `iceibank.main:app` funciona;
- servidor inicia com um worker;
- suíte vazia/configuração de pytest não falha;
- `.env` e `.venv` não aparecem no status.

## Commit 02 — Configuração e particionamento

### Mensagem

```text
feat(config): define particionamento de contas entre 3 agencias
```

### Objetivo

Configurar `AGENCIA_ID`, offset 45, portas 4045–4047 e a função responsável por localizar a agência de uma conta.

### Arquivos

**Novos:**

- `agencia/src/iceibank/core/config.py`
- `agencia/tests/unit/__init__.py`
- `agencia/tests/unit/test_config.py`

**Modificados:**

- `agencia/.env.example`
- `agencia/src/iceibank/main.py`
- `README.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

### Conteúdo esperado

- `NUMERO_AGENCIAS=3`;
- `PORTA_BASE=4045`;
- validação de IDs de agência 0, 1 e 2;
- URLs calculadas de forma centralizada;
- `agencia_responsavel(id_conta) = id_conta % 3`;
- rejeição de ID de conta negativo.

### Verificação antes do commit

- testes dos IDs 0–11;
- configuração inválida impede inicialização;
- cada processo informa identidade e porta corretas;
- nenhum segredo real no `.env.example`.

## Commit 03 — Relógio de Lamport e eventos

### Mensagem

```text
feat(lamport): implementa relogio logico e registro de eventos
```

### Objetivo

Implementar e validar isoladamente as três regras de Lamport e o registro append-only por agência.

### Arquivos

**Novos:**

- `agencia/src/iceibank/models/evento.py`
- `agencia/src/iceibank/services/relogio_lamport.py`
- `agencia/src/iceibank/services/registro_eventos.py`
- `agencia/tests/unit/test_relogio_lamport.py`
- `agencia/tests/unit/test_registro_eventos.py`

**Modificados:**

- `agencia/src/iceibank/main.py`
- `agencia/tests/conftest.py`
- `RESPOSTAS.md`
- `docs/LAMPORT_E_OBSERVABILIDADE.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

### Conteúdo esperado

- `evento_local`, `ao_enviar`, `ao_receber` e leitura atual;
- lock único para o contador;
- arquivo `eventos-agencia-{id}.jsonl`;
- hora UTC e detalhes serializáveis;
- diretório de log substituível em testes;
- respostas da Parte B revisadas a partir dos testes.

### Verificação antes do commit

- local 10 recebendo 3 resulta em 11;
- local 10 recebendo 20 resulta em 21;
- chamadas concorrentes não repetem timestamps locais;
- cada linha produz JSON válido;
- arquivos reais em `agencia/data/*.jsonl` continuam ignorados.

## Commit 04 — API de contas

### Mensagem

```text
feat(contas): implementa API REST/MVC de contas
```

### Objetivo

Entregar criação, consulta, depósito e saque com separação clara de responsabilidades e eventos Lamport.

### Arquivos

**Novos:**

- `agencia/src/iceibank/core/exceptions.py`
- `agencia/src/iceibank/core/money.py`
- `agencia/src/iceibank/models/conta.py`
- `agencia/src/iceibank/schemas/conta.py`
- `agencia/src/iceibank/repositories/conta_repository.py`
- `agencia/src/iceibank/services/conta_service.py`
- `agencia/src/iceibank/controllers/contas_controller.py`
- `agencia/src/iceibank/api/dependencies.py`
- `agencia/tests/integration/test_auth_e_contas.py`

**Modificados:**

- `agencia/src/iceibank/api/router.py`
- `agencia/src/iceibank/main.py`
- `agencia/tests/conftest.py`
- `docs/API_SPRINT_1.md`
- `docs/BACKEND_FASTAPI.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

### Conteúdo esperado

- `POST /contas`;
- `GET /contas/{id}`;
- `POST /contas/{id}/depositar`;
- `POST /contas/{id}/sacar`;
- valores internos em `Decimal`;
- validações de partição, duplicidade, existência, valor e saldo;
- erros padronizados;
- controller delegando ao serviço.

### Verificação antes do commit

- fluxo criar → consultar → depositar → sacar;
- agência errada recusa sem alterar estado;
- valor inválido e saldo insuficiente preservam saldo;
- todas as mutações geram evento;
- testes unitários e de integração passam.

## Commit 05 — Transferências

### Mensagem

```text
feat(transferencias): implementa transferencias locais e entre agencias
```

### Objetivo

Implementar transferência local atômica, comunicação REST direta, propagação de Lamport e a limitação remota intencional.

### Arquivos

**Novos:**

- `agencia/src/iceibank/schemas/transferencia.py`
- `agencia/src/iceibank/services/agencia_client.py`
- `agencia/src/iceibank/services/transferencia_service.py`
- `agencia/src/iceibank/controllers/transferencias_controller.py`
- `agencia/tests/integration/test_transferencias.py`

**Modificados:**

- `agencia/pyproject.toml`
- `agencia/src/iceibank/api/dependencies.py`
- `agencia/src/iceibank/api/router.py`
- `agencia/src/iceibank/main.py`
- `agencia/tests/conftest.py`
- `RESPOSTAS.md`
- `docs/API_SPRINT_1.md`
- `docs/BACKEND_FASTAPI.md`
- `docs/LAMPORT_E_OBSERVABILIDADE.md`
- `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

**Evidências:**

- `evidencias/sprint1/transferencia-local.png`
- `evidencias/sprint1/transferencia-entre-agencias.png`
- `evidencias/sprint1/falha-conhecida.png`

### Conteúdo esperado

- `POST /transferencias`;
- `POST /contas/{id}/creditar-remoto` inicialmente funcional;
- transferência local valida as duas contas antes da mutação;
- transferência remota debita, envia Lamport e credita o destino;
- timeout/falha gera 502 e `TRANSFERENCIA_FALHOU`;
- nenhum rollback remoto.

### Verificação antes do commit

- conta 0 → 3 preserva a soma local;
- conta 0 → 1 atualiza os dois processos;
- timestamp no destino é maior que o recebido;
- Agência 2 desligada causa 502 e mantém o débito;
- três PNGs são reais, legíveis e não expõem segredos;
- respostas da Parte D citam os valores observados.

## Commit 06 — Linha do tempo unificada

### Mensagem

```text
feat(observabilidade): adiciona linha do tempo unificada
```

### Objetivo

Unir os JSONL das três agências e documentar a observação de causalidade/concorrência.

### Arquivos

**Novos:**

- `agencia/scripts/mesclar_logs.py`
- `agencia/tests/unit/test_mesclar_logs.py`

**Modificados:**

- `RESPOSTAS.md`
- `README.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/LAMPORT_E_OBSERVABILIDADE.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

**Evidência:**

- `evidencias/sprint1/linha-do-tempo.png`

### Conteúdo esperado

- leitura de todos os `*.jsonl`;
- erro útil para linha inválida;
- ordenação primária por Lamport;
- desempate apenas visual;
- saída com hora de parede, agência, tipo e detalhes;
- observação real registrada na Parte E.

### Verificação antes do commit

- script funciona com zero, um e três arquivos;
- linhas vazias são ignoradas;
- saída contém eventos das três agências;
- empate/concorrência é explicado sem inferir causalidade indevida;
- print inclui a saída solicitada e `Get-Date`.

## Commit 07 — JWT e comunicação interna protegida

### Mensagem

```text
feat(auth): protege a API com autenticacao JWT
```

### Objetivo

Adicionar login, expiração, proteção das rotas e identidade interna sem quebrar a transferência remota.

### Arquivos

**Novos:**

- `agencia/src/iceibank/core/security.py`
- `agencia/src/iceibank/schemas/auth.py`
- `agencia/src/iceibank/services/auth_service.py`
- `agencia/src/iceibank/controllers/auth_controller.py`

**Modificados:**

- `agencia/pyproject.toml`
- `agencia/.env.example`
- `agencia/src/iceibank/api/dependencies.py`
- `agencia/src/iceibank/api/router.py`
- `agencia/src/iceibank/main.py`
- `agencia/src/iceibank/services/agencia_client.py`
- `agencia/src/iceibank/controllers/contas_controller.py`
- `agencia/src/iceibank/controllers/transferencias_controller.py`
- `agencia/tests/conftest.py`
- `agencia/tests/integration/test_auth_e_contas.py`
- `agencia/tests/integration/test_transferencias.py`
- `RESPOSTAS.md`
- `docs/API_SPRINT_1.md`
- `docs/SEGURANCA.md`
- `docs/decisions/ADR-003-autenticacao-e-comunicacao-interna.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

**Evidências:**

- `evidencias/sprint1/auth-sem-token.png`
- `evidencias/sprint1/auth-com-token.png`
- `evidencias/sprint1/auth-token-expirado.png`

### Conteúdo esperado

- `POST /auth/login`;
- senha comparada por hash;
- JWT com `sub`, `iat`, `exp` e `iss`;
- 401 para ausência, invalidade e expiração;
- token interno no cliente e na rota remota;
- CORS configurado para o React;
- ADR-003 atualizado para Aceito se a decisão for confirmada.

### Verificação antes do commit

- três cenários JWT obrigatórios;
- credenciais inválidas não revelam o campo incorreto;
- token interno ausente/incorreto bloqueia crédito;
- transferência remota autenticada continua funcionando;
- nenhum segredo aparece no Git, log ou PNG;
- respostas da Parte F correspondem ao código real.

## Commit 08 — Estrutura inicial do React

### Mensagem

```text
chore(frontend): cria aplicacao React com Vite
```

### Objetivo

Criar a base React/Vite limpa antes das funcionalidades de autenticação e banco.

### Arquivos

**Novos:**

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/.env.example`
- `frontend/eslint.config.js`
- `frontend/index.html`
- `frontend/vite.config.js`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/styles/global.css`
- `docs/decisions/ADR-005-proxy-vite-para-portas-das-agencias.md`

**Modificados:**

- `.gitignore`
- `README.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/FRONTEND_REACT.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

### Conteúdo esperado

- projeto sem arquivos demonstrativos desnecessários do template;
- três URLs de agência configuráveis;
- aplicação mínima renderiza;
- scripts de desenvolvimento, lint e build;
- lockfile versionado.

### Verificação antes do commit

- `npm install` reproduz dependências;
- `npm run dev` inicia em 5173;
- `npm run lint` passa;
- `npm run build` passa;
- `node_modules` e `.env` estão ignorados.

## Commit 09 — Login e seleção de agência no React

### Mensagem

```text
feat(frontend): implementa login e selecao de agencia
```

### Objetivo

Implementar sessão JWT, cliente HTTP central e escolha controlada da agência de entrada.

### Arquivos

**Novos:**

- `frontend/src/api/cliente.js`
- `frontend/src/api/erros.js`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/context/AgenciaContext.jsx`
- `frontend/src/hooks/useAuth.js`
- `frontend/src/hooks/useAgencia.js`
- `frontend/src/components/AgenciaSelector.jsx`
- `frontend/src/components/AlertMessage.jsx`
- `frontend/src/pages/LoginPage.jsx`

**Modificados:**

- `frontend/src/App.jsx`
- `frontend/src/styles/global.css`
- `docs/FRONTEND_REACT.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

**Evidência:**

- `evidencias/sprint1/frontend-login.png`

### Conteúdo esperado

- formulário de login;
- JWT armazenado conforme decisão documentada;
- cliente injeta `Authorization`;
- 401 limpa sessão e retorna ao login;
- seletor limitado às agências 0–2;
- mensagens visíveis e estados de carregamento.

### Verificação antes do commit

- login válido/inválido;
- recarregar página com sessão;
- logout;
- token expirado volta ao login com aviso;
- troca de agência usa somente URLs configuradas;
- lint/build passam;
- print não revela JWT.

## Commit 10 — Operações bancárias no React

### Mensagem

```text
feat(frontend): implementa operacoes bancarias
```

### Objetivo

Completar consulta, depósito, saque, transferência e tratamento visual dos erros obrigatórios.

### Arquivos

**Novos:**

- `frontend/src/components/ContaCard.jsx`
- `frontend/src/components/DepositoForm.jsx`
- `frontend/src/components/SaqueForm.jsx`
- `frontend/src/components/TransferenciaForm.jsx`
- `frontend/src/pages/DashboardPage.jsx`

**Modificados:**

- `frontend/src/App.jsx`
- `frontend/src/api/cliente.js`
- `frontend/src/styles/global.css`
- `RESPOSTAS.md`
- `docs/FRONTEND_REACT.md`
- `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`

**Evidências:**

- `evidencias/sprint1/frontend-transferencia.png`
- `evidencias/sprint1/frontend-erro.png`

### Conteúdo esperado

- consulta de conta/saldo;
- depósito e saque;
- transferência com contrato único;
- resultado local/remoto visível;
- erro de saldo, conta, JWT, rede e 502 visível;
- atualização do saldo depois do sucesso;
- mapeamento MVC descrito com nomes reais.

### Verificação antes do commit

- fluxo completo exclusivamente pela interface;
- transferência 0 → 3 e 0 → 1;
- saque acima do saldo;
- agência indisponível;
- token expirando durante operação;
- lint/build passam;
- Parte G atualizada com comportamento observado.

## Commit 11 — Funcionalidade adicional

### Mensagem

```text
feat(extra): adiciona controle financeiro mensal
```

### Objetivo

Permitir definir meta de economia mensal, registrar gastos categorizados e recomendar reduções transparentes, mantendo toda a funcionalidade adicional isolada.

### Arquivos

**Novos:**

- `agencia/src/iceibank/models/gasto.py`
- `agencia/src/iceibank/models/planejamento_financeiro.py`
- `agencia/src/iceibank/schemas/controle_financeiro.py`
- `agencia/src/iceibank/repositories/controle_financeiro_repository.py`
- `agencia/src/iceibank/services/controle_financeiro_service.py`
- `agencia/src/iceibank/services/recomendacao_economia_service.py`
- `agencia/src/iceibank/controllers/controle_financeiro_controller.py`
- `agencia/tests/unit/test_recomendacao_economia.py`
- `agencia/tests/integration/test_controle_financeiro.py`
- `frontend/src/components/PlanejamentoMensalForm.jsx`
- `frontend/src/components/GastoForm.jsx`
- `frontend/src/components/ResumoFinanceiro.jsx`
- `frontend/src/components/RecomendacoesEconomia.jsx`
- `frontend/src/components/GastosDoMesList.jsx`

**Modificados:**

- `agencia/src/iceibank/api/dependencies.py`
- `agencia/src/iceibank/api/router.py`
- `agencia/src/iceibank/main.py`
- `agencia/src/iceibank/repositories/conta_repository.py`
- `frontend/src/api/cliente.js`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/styles/global.css`
- `RESPOSTAS.md`
- `docs/API_SPRINT_1.md`
- `docs/FRONTEND_REACT.md`
- `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`
- `docs/decisions/ADR-004-controle-financeiro-mensal.md`
- `docs/specs/SPEC-001-arquitetura-sprint-1.md`
- `docs/specs/SPEC-002-controle-financeiro-mensal.md`

**Evidência:**

- `evidencias/sprint1/funcionalidade-adicional.png`

### Conteúdo esperado

- planejamento por conta e competência, protegido por JWT;
- renda prevista, meta de economia, limites e categorias flexíveis;
- registro de gasto categorizado;
- débito do gasto no saldo, conforme semântica implementada;
- cálculo de total, economia projetada e ajuste necessário;
- recomendações determinísticas por categoria;
- eventos Lamport de planejamento e gasto;
- interface React completa do controle financeiro;
- ADR-004 aceito e descrição final em `RESPOSTAS.md`.

### Verificação antes do commit

- renda 500 e meta 100 geram limite de gasto 400;
- gastos de 450 geram economia projetada 50 e ajuste necessário 50;
- recomendação reduz 40 em Delivery e 10 em Lazer;
- categorias não flexíveis nunca recebem recomendação;
- gasto sem planejamento e gasto acima do saldo são rejeitados;
- gasto e débito são atômicos, se essa semântica for confirmada;
- consulta de resumo não incrementa Lamport;
- ausência de JWT retorna 401;
- PNG, testes, documentação e código pertencem ao mesmo extra.

## Commit 12 — Fechamento documental e validação

### Mensagem

```text
docs(sprint1): finaliza respostas e validacao da entrega
```

### Objetivo

Registrar apenas resultados finais reais, fechar os marcadores pendentes e garantir que outra pessoa consegue reproduzir a sprint.

### Arquivo novo previsto

- `docs/RELATORIO_DE_VALIDACAO_SPRINT_1.md`

### Arquivos modificados previstos

- `README.md`
- `ROADMAP_SPRINT_1.md`
- `RESPOSTAS.md`
- `docs/README.md`
- `docs/API_SPRINT_1.md`
- `docs/BACKEND_FASTAPI.md`
- `docs/CONFIGURACAO_E_EXECUCAO.md`
- `docs/ENTREGA_E_VIDEO.md`
- `docs/FRONTEND_REACT.md`
- `docs/PLANO_DE_COMMITS_SPRINT_1.md`
- `docs/PLANO_DE_TESTES_E_EVIDENCIAS.md`
- `docs/REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md`
- `docs/SEGURANCA.md`
- `docs/decisions/README.md`
- `docs/decisions/ADR-002-funcionalidade-adicional-health-check.md`
- `docs/decisions/ADR-003-autenticacao-e-comunicacao-interna.md`
- `docs/decisions/ADR-004-controle-financeiro-mensal.md`
- `docs/specs/SPEC-001-arquitetura-sprint-1.md`
- `docs/specs/SPEC-002-controle-financeiro-mensal.md`
- `evidencias/sprint1/README.md`

Só incluir arquivos dessa lista que realmente tenham mudado. Não fazer alterações cosméticas apenas para incluí-los.

### Conteúdo esperado

- comandos testados do README;
- requisitos marcados como Implementado/Validado/Evidenciado;
- todos os `[PREENCHER]` resolvidos com dados reais;
- ADRs com status correto;
- relatório com data, commit testado, ambiente, cenários e resultados;
- catálogo de evidências atualizado;
- declaração de IA revisada e verdadeira;
- roteiro do vídeo conferido.

### Verificação antes do commit

- testes backend passam;
- lint/build React passam;
- fluxo integrado completo passa;
- onze PNGs existem e são legíveis;
- links Markdown válidos;
- nenhum segredo, `.env` ou JSONL versionado;
- `git log --oneline` mostra evolução incremental;
- `git status` contém apenas o que foi intencionalmente preparado.

## Arquivos que nunca devem entrar em commit

```text
agencia/.env
agencia/.venv/
agencia/data/*.jsonl
frontend/.env
frontend/node_modules/
frontend/dist/
__pycache__/
.pytest_cache/
.coverage
htmlcov/
*.pyc
```

Também não versionar:

- chave JWT real;
- senha ou hash copiado de ambiente real;
- token interno real;
- JWT capturado durante testes;
- vídeo pesado sem exigência explícita do professor;
- arquivos temporários do editor/sistema.

## Arquivos que devem ser versionados

- `agencia/.env.example` sem valores secretos;
- `frontend/.env.example`;
- `agencia/pyproject.toml` e, se a ferramenta adotada gerar um lockfile Python, esse lockfile;
- `frontend/package.json` e `frontend/package-lock.json`;
- testes automatizados;
- documentação;
- evidências PNG exigidas;
- `.gitkeep` somente onde necessário para preservar pasta vazia.

## Regra para desvios do plano

Se um arquivo novo se tornar necessário:

1. identificar qual responsabilidade ele possui;
2. colocá-lo no commit que entrega essa responsabilidade;
3. atualizar este plano antes de criar o commit;
4. não usar o novo arquivo como justificativa para misturar funcionalidades.

Se um arquivo listado não for necessário, removê-lo deste plano e explicar a mudança na documentação de arquitetura quando afetar responsabilidades.

## Checklist antes de cada commit futuro

- [ ] O commit tem uma única intenção principal.
- [ ] Todos os arquivos staged pertencem à lista prevista ou ao desvio documentado.
- [ ] Não há arquivo necessário esquecido fora do staging.
- [ ] Os testes relevantes passaram.
- [ ] Evidências são reais quando incluídas.
- [ ] Documentação não afirma algo ainda não validado.
- [ ] Nenhum segredo ou artefato gerado foi incluído.
- [ ] A mensagem descreve o resultado, não a atividade vaga.

## Referências

- [Roadmap](../ROADMAP_SPRINT_1.md)
- [Guia de desenvolvimento](GUIA_DE_DESENVOLVIMENTO.md)
- [Requisitos e rastreabilidade](REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md)
- [Plano de testes e evidências](PLANO_DE_TESTES_E_EVIDENCIAS.md)
- [Guia de entrega](ENTREGA_E_VIDEO.md)
