# Plano de testes e evidências — Sprint 1

## Status

Testes automatizados e fluxo integrado executados em 7 de setembro de 2026. Uma
rodada complementar real ocorreu em 5 de outubro de 2026 e está registrada em
[`../evidencias/sprint1/registro-execucao-2026-10-05.md`](../evidencias/sprint1/registro-execucao-2026-10-05.md).
As capturas PNG e o vídeo continuam pendentes e só devem ser marcados depois de
salvos em `evidencias/sprint1/`.

> A branch atual evoluiu para a arquitetura da Sprint 2 (RabbitMQ e relógios
> vetoriais). Assim, a rodada de 05/10 revalidou transferência local, JWT e
> controle financeiro, mas não declara como reproduzidos os cenários históricos
> de HTTP direto, falha HTTP `502` e Lamport.

Na regressão documental de 11/10/2026, a suíte atual do backend teve 45 testes
aprovados e `ruff check src tests` passou; o frontend passou em lint e build.
Esses comandos verificam o estado vigente, mas não substituem as capturas reais
que permanecem pendentes.

## Resultado histórico da execução de referência

| Verificação | Resultado |
|---|---|
| `pytest --cov=iceibank --cov-report=term-missing` | 15 testes aprovados; 92% de cobertura |
| `ruff check src tests scripts` | aprovado |
| `npm run lint` | aprovado |
| `npm run build` | aprovado com Vite 8.2.2 |
| três processos FastAPI | portas 4045, 4046 e 4047 em escuta |
| transferência real 9 → 10 de R$ 25,00 | origem R$ 75,00; destino R$ 45,00; tipo `ENTRE_AGENCIAS` |
| cenário financeiro da SPEC-002 | total R$ 450,00; projeção R$ 50,00; Delivery R$ 40,00; Lazer R$ 10,00 |
| linha do tempo | arquivos das três agências lidos e ordenados pelo Lamport |

O Google Chrome bloqueou o acesso direto à porta 4045. O reteste pelo proxy Vite em 5173 passou; a decisão está registrada no ADR-005.

## Regressão da implementação vigente

| Verificação | Resultado em 11/10/2026 |
|---|---|
| `agencia/.venv/Scripts/python.exe -m pytest -q` | 45 testes aprovados |
| `agencia/.venv/Scripts/python.exe -m ruff check src tests` | aprovado |
| `frontend/npm run lint` | aprovado |
| `frontend/npm run build` | aprovado |

O lint amplo de `agencia/scripts/mesclar_logs.py` não integra este resultado;
suas pendências de estilo devem ser corrigidas antes de afirmar `ruff check .`
como aprovado.

## Objetivo

Validar cada requisito funcional, evitar regressões ao adicionar JWT e frontend e produzir as evidências exatas solicitadas no roteiro.

## Ambiente de teste

- Agência 0: `http://localhost:4045`.
- Agência 1: `http://localhost:4046`.
- Agência 2: `http://localhost:4047`.
- Frontend: `http://localhost:5173`.
- Um worker por agência.
- Logs novos ou claramente separados por sessão de teste.
- `Get-Date` visível nas capturas que comprovam execução recente.

## Massa de dados padrão

| Conta | Titular de teste | Agência | Saldo inicial |
|---:|---|---:|---:|
| 0 | Ana | 0 | 200,00 |
| 3 | Bruno | 0 | 50,00 |
| 1 | Carla | 1 | 80,00 |
| 2 | Diego | 2 | 60,00 |

Essa massa permite transferência local 0 → 3, remota 0 → 1 e falha remota 0 → 2.

## Testes unitários

### Particionamento

| ID | Entrada | Esperado |
|---|---:|---:|
| UT-PAR-01 | 0 | agência 0 |
| UT-PAR-02 | 1 | agência 1 |
| UT-PAR-03 | 2 | agência 2 |
| UT-PAR-04 | 3 | agência 0 |
| UT-PAR-05 | 10 | agência 1 |
| UT-PAR-06 | -1 | rejeição |

### Lamport

| ID | Estado/operação | Esperado |
|---|---|---|
| UT-LAM-01 | inicial | 0 |
| UT-LAM-02 | evento local | 1 |
| UT-LAM-03 | envio após 1 | 2 |
| UT-LAM-04 | local 10 recebe 3 | 11 |
| UT-LAM-05 | local 10 recebe 20 | 21 |
| UT-LAM-06 | operações concorrentes | valores locais únicos/crescentes |

### Contas e dinheiro

- criação válida e duplicada;
- saldo inicial omitido, zero e negativo;
- depósito positivo, zero, negativo e com casas excessivas;
- saque válido, valor inválido e saldo insuficiente;
- operação em partição incorreta;
- centavos sem erro de `float`;
- saldo intacto após erro.

### Transferência local

