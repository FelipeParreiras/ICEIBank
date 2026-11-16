# Respostas — Sprint 1 do ICEIBank

## Estado do documento

Este arquivo consolida as decisões e os comportamentos observados na implementação de 7 de setembro de 2026. A tabela de evidências permanece pendente porque nenhum PNG ou commit foi produzido nesta etapa, conforme solicitado.

## 1. Decisões do projeto

### 1.1 Linguagem e framework do backend

Escolhi Python com FastAPI porque já possuo familiaridade com Python e considero sua sintaxe mais prática para concentrar o esforço nos conceitos distribuídos da disciplina. FastAPI também oferece validação de dados e documentação da API, reduzindo configuração manual. Java/Spring Boot atenderia ao roteiro, mas adicionaria uma curva de aprendizado que não contribui diretamente para os objetivos desta sprint.

Referência: [ADR-001](docs/decisions/ADR-001-stack-python-fastapi-react.md).

### 1.2 Tecnologia do frontend

Escolhi React porque já tenho habilidade com a biblioteca. O projeto usará Vite e JavaScript modular. A decisão evita aprender um framework novo durante a sprint e facilita separar componentes visuais, estado de autenticação, seleção da agência e cliente HTTP.

Referência: [ADR-001](docs/decisions/ADR-001-stack-python-fastapi-react.md).

### 1.3 Portas

Meus dois últimos dígitos do RA são 45. A porta base será 4045:

- Agência 0: 4045;
- Agência 1: 4046;
- Agência 2: 4047;
- Frontend: 5173.

### 1.4 Formato das credenciais e expiração

**Decisão implementada:** usar um usuário de demonstração configurado por variável de ambiente, com senha armazenada como PBKDF2-HMAC-SHA256. O login retorna um JWT HS256 com expiração inicial de 15 minutos, configurável para permitir o teste de token expirado.

Essa opção foi escolhida porque o requisito da sprint é autenticação. Criar cadastro, recuperação de senha e associação de usuários a contas ampliaria o escopo sem ser necessário para a avaliação.

Foi usada a biblioteca PyJWT. Os claims emitidos são `sub`, `iss`, `iat` e `exp`; o backend valida assinatura, algoritmo, emissor e expiração.

### 1.5 Autenticação entre agências

**Decisão implementada:** a chamada de crédito remoto usa uma credencial interna diferente do JWT do usuário. O JWT representa uma pessoa autenticada; o token interno representa outra instância do serviço. O token interno nunca é enviado ao frontend.

Essa separação reduz a propagação do JWT do navegador e impede que a rota interna fique pública. Em uma aplicação real, o mecanismo simples seria substituído por uma identidade de serviço mais forte, como mTLS.

Referência: [ADR-003](docs/decisions/ADR-003-autenticacao-e-comunicacao-interna.md).

### 1.6 Funcionalidade adicional

Escolhi implementar um **Controle Financeiro Mensal** por conta. A pessoa define sua renda prevista, informa quanto deseja economizar no mês, configura limites por categoria e registra gastos. O sistema calcula quanto ainda pode ser gasto, projeta a economia e recomenda onde reduzir despesas quando a meta estiver ameaçada.

As recomendações são produzidas por regras transparentes: primeiro observam categorias flexíveis acima do limite e, se ainda houver ajuste necessário, consideram as maiores categorias flexíveis. Não será usado um serviço externo de IA.

O MVP será armazenado em memória na agência responsável. Criar/alterar o planejamento e registrar gasto produzem eventos Lamport; consultar o resumo não incrementa o relógio.

Registrar um gasto debita o saldo da conta na mesma seção crítica usada para inserir o gasto, evitando gasto sem débito ou débito sem gasto no armazenamento em memória.

Referências: [ADR-004](docs/decisions/ADR-004-controle-financeiro-mensal.md) e [SPEC-002](docs/specs/SPEC-002-controle-financeiro-mensal.md).

## 2. Parte B — Relógio de Lamport

### 2.1 Por que usar `max(contador_local, timestampRecebido) + 1`?

O recebimento precisa ficar logicamente depois tanto dos eventos que a agência já processou quanto do evento de envio da mensagem. O `max` preserva o maior histórico conhecido e o `+1` cria um novo evento posterior aos dois. Adotar diretamente o timestamp recebido poderia fazer o relógio local regredir quando a mensagem viesse de uma agência com contador menor.

### 2.2 Agência no contador 10 recebendo timestamp 3

O novo contador é:

```text
max(10, 3) + 1 = 11
```

A agência que já processou muitos eventos não volta no tempo lógico ao receber uma mensagem de uma agência mais lenta. Contadores maiores não significam necessariamente mais tempo físico; representam apenas mais progresso lógico conhecido naquele processo.

