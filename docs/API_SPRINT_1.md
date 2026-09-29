# Contrato da API — Sprint 1

## Status

Contrato implementado e coberto pelos testes de integração da Sprint 1.

## Convenções

- Conteúdo: `application/json`.
- Campos JSON: `camelCase`, acompanhando o roteiro.
- Nomes Python internos: `snake_case`, usando aliases Pydantic na fronteira HTTP.
- Valores monetários no JSON: números com no máximo duas casas decimais.
- Valores monetários no domínio: `Decimal`.
- Datas: ISO-8601 em UTC.
- Autenticação de usuário: `Authorization: Bearer <JWT>`.
- Autenticação interna: `X-ICEIBANK-INTERNAL-TOKEN: <token>`.
- A agência de uma conta é `id % 3`.

## URLs-base

| Agência | URL |
|---|---|
| 0 | `http://localhost:4045` |
| 1 | `http://localhost:4046` |
| 2 | `http://localhost:4047` |

## Formato de erro

Erros de domínio e infraestrutura devem usar:

```json
{
  "erro": "Conta não encontrada nesta agência.",
  "codigo": "CONTA_NAO_ENCONTRADA",
  "detalhes": null
}
```

`detalhes` é opcional e nunca deve conter senha, JWT ou token interno.

Erros estruturais de validação podem incluir a lista de campos inválidos, mantendo uma mensagem principal compreensível pelo frontend.

## Autenticação

### `POST /auth/login`

Autentica usuários cadastrados ou o usuário de demonstração configurado por ambiente.
As agências 1 e 2 encaminham a autenticação para a agência 0; não mantêm cópias das senhas.

Requisição:

```json
{
  "usuario": "aluno",
  "senha": "senha-informada-localmente"
}
```

Resposta 200:

```json
{
  "accessToken": "eyJ...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```

Erros:

- 401 `CREDENCIAIS_INVALIDAS`.
- 422 `REQUISICAO_INVALIDA`.

O endpoint não deve informar se foi o usuário ou a senha que falhou.

Se a agência 0 não responder, as agências 1 e 2 retornam 503 `AUTENTICACAO_INDISPONIVEL`.

### `POST /auth/cadastro`

Rota pública disponível nas três agências. Cria credenciais e retorna 201 com o mesmo
`TokenResponse` do login, iniciando a sessão. Não cria conta bancária.

```json
{
  "usuario": "ana.silva",
  "senha": "senha-de-exemplo-123",
  "confirmarSenha": "senha-de-exemplo-123"
}
```

- Usuário: 3 a 100 caracteres, somente letras ASCII, números, ponto, hífen e sublinhado.
  A comparação distingue maiúsculas de minúsculas; não remove espaços nem altera o nome.
- Senha: 8 a 256 caracteres, não pode conter apenas espaços; confirmação deve ser idêntica.
- 400 `CADASTRO_INVALIDO`: confirmação divergente ou senha composta apenas de espaços.
- 409 `USUARIO_JA_EXISTE`: nome ocupado, inclusive pelo usuário de demonstração.
- 422 `REQUISICAO_INVALIDA`: formato, campos obrigatórios ou limites inválidos.
- 503 `AUTENTICACAO_INDISPONIVEL`: agência 0 indisponível ao encaminhar a requisição.

A agência 0 mantém usuários em memória com inserção atômica e senha em hash PBKDF2.
Reiniciá-la apaga os cadastros. As agências 1 e 2 encaminham cadastro e login por HTTP;
JWTs são aceitos pelas três instâncias. Nenhuma resposta de validação de autenticação
inclui os valores recebidos de senha ou confirmação. Cadastro e login não alteram
saldo nem o relógio de Lamport das operações bancárias.

## Contas

### `GET /contas`

Proteção: JWT. Retorna 200 com a lista de contas da agência consultada, ordenada por ID.
Cada item contém `id`, `nomeAluno` e `saldo`, como na consulta individual.
Uma agência sem contas retorna `[]`. A consulta não incrementa o relógio de Lamport.
O frontend consulta as três agências e agrupa suas contas nos seletores de origem e
destino da transferência. A requisição é enviada à agência da conta de origem. Nos
formulários de depósito e saque, a conta é definida automaticamente pela consulta
exibida no painel, evitando operar em uma conta diferente por engano. As listas são
recarregadas ao trocar de agência, criar uma conta ou clicar em **Atualizar contas**.
Falhas de uma agência são exibidas sem descartar as contas das demais.

### `POST /contas`

Cria uma conta na agência responsável.

Proteção: JWT.

Requisição:

```json
{
  "id": 0,
  "nomeAluno": "Ana",
  "saldoInicial": 200.00
}
```

Resposta 201:

```json
{
  "id": 0,
  "nomeAluno": "Ana",
  "saldo": 200.00
}
```