- origem/destino válidos;
- origem inexistente;
- destino inexistente;
- IDs iguais;
- valor inválido;
- saldo insuficiente;
- soma dos dois saldos preservada;
- dois eventos Lamport em ordem.

### Autenticação

- credenciais válidas e inválidas;
- token com claims esperadas;
- token válido, expirado, alterado e ausente;
- token interno válido, inválido e ausente;
- segredo/token nunca aparece na saída do logger.

### Controle financeiro mensal

- renda zero/negativa e meta maior que renda;
- soma dos limites maior que o limite mensal;
- criação e substituição de planejamento;
- atualização preservando gastos já registrados;
- gasto sem planejamento;
- gasto válido, valor inválido e saldo insuficiente;
- gasto e débito atômicos, se essa semântica for confirmada;
- meta atingível, ajuste necessário e renda excedida;
- prioridade para categoria flexível acima do limite;
- nenhuma recomendação para categoria não flexível;
- cálculo de valor não coberto;
- consulta sem incremento do Lamport.

## Testes de integração da API

| ID | Cenário | Esperado |
|---|---|---|
| IT-API-01 | criar conta na agência correta | 201 + evento |
| IT-API-02 | criar conta em agência errada | 400, sem mutação |
| IT-API-03 | consultar inexistente | 404 |
| IT-API-04 | depositar/sacar | saldos corretos + eventos |
| IT-AUT-01 | conta sem JWT | 401 |
| IT-AUT-02 | conta com JWT válido | operação permitida |
| IT-AUT-03 | conta com JWT expirado | 401 |
| IT-TRF-01 | 0 → 3 | transferência local |
| IT-TRF-02 | 0 → 1 | chamada real entre processos |
| IT-TRF-03 | token interno inválido | destino rejeita, origem trata falha |
| IT-TRF-04 | agência 2 desligada | 502 + débito mantido + log de falha |
| IT-OBS-01 | mesclar três JSONL | saída ordenada e legível |
| IT-CORS-01 | origem 5173 | permitida |
| IT-CORS-02 | origem diferente | não autorizada |
| IT-EXT-01 | criar plano com renda 500/meta 100 | limite mensal 400 |
| IT-EXT-02 | registrar gasto válido | gasto salvo, evento e débito conforme decisão |
| IT-EXT-03 | gastos totalizam 450 | projeção 50 e ajuste 50 |
| IT-EXT-04 | excessos Delivery/Lazer | recomendações 40 e 10 |
| IT-EXT-05 | consultar resumo duas vezes | resultados iguais e Lamport inalterado |

## Roteiro manual integrado

### Preparação

1. iniciar as três agências;
2. iniciar o frontend;
3. executar `Get-Date` em terminal visível;
4. realizar login;
5. criar as quatro contas da massa padrão;
6. anotar o Lamport inicial observado em cada agência.

### Cenário A — Transferência local

1. consultar contas 0 e 3: 200,00 e 50,00;
2. transferir 25,00 da conta 0 para a 3 pela Agência 0;
3. confirmar saldos 175,00 e 75,00;
4. confirmar `TRANSFERENCIA_DEBITO` seguido de `TRANSFERENCIA_CREDITO`;
5. capturar `transferencia-local.png`.

Invariante: 175,00 + 75,00 = 250,00.

### Cenário B — Transferência entre agências

1. consultar contas 0 e 1: 175,00 e 80,00;
2. transferir 30,00 da conta 0 para a 1 pela Agência 0;
3. confirmar saldos 145,00 e 110,00;
4. comparar timestamp enviado na origem com o crédito remoto no destino;
5. capturar interface/resposta e logs das duas agências;
6. salvar `transferencia-entre-agencias.png`.

Invariante global observado: 145,00 + 110,00 = 255,00.

### Cenário C — Falha conhecida

1. confirmar saldo 145,00 na conta 0;
2. encerrar a Agência 2 e deixar seu terminal/estado visível;
3. transferir 10,00 da conta 0 para a conta 2;
4. confirmar resposta 502 e mensagem explícita;
5. consultar conta 0 e confirmar saldo 135,00;
6. confirmar `TRANSFERENCIA_FALHOU` no log da Agência 0;
7. salvar `falha-conhecida.png`.

Resultado didático: o débito de 10,00 não foi revertido. A inconsistência é intencional.

Ao reiniciar a Agência 2, confirmar que sua conta permanece no SQLite local. Não a
recriar, salvo se o arquivo da agência tiver sido conscientemente resetado antes do teste.

### Cenário D — Linha do tempo

1. reiniciar/recompor a massa necessária;
2. gerar eventos independentes quase simultâneos em agências diferentes;
3. executar `python scripts/mesclar_logs.py`;
4. localizar um empate ou um par sem relação causal conhecida;
5. comparar Lamport e `horaParede`;
6. salvar `linha-do-tempo.png`;
7. anotar os eventos exatos em `RESPOSTAS.md`.