O teste `test_recebimento_usa_maximo_mais_um` confirmou `ao_receber(7) == 8` e, em seguida, `ao_receber(3) == 9`, sem regressão do contador.

## 3. Parte D — Transferências

### 3.1 Por que a transferência local não usa envio/recebimento?

Na transferência local, débito e crédito acontecem dentro do mesmo processo e compartilham o mesmo relógio. Não existe uma mensagem cruzando a fronteira entre relógios independentes, então os dois passos são eventos locais consecutivos.

Na transferência entre agências, cada processo possui seu próprio contador. O timestamp enviado pela origem permite que o destino atualize seu relógio e registre o crédito logicamente depois do envio.

### 3.2 Falha conhecida e consistência

O roteiro define que o débito remoto acontece antes da chamada à agência de destino. Se o destino estiver indisponível, o débito não é revertido automaticamente.

- saldo da origem antes: R$ 100,00;
- valor transferido no teste automatizado: R$ 30,00;
- saldo depois do 502: R$ 70,00;
- evento `TRANSFERENCIA_FALHOU` observado no timestamp Lamport 4 (`CRIAR_CONTA=1`, débito=2 e envio=3);
- evidência: `evidencias/sprint1/falha-conhecida.png`.

Isso significa que a operação não é atômica entre as agências: uma parte foi confirmada e a outra não. O saldo global fica inconsistente e o valor parece desaparecer temporariamente.

### 3.3 Duas formas de corrigir no futuro

1. **Two-Phase Commit (2PC):** um coordenador primeiro pergunta se os participantes podem confirmar e só depois ordena o commit. Se algum participante não estiver pronto, todos abortam. O custo é maior acoplamento e possibilidade de bloqueio diante de falhas do coordenador.
2. **Saga:** a transferência é dividida em etapas com ações compensatórias. Se o crédito falhar, uma compensação futura devolve o débito. A solução favorece disponibilidade, mas aceita consistência eventual e exige idempotência/controle das compensações.

Essas soluções são apenas descritas nesta sprint; não serão implementadas antes da Sprint 4.

## 4. Parte E — Linha do tempo unificada

### 4.1 Timestamps diferentes sem relação conhecida

Lamport garante que causalidade conhecida implica timestamps crescentes. A relação inversa não é garantida. Portanto, ao ver dois timestamps diferentes, não posso concluir apenas pelos números que o primeiro evento causou o segundo; eles podem ter acontecido independentemente em agências diferentes.

### 4.2 Lamport distingue concorrência com certeza?

Não. Um relógio escalar de Lamport não carrega informação suficiente para distinguir sempre “A aconteceu antes de B” de “A e B são concorrentes”. Relógios vetoriais mantêm uma posição por processo e permitem comparar históricos: vetores incomparáveis indicam concorrência. Isso motiva sua introdução na Sprint 2.

### 4.3 Observação obrigatória da execução

Par real observado na transferência entre as contas 9 e 10:

| Campo | Evento A | Evento B |
|---|---|---|
| Agência | `agencia-0` | `agencia-1` |
| Tipo | `TRANSFERENCIA_DEBITO` | `TRANSFERENCIA_CREDITO_REMOTO` |
| Lamport | 8 | 10 |
| Hora de parede | `2026-09-08T02:53:36.472861Z` | `2026-09-08T02:53:36.748637Z` |
| Relação observada | origem do envio | efeito causado pelo envio no destino |

Esses eventos não são concorrentes: o crédito remoto foi causado pela mensagem enviada depois do débito. Os timestamps não empataram e a hora de parede sugeriu a mesma ordem mostrada pelo Lamport. A criação independente da conta 11 na Agência 2 também apareceu na saída mesclada, comprovando a leitura dos três arquivos.

Evidência: `evidencias/sprint1/linha-do-tempo.png`.

## 5. Parte F — Autenticação JWT

### 5.1 Autenticação versus autorização

Autenticação confirma quem está fazendo a requisição. Autorização decide o que essa identidade pode fazer.

A implementação verifica autenticação, mas não autorização por titularidade. Assim, um usuário autenticado pode sacar ou transferir de qualquer conta cujo ID conheça. Isso atende ao escopo mínimo, mas não seria aceitável em um banco real.

### 5.2 Por que validar JWT sem consultar um banco?

O servidor recalcula e verifica a assinatura do token usando sua chave. Se a assinatura for válida e claims como `exp` forem aceitas, o servidor confia que o conteúdo não foi alterado. Não é necessário guardar uma sessão em memória ou consultar um banco a cada requisição.

Isso facilita escalar múltiplas instâncias porque elas só precisam compartilhar a configuração criptográfica. Em contrapartida, revogar um token específico antes da expiração é mais difícil sem adicionar estado, como uma lista de revogação.

### 5.3 Consequência do vazamento da chave secreta