Regras:

- `id` inteiro e não negativo;
- `nomeAluno` obrigatório após remover espaços externos;
- `saldoInicial` opcional, padrão zero e nunca negativo;
- a agência atual deve ser `id % 3`;
- o ID não pode existir na agência.

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 401 `NAO_AUTENTICADO`.
- 409 `CONTA_JA_EXISTE`.
- 422 `REQUISICAO_INVALIDA`.

### `GET /contas/{id}`

Consulta a conta armazenada na agência atual.

Proteção: JWT.

Resposta 200:

```json
{
  "id": 0,
  "nomeAluno": "Ana",
  "saldo": 200.00
}
```

Erros:

- 400 `CONTA_FORA_DA_PARTICAO` quando o ID pertence a outra agência.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 422 `ID_INVALIDO`.

### `POST /contas/{id}/depositar`

Proteção: JWT.

Requisição:

```json
{
  "valor": 25.50
}
```

Resposta 200:

```json
{
  "id": 0,
  "nomeAluno": "Ana",
  "saldo": 225.50
}
```

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 400 `VALOR_INVALIDO`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 422 `REQUISICAO_INVALIDA`.

### `POST /contas/{id}/sacar`

Proteção: JWT.

Requisição:

```json
{
  "valor": 20.00
}
```

Resposta 200:

```json
{
  "id": 0,
  "nomeAluno": "Ana",
  "saldo": 205.50
}
```

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 400 `VALOR_INVALIDO`.
- 400 `SALDO_INSUFICIENTE`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 422 `REQUISICAO_INVALIDA`.

## Transferências

### `POST /transferencias`

O cliente chama sempre a agência responsável pela conta de origem. O backend decide se a transferência é local ou remota.

Proteção: JWT.

Requisição:

```json
{
  "idOrigem": 0,
  "idDestino": 1,
  "valor": 30.00
}
```

Resposta 200 local:

```json
{
  "mensagem": "Transferência concluída (mesma agência).",
  "tipo": "LOCAL"
}
```

Resposta 200 remota:

```json
{
  "mensagem": "Transferência concluída (entre agências).",
  "tipo": "ENTRE_AGENCIAS"
}
```

Regras:

- origem e destino diferentes;
- valor maior que zero;
- origem pertence à agência chamada;
- origem existe e possui saldo;
- destino local é validado antes de qualquer mutação;
- no fluxo remoto, o débito ocorre antes da chamada ao destino, conforme o roteiro.

Erros:

- 400 `CONTA_ORIGEM_FORA_DA_PARTICAO`.
- 400 `VALOR_INVALIDO`.
- 400 `SALDO_INSUFICIENTE`.
- 400 `CONTAS_IGUAIS`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_ORIGEM_NAO_ENCONTRADA`.
- 404 `CONTA_DESTINO_NAO_ENCONTRADA` no fluxo local.
- 502 `AGENCIA_DESTINO_INDISPONIVEL` no fluxo remoto.

Resposta 502 esperada:

```json
{
  "erro": "Falha ao contatar agência de destino. Débito já aplicado — inconsistência conhecida da Sprint 1.",
  "codigo": "AGENCIA_DESTINO_INDISPONIVEL",
  "detalhes": {
    "debitoRevertido": false
  }
}
```

Essa resposta não representa um bug a ser corrigido nesta sprint. Ela documenta a limitação que será tratada com transações distribuídas na Sprint 4.

### `POST /contas/{id}/creditar-remoto`

Rota de uso exclusivo entre agências.

Proteção: token interno.

Requisição:

```json
{
  "valor": 30.00,
  "timestampLamport": 7,
  "origemAgencia": 0
}
```

Resposta 200:

```json
{
  "mensagem": "Crédito remoto aplicado.",
  "saldoAtual": 110.00
}
```

Ordem obrigatória:

1. validar token interno e estrutura da mensagem;
2. executar `ao_receber(timestampLamport)`;
3. localizar a conta local;
4. aplicar o crédito;
5. registrar `TRANSFERENCIA_CREDITO_REMOTO` com o timestamp resultante.

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 400 `VALOR_INVALIDO`.
- 401 `TOKEN_INTERNO_INVALIDO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 422 `REQUISICAO_INVALIDA`.

## Funcionalidade adicional — Controle Financeiro Mensal

As três rotas exigem JWT e operam somente na agência responsável pela conta.

### `PUT /contas/{id}/controle-financeiro/{competencia}/planejamento`

Cria ou substitui o planejamento da conta no mês `AAAA-MM`.

Requisição:

```json
{
  "rendaPrevista": 500.00,
  "metaEconomia": 100.00,
  "limitesPorCategoria": {
    "ALIMENTACAO": 150.00,
    "TRANSPORTE": 100.00,
    "DELIVERY": 80.00,
    "LAZER": 70.00
  },
  "categoriasFlexiveis": ["DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"]
}
```