### Cenário E — JWT

1. chamar conta sem token e salvar `auth-sem-token.png`;
2. autenticar e executar operação válida, salvando `auth-com-token.png` sem expor o JWT completo;
3. em ambiente de teste, emitir token com expiração curta;
4. esperar expirar e confirmar 401;
5. salvar `auth-token-expirado.png`;
6. restaurar a expiração normal;
7. repetir transferência remota para confirmar a comunicação interna.

### Cenário F — Frontend

1. login e seleção de agência: `frontend-login.png`;
2. consulta, depósito e saque;
3. transferência local e remota: `frontend-transferencia.png`;
4. saque acima do saldo ou agência indisponível: `frontend-erro.png`;
5. confirmar que nenhum erro depende apenas do console.

### Cenário G — Funcionalidade adicional

1. criar a conta 6 na Agência 0 com saldo suficiente para os gastos do cenário;
2. definir renda prevista de R$ 500,00 e meta de economia de R$ 100,00 para `2026-09`;
3. configurar limites de Alimentação R$ 150,00, Transporte R$ 100,00, Delivery R$ 80,00 e Lazer R$ 70,00;
4. marcar Delivery e Lazer como flexíveis;
5. registrar R$ 150,00 em Alimentação, R$ 80,00 em Transporte, R$ 120,00 em Delivery e R$ 100,00 em Lazer;
6. confirmar total gasto de R$ 450,00, economia projetada de R$ 50,00 e ajuste necessário de R$ 50,00;
7. confirmar recomendação de R$ 40,00 em Delivery e R$ 10,00 em Lazer;
8. confirmar os eventos `DEFINIR_PLANEJAMENTO_MENSAL` e `REGISTRAR_GASTO`;
9. confirmar que consultar o resumo não incrementa Lamport;
10. se o débito do gasto for confirmado, conferir que cada registro também reduziu o saldo;
11. salvar `funcionalidade-adicional.png` com meta, totais e recomendações visíveis.

## Catálogo de evidências

Todos os arquivos ficam em `evidencias/sprint1/`.

Consulte também o [índice da pasta de evidências](../evidencias/sprint1/README.md).

| Arquivo | Deve mostrar | Estado |
|---|---|---|
| `transferencia-local.png` | requisição/interface, saldos e log local | Pendente |
| `transferencia-entre-agencias.png` | resultado e logs de origem/destino | Pendente |
| `falha-conhecida.png` | destino parado, 502, saldo debitado e log | Pendente |
| `linha-do-tempo.png` | saída do mesclador e `Get-Date` | Pendente |
| `auth-sem-token.png` | requisição sem token e 401 | Pendente |
| `auth-com-token.png` | operação autorizada sem revelar token | Pendente |
| `auth-token-expirado.png` | token expirado e 401 | Pendente |
| `frontend-login.png` | login funcional | Pendente |
| `frontend-transferencia.png` | transferência concluída na interface | Pendente |
| `frontend-erro.png` | erro visível para o usuário | Pendente |
| `funcionalidade-adicional.png` | meta de R$ 100, gastos e recomendações | Pendente |

## Padrão de captura

- usar imagem PNG legível;
- mostrar resultado em execução, não apenas código;
- incluir `Get-Date` quando exigido;
- não cortar o código HTTP ou mensagem relevante;
- mostrar logs das duas agências na transferência remota;
- ocultar token, senha, hash e segredo interno;
- evitar informações pessoais desnecessárias;
- conferir o arquivo depois de salvar;
- não editar a imagem de forma que altere o resultado técnico.

## Registro de execução

Preencher depois de cada rodada:

| Rodada | Data/hora | Commit | Cenários | Resultado | Observações |
|---|---|---|---|---|---|
| 1 | Pendente | Pendente | Pendente | Pendente | Pendente |
| 2 | 05/10/2026 15:24 -03:00 | `52af43a` | JWT, transferência local e controle financeiro | Aprovado nos cenários executados | Detalhes e limitações de arquitetura no registro de 05/10; PNGs ainda pendentes. |

## Critério de saída

A Sprint 1 somente pode ser considerada validada quando:

- todos os testes críticos passam;
- os saldos esperados foram conferidos;
- a falha conhecida foi reproduzida, não corrigida ou escondida;
- JWT não quebrou transferência remota;
- todos os PNGs obrigatórios existem e são legíveis;
- observações reais foram inseridas em `RESPOSTAS.md`;
- os requisitos foram atualizados para Validado/Evidenciado.

## Referências

- [Requisitos e rastreabilidade](REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md)
- [Contrato da API](API_SPRINT_1.md)
- [Configuração e execução](CONFIGURACAO_E_EXECUCAO.md)
- [Lamport e observabilidade](LAMPORT_E_OBSERVABILIDADE.md)
