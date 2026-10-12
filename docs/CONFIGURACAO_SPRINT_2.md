# Configuração — Sprint 2

## Estado

Instância RabbitMQ criada pelo aluno e conexão AMQP validada pela aplicação em
04/10/2026. A topologia foi declarada pelo código e transferências reais foram
processadas. Revisado em 11/10/2026; as capturas PNG da entrega permanecem
pendentes.

## Etapa 1: preparar a instância

O roteiro sugere CloudAMQP e permite RabbitMQ local como alternativa.
Começar pelo serviço gerenciado para evitar instalação local nesta etapa.

1. Acessar o CloudAMQP, criar a conta ou entrar e concluir a verificação de email.
2. Iniciar a criação de uma instância com nome `iceibank`.
3. Selecionar o broker **RabbitMQ**, exigido pelo roteiro. O provedor também
   oferece LavinMQ; verificar o produto selecionado.
4. Procurar o plano **Little Lemur**, indicado como gratuito no roteiro, e
   conferir preço e disponibilidade na tela atual antes de concluir.
   Se não houver opção gratuita de RabbitMQ, discutir a alternativa local.
5. Selecionar uma região disponível e concluir a criação da instância gratuita.
6. Abrir os detalhes da instância e acessar **RabbitMQ Manager**.
7. Identificar as áreas de exchanges, filas e conexões. Não é necessário criar
   filas manualmente neste primeiro passo.

Andamento: a conexão AMQP da aplicação e a topologia declarada pelo código foram
validadas em 04/10/2026. As capturas de tela do Manager continuam pendentes.

## Configuração local posterior

O roteiro usa `RABBITMQ_URL`. A URL da instância contém credenciais e deve
permanecer somente na configuração local, nunca em commits, prints ou no chat.
O projeto já ignora `agencia/.env`; preservar seu conteúdo existente ao adicionar
a variável. Não colocar a URL no frontend nem em variáveis `VITE_*`.

`Settings` lê a variável como `rabbitmq_url` e o projeto usa `pika`. Defina a URL
antes de iniciar cada uma das três agências:

```powershell
$env:RABBITMQ_URL="amqps://usuario:senha@host.cloudamqp.com/vhost"
$env:AGENCIA_ID="0" # repetir com 1 e 2 em terminais próprios
Set-Location agencia
.\.venv\Scripts\python.exe -m uvicorn iceibank.main:app --port 4045
```

Na inicialização, cada agência declara a exchange e a própria fila/binding. A
URL não deve ser registrada em evidências, commits ou frontend. Sem a variável,
o backend inicia para regressão local, mas transferência remota retorna 503.

## Topologia prevista no roteiro

- Exchange durável `iceibank.eventos`, tipo `topic`.
- Filas duráveis `fila-agencia-0`, `fila-agencia-1` e `fila-agencia-2`.
- Bindings com `agencia.0.creditar`, `agencia.1.creditar` e `agencia.2.creditar`.
- Mensagens persistentes; filas e bindings devem existir antes da publicação
  usada no teste de destino indisponível.

O código declara a topologia de forma reproduzível. O teste real de conexão está
registrado em `evidencias/sprint2/validacao-real.md`; falta apenas capturar as
evidências PNG exigidas.

## Referências

- [Guia oficial CloudAMQP para RabbitMQ](https://www.cloudamqp.com/docs/rabbitmq-server.html)
- [Detalhes da instância](https://www.cloudamqp.com/docs/cloudamqp-overview.html)
- [Planos do provedor](https://www.cloudamqp.com/plans.html)
- Roteiro da Sprint 2, seções 4.1 e 5.
- [Roadmap](../ROADMAP_SPRINT_2.md)