Quem obtiver a chave pode forjar tokens com identidades e prazos arbitrários. O servidor não consegue distinguir um token forjado corretamente assinado de um legítimo. A resposta deve incluir troca imediata da chave, invalidação dos tokens anteriores e investigação de onde o segredo foi exposto.

## 6. Parte G — Frontend

### 6.1 Como o frontend lembra o token?

Após o login, `AuthContext.jsx` guarda o JWT em estado e em `localStorage`. O cliente central `api/cliente.js` recebe o token e adiciona `Authorization: Bearer` em cada chamada autenticada.

Isso evita repetir a lógica em cada componente.

### 6.2 O que acontece quando o token expira?

Ao receber 401, `apiRequest` chama o encerramento de sessão fornecido pelo `AuthContext`: o token e o usuário são removidos do estado e do `localStorage`, e o `App` volta a renderizar `LoginPage` com mensagem amigável. A captura específica com token expirado ainda deve ser produzida.

### 6.3 Onde estão Model, View e Controller?

- **Model:** schemas/modelos/serviços no backend e estado/contratos no frontend.
- **View:** respostas JSON no backend e componentes/páginas React para a interface.
- **Controller:** módulos FastAPI com `APIRouter` no backend e hooks/manipuladores que coordenam ações no React.

React não impõe MVC clássico e pode misturar View e Controller dentro de componentes. Na implementação, chamadas HTTP ficam em `frontend/src/api/cliente.js`, estado global em `AuthContext.jsx` e `AgenciaContext.jsx`, telas em `pages/` e formulários/visualizações em `components/`. Os handlers de `DashboardPage.jsx` ainda coordenam parte do comportamento de controller, um desvio pragmático documentado no blueprint.

## 7. Registro das evidências

| Evidência | Data | Commit relacionado | Observação |
|---|---|---|---|
| `transferencia-local.png` | Pendente | Pendente | Pendente |
| `transferencia-entre-agencias.png` | Pendente | Pendente | Pendente |
| `falha-conhecida.png` | Pendente | Pendente | Pendente |
| `linha-do-tempo.png` | Pendente | Pendente | Pendente |
| `auth-sem-token.png` | Pendente | Pendente | Pendente |
| `auth-com-token.png` | Pendente | Pendente | Pendente |
| `auth-token-expirado.png` | Pendente | Pendente | Pendente |
| `frontend-login.png` | Pendente | Pendente | Pendente |
| `frontend-transferencia.png` | Pendente | Pendente | Pendente |
| `frontend-erro.png` | Pendente | Pendente | Pendente |
| `funcionalidade-adicional.png` | Pendente | Pendente | Meta, gastos e recomendações |

### 7.1 Rodada complementar de 05/10/2026

O registro verificável desta rodada está em
[`evidencias/sprint1/registro-execucao-2026-10-05.md`](evidencias/sprint1/registro-execucao-2026-10-05.md).
Foram reexecutados, na Agência 0, a consulta sem credencial (HTTP 401), o
acesso autenticado, a transferência local 9900 → 9903 de R$ 25,00 (saldos
finais R$ 175,00 e R$ 75,00) e o cenário financeiro da conta 9906 (total
R$ 450,00, projeção R$ 50,00, Delivery R$ 40,00 e Lazer R$ 10,00).

A árvore atual é a evolução da Sprint 2 e usa RabbitMQ/relógio vetorial. Logo,
não se deve declarar que as capturas históricas de HTTP direto, falha 502 ou
Lamport foram produzidas nesta rodada. Todas as imagens da tabela continuam
pendentes até serem capturadas da versão apropriada, com os requisitos visuais
do roteiro.

## 8. Declaração de uso de IA

Rascunho a ser confirmado e ajustado pelo aluno antes da entrega:

> Utilizei o OpenAI Codex como apoio no planejamento, definição da arquitetura, organização da documentação e revisão técnica da Sprint 1. As decisões e respostas foram revisadas por mim, e os resultados descritos como observados foram obtidos em execuções reais conduzidas por mim. Sou capaz de explicar e defender o código e as decisões entregues.

Não afirmar que uma revisão ou execução foi realizada antes que isso aconteça.

## 9. Revisão final deste documento

- [x] Remover todos os marcadores `[PREENCHER]`.
- [x] Atualizar todos os itens “Validar após implementação”.
- [x] Confirmar o status do ADR-003 e manter o histórico de substituição do ADR-002 pelo ADR-004.
- [x] Citar saldos, timestamps e eventos reais.
- [ ] Conferir links e nomes das evidências.
- [ ] Reescrever em linguagem própria onde necessário.
- [ ] Confirmar que a declaração de IA é verdadeira.

---

# Sprint 2 - Respostas e registro de entrega

## Parte B - Relógio vetorial

### 6.4.1 Crescimento para 10 agências

