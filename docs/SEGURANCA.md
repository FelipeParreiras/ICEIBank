# Segurança — Sprint 1

## Status

Modelo implementado e revisado em 11/10/2026. O JWT permanece regido pelo
ADR-003; o crédito remoto HTTP descrito na baseline foi substituído pelo canal
RabbitMQ definido no ADR-007.

## Objetivo

Atender aos requisitos acadêmicos de autenticação JWT e proteger a comunicação entre agências sem apresentar a Sprint 1 como um sistema bancário pronto para produção.

## Limites de confiança

```mermaid
flowchart LR
    U["Pessoa usuária"] -->|"credenciais/JWT"| F["React no navegador"]
    F -->|"JWT"| A["API da agência"]
    A -->|"AMQP + relógio vetorial"| B["RabbitMQ / agência de destino"]
    A -->|"sem segredos"| L["JSONL/terminal"]
```

- Navegador e entrada HTTP são não confiáveis.
- Uma agência só processa crédito remoto recebido pela sua fila AMQP configurada
  e após validar o formato da mensagem.
- Logs e evidências são considerados públicos para fins acadêmicos; não podem conter segredos.
- Arquivos `.env` são locais e não devem entrar no Git.

## Ativos protegidos

- saldo e integridade das contas persistidos no SQLite local;
- chave de assinatura JWT;
- hash da senha de demonstração;
- credenciais AMQP do broker; o token interno da Sprint 1 permanece apenas como
  compatibilidade de configuração e não protege o fluxo remoto vigente;
- tokens JWT emitidos;
- detalhes operacionais que não precisam ser expostos.

## Autenticação do usuário

### Credenciais

- um usuário de demonstração configurado por ambiente;
- senha comparada por hash usando biblioteca apropriada;
- resposta genérica para usuário ou senha inválidos;
- nenhuma senha escrita em logs ou retornada pela API.

Também existe cadastro público que cria credenciais persistidas na agência 0 e
inicia a sessão. Não há recuperação de senha nem vínculo entre usuário e conta.

### JWT

Claims implementadas:

| Claim | Uso |
|---|---|
| `sub` | identidade autenticada |
| `iat` | momento de emissão |
| `exp` | expiração obrigatória |
| `iss` | emissor ICEIBank |

Regras:

- algoritmo permitido fixado pelo servidor; nunca aceitar o algoritmo indicado pelo cliente sem restrição;
- segredo forte e comum às três instâncias locais;
- expiração configurável, com 15 minutos como valor inicial de desenvolvimento;
- 401 para token ausente, inválido ou expirado;
- mensagens diferenciadas por código para a interface, sem expor detalhes criptográficos;
- não registrar JWT completo.

## Autorização

A Sprint 1 possui autenticação, mas não autorização por titularidade. Depois de autenticado, o usuário pode operar qualquer conta cujo ID conheça.

Essa limitação é aceitável para o roteiro, desde que:

- seja descrita em `RESPOSTAS.md`;
- não seja apresentada como segurança bancária real;
- uma evolução futura exija vínculo usuário-conta e políticas por operação.

## Comunicação interna

O crédito remoto não é mais exposto por rota HTTP. A origem publica uma mensagem
AMQP no RabbitMQ; cada agência consome somente sua fila. `RABBITMQ_URL` contém
credenciais do broker, fica apenas no ambiente local e nunca deve aparecer em
logs, commits, frontend ou evidências. A validação do formato da mensagem ocorre
antes de aplicar o crédito e o relógio vetorial é atualizado no recebimento.

Em produção, a URL do broker deve ser fornecida por um gerenciador de segredos,
com rotação e TLS. O desenho acadêmico não implementa autenticação mútua entre
serviços nem autorização por titularidade.

## Armazenamento do token no React

O plano usa `localStorage` por simplicidade didática e compatibilidade com o roteiro.

Riscos:

- qualquer script executado na página pode ler o token;
- uma vulnerabilidade XSS pode roubar a sessão;
- o token permanece após fechar o navegador até expirar ou ocorrer logout.

Controles mínimos:

- não renderizar HTML não confiável;
- não usar `dangerouslySetInnerHTML`;
- não carregar scripts desconhecidos;
- apagar o token no logout e ao receber 401;
- não exibir token na tela, console ou captura;
- manter dependências reduzidas.

Em um banco real, a preferência seria cookie `HttpOnly`, `Secure` e `SameSite`, com desenho explícito para CSRF.

## CORS

- permitir apenas `http://localhost:5173` durante a sprint;
- permitir os métodos e cabeçalhos realmente utilizados;
- não combinar origem curinga com credenciais;
- chamadas agência-a-agência não dependem de CORS, pois CORS é uma política do navegador.

## Validação de entrada

- IDs inteiros e não negativos;
- valores positivos, finitos e com até duas casas;
- nomes não vazios;
- agência e partição validadas no servidor;
- URL de agência escolhida a partir de lista fechada, nunca de URL arbitrária enviada pelo cliente;
- timeout em chamadas internas;
- mensagens remotas validadas por schema.
- competência mensal, categoria e limites financeiros validados no servidor;
- recomendação calculada somente com categorias flexíveis definidas pela pessoa usuária.

## Dados do controle financeiro

- descrições de gastos podem revelar hábitos pessoais;
- usar apenas dados fictícios nas evidências e no vídeo;
- não enviar planejamento ou gastos a serviços externos;
- não registrar descrição completa no terminal quando IDs/categoria/valor forem suficientes;
- proteger todas as rotas financeiras com JWT;
- não apresentar a recomendação como aconselhamento financeiro profissional.

## Logs seguros

Pode registrar:

- agência, tipo, timestamp vetorial e hora UTC;
- IDs de conta necessários para o exercício;
- valor e saldo conforme o roteiro;
- competência, categoria e valores agregados do controle financeiro;
- tipo resumido de falha.

Não pode registrar:

- senha ou hash;
- JWT;
- token interno;
- conteúdo integral de cabeçalhos;
- stack trace devolvida ao frontend;
- `.env`.
- descrições sensíveis de gastos sem necessidade técnica.

## Resposta a vazamento de segredo

Se um segredo aparecer no Git ou em evidência:

1. considerar o segredo comprometido;
2. gerar e configurar um valor novo em todas as instâncias;
3. invalidar tokens antigos ao trocar a chave JWT;
4. remover o segredo do arquivo/evidência;
5. avaliar a necessidade de limpar o histórico Git com orientação do professor;
6. documentar o incidente sem republicar o valor.

Apagar somente o commit mais recente não torna um segredo antigo automaticamente seguro.

## Verificações obrigatórias

| ID | Cenário | Esperado |
|---|---|---|
| SEG-01 | login inválido | 401 genérico |
| SEG-02 | rota de conta sem JWT | 401 |
| SEG-03 | JWT alterado | 401 |
| SEG-04 | JWT expirado | 401 e frontend retorna ao login |
| SEG-05 | `RABBITMQ_URL` ausente | transferência remota retorna 503 e saldo de origem intacto |
| SEG-06 | publicação AMQP sem confirmação | transferência retorna erro e saldo de origem intacto |
| SEG-07 | mensagem AMQP válida na fila do destino | crédito aplicado pelo consumidor |
| SEG-08 | origem CORS não permitida | bloqueio pelo navegador |
| SEG-09 | logs após todos os testes | nenhum segredo encontrado |
| SEG-10 | controle financeiro sem JWT | 401 e nenhum dado retornado/alterado |

## Limitações assumidas

- HTTP local sem TLS.
- Segredos compartilhados manualmente entre processos.
- Sem revogação individual antes da expiração.
- Sem rate limit de login.
- Sem autorização por conta.
- SQLite local sem criptografia em repouso, backup automático ou controle de
  acesso do SGBD.

Essas limitações impedem uso real, mas não bloqueiam os objetivos acadêmicos da Sprint 1.

## Referências

- [ADR-003](decisions/ADR-003-autenticacao-e-comunicacao-interna.md)
- [Contrato da API](API_SPRINT_1.md)
- [Plano de testes](PLANO_DE_TESTES_E_EVIDENCIAS.md)
