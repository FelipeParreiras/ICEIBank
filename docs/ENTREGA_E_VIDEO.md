# Guia de entrega e vídeo — Sprint 1

## Objetivo

Garantir que o código funcional também seja reproduzível, explicável e alinhado aos 20 pontos da avaliação.

## Conteúdo esperado do repositório

- código FastAPI da agência;
- código React do frontend;
- testes automatizados;
- script Python de mesclagem dos logs;
- `.env.example` sem segredos;
- logs JSONL ignorados;
- onze imagens mínimas em `evidencias/sprint1/`;
- `RESPOSTAS.md` completo;
- README e documentação técnica;
- histórico incremental de commits.

## Auditoria antes da entrega

### Código

- [ ] as três agências usam o mesmo código;
- [ ] portas 4045, 4046 e 4047 estão documentadas;
- [ ] partição `id % 3` é aplicada em todas as operações;
- [ ] valores inválidos não alteram saldo;
- [ ] Lamport é seguro para concorrência;
- [ ] transferência local preserva saldo total;
- [ ] transferência remota funciona com JWT e token interno;
- [ ] falha remota deixa o débito e gera 502/log;
- [ ] frontend exibe erros;
- [ ] Controle Financeiro Mensal calcula meta, gastos e recomendações.

### Testes

- [ ] suíte Python passa;
- [ ] lint/build do frontend passa;
- [ ] fluxo integrado foi executado com três processos reais;
- [ ] token ausente, válido e expirado foram testados;
- [ ] script de linha do tempo foi executado;
- [ ] todos os saldos foram conferidos antes/depois.

### Segurança

- [ ] nenhum `.env` foi versionado;
- [ ] nenhum JWT aparece em imagem ou log;
- [ ] nenhuma senha, hash ou token interno aparece no diff;
- [ ] CORS não usa origem curinga desnecessária;
- [ ] rota interna rejeita chamada sem credencial.

### Documentação

- [ ] README funciona a partir de clone limpo;
- [ ] API documentada corresponde ao código;
- [ ] ADRs possuem status atual;
- [ ] `RESPOSTAS.md` cita observações reais;
- [ ] uso de IA foi declarado de forma verdadeira;
- [ ] requisitos foram marcados com o estado correto.

### Evidências

- [ ] nomes dos onze PNGs estão exatos;
- [ ] imagens são legíveis;
- [ ] `Get-Date` está visível quando solicitado;
- [ ] transferência remota mostra as duas agências;
- [ ] falha mostra 502, saldo e evento de falha;
- [ ] nenhuma imagem expõe segredo.

## Revisão do Git

Antes de preparar qualquer alteração, conferir o [plano de commits e arquivos](PLANO_DE_COMMITS_SPRINT_1.md).

Comandos de inspeção:

```powershell
git status --short
git log --oneline --decorate
git diff
git diff --cached
```

O histórico deve contar a evolução. Sequência esperada:

1. estrutura;
2. particionamento;
3. Lamport/logs;
4. contas;
5. transferências;
6. observabilidade;
7. JWT;
8. frontend;
9. extra;
10. documentação final.

Não criar um único commit contendo toda a sprint. Não versionar arquivos gerados ou segredos apenas para “completar” a entrega.

## Roteiro recomendado do vídeo

A duração deve seguir a orientação dos professores, se houver. O vídeo precisa priorizar demonstração e explicação.

### 1. Apresentação

- objetivo do ICEIBank;
- tecnologias escolhidas e justificativa;
- visão das três agências e portas.

### 2. Arquitetura

- mesmo serviço executado três vezes;
- partição `id % 3`;
- MVC adaptado ao FastAPI e React;
- SQLite local por agência e um worker por agência.

### 3. Contas e transferências

- criar/consultar uma conta;
- depósito e saque;
- transferência local;
- transferência entre agências mostrando dois terminais.

### 4. Relógio vetorial e mensageria

- apontar os vetores na origem e no evento de crédito remoto;
- executar/mostrar linha do tempo unificada;
- explicar eventos causais e concorrentes;
- mostrar que uma transferência remota confirma a publicação no RabbitMQ, não
  o crédito já observado pelo cliente de origem.

### 5. Indisponibilidade da mensageria

- executar transferência sem `RABBITMQ_URL` ou com broker indisponível;
- mostrar 503 `MENSAGERIA_INDISPONIVEL` e saldo de origem intacto;
- explicar que a entrega não é exatamente uma vez e não há confirmação reversa
  de crédito.

### 6. JWT e frontend

- login;
- ação autenticada;
- tratamento visual de erro;
- explicar token do usuário versus credenciais do RabbitMQ mantidas no backend.

### 7. Funcionalidade adicional

- definir uma meta de economia de R$ 100,00;
- registrar gastos categorizados;
- mostrar limite, economia projetada e ajuste necessário;
- explicar por que Delivery/Lazer receberam sugestões de redução;
- mostrar que a consulta não incrementa o relógio vetorial;
- explicar que a recomendação é determinística e limitada aos dados cadastrados.

### 8. Fechamento

- limitações assumidas;
- evidências e testes;
- principais aprendizados;
- declaração responsável do apoio de IA.

## Perguntas que o aluno deve saber responder

- Por que três processos não compartilham o mesmo relógio?
- Por que `max(local, recebido) + 1`?
- Qual diferença entre evento local e mensagem remota?
- Por que transferência local não precisa de `ao_enviar/ao_receber`?
- Onde o dinheiro se perde na falha conhecida?
- Por que não foi adicionado rollback agora?
- Qual diferença entre autenticação e autorização?
- Por que o JWT pode ser validado sem sessão no servidor?
- Por que a rota interna não reutiliza o JWT do navegador?
- Onde estão Model, View e Controller?
- Por que um worker por agência?
- Por que `Decimal` em vez de `float`?
- O que a funcionalidade adicional acrescenta?
- Como o sistema calcula a economia projetada e escolhe as categorias sugeridas?
- Registrar um gasto altera o saldo? Por que essa decisão foi tomada?

## Pacote final

Antes de enviar o link ou arquivo:

1. conferir branch/commit solicitado pela instituição;
2. abrir o repositório como avaliador;
3. seguir o README sem conhecimento implícito;
4. abrir cada evidência;
5. reproduzir o vídeo se a plataforma permitir prévia;
6. confirmar que a entrega não contém dados pessoais ou segredos desnecessários.

## Referências

- [Roadmap](../ROADMAP_SPRINT_1.md)
- [Plano de testes e evidências](PLANO_DE_TESTES_E_EVIDENCIAS.md)
- [Requisitos e rastreabilidade](REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md)
- [RESPOSTAS.md](../RESPOSTAS.md)