Resposta 200:

```json
{
  "contaId": 6,
  "competencia": "2026-09",
  "rendaPrevista": 500.00,
  "metaEconomia": 100.00,
  "limiteGastoMensal": 400.00,
  "limitesPorCategoria": {
    "ALIMENTACAO": 150.00,
    "TRANSPORTE": 100.00,
    "DELIVERY": 80.00,
    "LAZER": 70.00
  },
  "categoriasFlexiveis": ["DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"]
}
```

Regras:

- renda maior que zero;
- meta entre zero e a renda;
- competência válida;
- limites não negativos e categorias reconhecidas;
- soma dos limites por categoria não superior ao limite mensal;
- atualização não apaga gastos existentes;
- registrar `DEFINIR_PLANEJAMENTO_MENSAL` com evento local.

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 400 `PLANEJAMENTO_INVALIDO`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 422 `REQUISICAO_INVALIDA`.

### `POST /contas/{id}/controle-financeiro/gastos`

Registra um gasto e, conforme a decisão aceita na SPEC-002, debita o saldo da conta atomicamente.

Requisição:

```json
{
  "descricao": "Pedido de jantar",
  "valor": 40.00,
  "categoria": "DELIVERY",
  "data": "2026-09-12"
}
```

Resposta 201:

```json
{
  "gasto": {
    "id": "a9861c72-28f1-4b77-87c7-3ad809713082",
    "contaId": 6,
    "descricao": "Pedido de jantar",
    "valor": 40.00,
    "categoria": "DELIVERY",
    "data": "2026-09-12",
    "competencia": "2026-09"
  },
  "saldoConta": 960.00
}
```

Regras:

- planejamento da competência deve existir;
- valor positivo com até duas casas;
- categoria pertencente ao catálogo;
- saldo suficiente;
- gasto e débito são uma única operação local;
- registrar `REGISTRAR_GASTO` com novo saldo.

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 400 `VALOR_INVALIDO`.
- 400 `SALDO_INSUFICIENTE`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 404 `PLANEJAMENTO_NAO_ENCONTRADO`.
- 422 `REQUISICAO_INVALIDA`.

### `GET /contas/{id}/controle-financeiro/{competencia}`

Consulta planejamento, gastos, totais e recomendações. A operação não incrementa Lamport.

Resposta 200 resumida:

```json
{
  "contaId": 6,
  "competencia": "2026-09",
  "rendaPrevista": 500.00,
  "metaEconomia": 100.00,
  "limiteGastoMensal": 400.00,
  "totalGasto": 450.00,
  "economiaProjetada": 50.00,
  "saldoParaGastar": 0.00,
  "valorAjuste": 50.00,
  "status": "AJUSTE_NECESSARIO",
  "totaisPorCategoria": {
    "ALIMENTACAO": 150.00,
    "TRANSPORTE": 80.00,
    "DELIVERY": 120.00,
    "LAZER": 100.00
  },
  "recomendacoes": [
    {
      "categoria": "DELIVERY",
      "reducaoSugerida": 40.00,
      "motivo": "ACIMA_DO_LIMITE"
    },
    {
      "categoria": "LAZER",
      "reducaoSugerida": 10.00,
      "motivo": "ACIMA_DO_LIMITE"
    }
  ],
  "valorNaoCoberto": 0.00
}
```

A resposta completa também inclui a lista `gastos`; ela foi omitida desse exemplo resumido para destacar os cálculos e as recomendações.

Erros:

- 400 `CONTA_FORA_DA_PARTICAO`.
- 401 `NAO_AUTENTICADO`.
- 404 `CONTA_NAO_ENCONTRADA`.
- 404 `PLANEJAMENTO_NAO_ENCONTRADO`.
- 422 `COMPETENCIA_INVALIDA`.

O algoritmo e o catálogo de categorias estão definidos na [SPEC-002](specs/SPEC-002-controle-financeiro-mensal.md).

## Códigos de autenticação

As três situações obrigatórias usam HTTP 401:

- token ausente: `TOKEN_AUSENTE`;
- assinatura/formato inválido: `TOKEN_INVALIDO`;
- token expirado: `TOKEN_EXPIRADO`.

O frontend pode personalizar a mensagem a partir do campo `codigo`, limpar o token e retornar ao login.

## OpenAPI

FastAPI fornecerá documentação interativa automaticamente. Ela é útil para exploração, mas não substitui este documento, que também registra decisões, limitações e semântica distribuída.

## Referências

- [SPEC-001](specs/SPEC-001-arquitetura-sprint-1.md)
- [Segurança](SEGURANCA.md)
- [Lamport e observabilidade](LAMPORT_E_OBSERVABILIDADE.md)
