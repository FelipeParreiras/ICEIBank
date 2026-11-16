# Registro de execução real - 05/10/2026

## Escopo

Registro complementar às capturas exigidas no roteiro da Sprint 2. Esta rodada
usou as três agências locais, a instância RabbitMQ configurada no ambiente e o
frontend em `http://127.0.0.1:5173`. Tokens, URL AMQP, usuário e senha não foram
gravados.

Os arquivos JSONL citados abaixo são os logs reais produzidos pela aplicação. As
capturas PNG requeridas pelo roteiro continuam pendentes porque devem mostrar o
terminal com `Get-Date` visível, além do comportamento executado.

## Transferência assíncrona

- Data/hora local: `2026-10-05T15:12:27-03:00`.
- Conta 90, Agência 0: criada com R$ 200,00.
- Conta 91, Agência 1: criada com R$ 10,00.
- Transferência 90 -> 91 de R$ 30,00: HTTP 200, tipo `ENTRE_AGENCIAS` e
  confirmação de publicação assíncrona.
- Após o consumo: origem R$ 170,00 e destino R$ 40,00.
- Eventos observados:
  - `TRANSFERENCIA_DEBITO`, Agência 0, vetor `[2, 0, 0]`;
  - `TRANSFERENCIA_CREDITO_REMOTO`, Agência 1, vetor `[2, 2, 0]`.
- Logs: `agencia/data/eventos-agencia-0.jsonl` e
  `agencia/data/eventos-agencia-1.jsonl`.

Captura ainda necessária: `transferencia-assincrona.png`, com as duas agências,
os logs acima e `Get-Date` visíveis.

## Resiliência da fila

- Data/hora local da publicação: `2026-10-05T15:13:53-03:00`.
- A Agência 1 foi interrompida antes da transferência 90 -> 91 de R$ 20,00.
- A publicação retornou HTTP 200 e tipo `ENTRE_AGENCIAS` mesmo sem consumidor
  ativo; a conta de origem passou de R$ 170,00 para R$ 150,00.
- A Agência 1 voltou a responder HTTP 200 às `2026-10-05T15:14:15-03:00`.
- O broker entregou a mensagem após o reinício, e o consumidor registrou
  `CREDITO_REMOTO_FALHOU`, vetor `[3, 1, 0]`, conta 91 e motivo
  `CONTA_NAO_ENCONTRADA`.
- O resultado confirma a retenção da mensagem e também a limitação esperada:
  a conta foi perdida porque permanece apenas em memória.

Captura ainda necessária: `resiliencia-fila.png`, mostrando o destino parado, a
publicação confirmada e o evento de falha após o retorno.

## Linha do tempo causal

- Data/hora local da execução do mesclador:
  `2026-10-05T15:12:37-03:00`.
- O comando `python scripts/mesclar_logs.py` identificou como concorrentes as
  criações independentes `[1, 0, 0]` da Agência 0 e `[0, 1, 0]` da Agência 1.
- O débito `[2, 0, 0]` da transferência 90 -> 91 não é concorrente do crédito
  remoto `[2, 2, 0]`, pois o primeiro vetor é menor ou igual ao segundo em todas
  as posições e estritamente menor na posição da Agência 1.

Captura ainda necessária: `linha-do-tempo-causal.png`, mostrando o bloco de pares
concorrentes do mesclador e `Get-Date`.

## Funcionalidade adicional - Caixinha

- Data/hora local: `2026-10-05T15:14:44-03:00`.
- Conta 92, Agência 2: criada com R$ 500,00.
- Caixinha `Reserva de evidência`: criada com a cor padrão `verde`.
- Depósito de R$ 120,00: conta R$ 380,00 e Caixinha R$ 120,00.
- Resgate de R$ 20,00: conta R$ 400,00 e Caixinha R$ 100,00.
- A consulta final retornou dois movimentos e os eventos
  `CRIAR_CAIXINHA`, `GUARDAR_CAIXINHA` e `RESGATAR_CAIXINHA` nos vetores
  `[0, 0, 7]`, `[0, 0, 8]` e `[0, 0, 9]`.
- Log: `agencia/data/eventos-agencia-2.jsonl`.

Captura ainda necessária: `caixinha.png`, mostrando o card/modal com saldo,
histórico e operações, além de data/hora visível em terminal.

## Regressão automatizada

- `ruff check src tests`: aprovado.
- `pytest tests`: 41 aprovados.
- `npm run lint`: aprovado.
- `npm run build`: aprovado.

## Rastreabilidade

- Commit da árvore no início da rodada: `bcefe11`.
- A evidência deve ser revisada antes da entrega, confrontando os valores acima
  com os JSONL e com os PNGs finais.