Cada timestamp passa a ter 10 posições e cada mensagem carrega as 10. O custo
por mensagem cresce linearmente com o número de processos, além de aumentar o
custo de comparação. Para três agências do ICEIBank é pequeno e torna explícita
a causalidade; para centenas ou milhares de processos se torna um problema e
exige técnicas como grupos, versões compactadas ou rastreamento parcial.

### 6.4.2 V1 = [3, 1, 0] e V2 = [3, 2, 0]

V1 aconteceu antes de V2: 3 <= 3, 1 <= 2 e 0 <= 0, com pelo menos uma posição
estritamente menor. Portanto V1 <= V2 e os vetores não são iguais.

### 6.4.3 V1 = [3, 1, 0] e V2 = [1, 3, 0]

São concorrentes. V1 não é menor ou igual a V2 porque 3 > 1 na primeira posição;
V2 não é menor ou igual a V1 porque 3 > 1 na segunda. Nenhum vetor contém todo
o histórico do outro.

## Parte C - Publish/Subscribe

### 7.5.1 Retorno da agência de destino

Na execução de 05/10/2026, a Agência 1 foi encerrada depois de criar a conta 91.
Uma transferência de R$ 20,00 da conta 90 foi publicada com a Agência 1 offline
e a origem passou de R$ 170,00 para R$ 150,00. Ao reiniciar a Agência 1, a fila
entregou a mensagem e o log registrou `CREDITO_REMOTO_FALHOU`, vetor `[3, 1, 0]`
e motivo `CONTA_NAO_ENCONTRADA`. A mensageria não falhou: a conta tinha sido
perdida porque o repositório ainda é somente em memória.

### 7.5.2 Melhoria e problema restante

Ao contrário do HTTP síncrono da Sprint 1, uma agência offline não impede a
publicação: a fila retém a mensagem. Isso não torna o sistema automaticamente
correto. As contas continuam voláteis, não existe transação distribuída,
persistência, idempotência durável ou confirmação de crédito ao remetente.

### 7.5.3 Segurança do consumidor

O consumidor não recebe JWT porque não é uma requisição de navegador; ele só
aceita mensagens entregues pelo RabbitMQ. Isso é aceitável apenas enquanto o
broker, vhost, credenciais e permissões de publicação forem restritos às
agências autorizadas. Em produção, as permissões AMQP devem limitar cada
publisher e a mensagem também deve ser validada como entrada não confiável.

## Parte D - Linha do tempo causal

### 8.3.1 Comparação confiável

Cada vetor registra o maior contador conhecido de cada agência. Comparar todas
as posições permite provar V1 <= V2 quando o histórico de V1 está contido no de
V2; se cada vetor tem ao menos uma posição maior, eles são incomparáveis e,
portanto, concorrentes. Lamport escalar não mantém essas posições independentes.

### 8.3.2 Par concorrente observado

No teste real de 05/10/2026, `CRIAR_CONTA` da Agência 0 teve vetor `[1, 0, 0]`
e `CRIAR_CONTA` da Agência 1 teve `[0, 1, 0]`. O mesclador classificou o par como
concorrente: a primeira posição é maior no primeiro vetor e a segunda é maior no
segundo, portanto não há relação de causa e efeito entre as criações.

### 8.3.3 Escalabilidade

Comparar todos os pares é O(n²), inviável para milhões de eventos. Em produção,
o processamento poderia ser incremental, particionado por tempo/agência,
indexado por vetor, limitado a janelas de investigação ou delegado a um motor
de análise distribuído. A ferramenta atual prioriza transparência acadêmica.

## Funcionalidade adicional - Caixinha

A Caixinha permite criar, listar, consultar, renomear e excluir reservas de uma
conta. Guardar debita a conta e cria um lote; resgatar aplica rendimentos vencidos
e consome lotes por FIFO. Cada lote rende 10% composto a cada 48 horas, com
arredondamento em centavos `ROUND_HALF_UP`. A exclusão resgata o saldo integral
para a conta antes de remover a reserva. A implementação e os testes estão
documentados em SPEC-003, ADR-006, ADR-008 e ADR-009. Na rodada de 05/10/2026,
a conta 92 guardou R$ 120,00 e resgatou R$ 20,00, terminando com R$ 400,00 na
conta e R$ 100,00 na Caixinha. A captura real `evidencias/sprint2/caixinha.png`
continua pendente.

## Uso de IA - Sprint 2

Rascunho a ser revisado pelo aluno antes da entrega:

> Utilizei o OpenAI Codex no desenvolvimento da Sprint 2 para apoio à implementação,
> testes, documentação e revisão. Revisei o código e devo conseguir explicar as
> decisões e os resultados. Os testes automatizados e a validação no RabbitMQ real
> registrados foram executados; as capturas PNG da entrega permanecem pendentes.
