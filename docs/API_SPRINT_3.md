# Contrato da API - Sprint 3

## Consenso Bully

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| `POST` | `/bully/eleicao` | `origemId`, `vetorEnvio` | `200` confirma que a agência maior está ativa. |
| `POST` | `/bully/coordenador` | `liderId`, `vetorEnvio` | `200` após registrar a líder anunciada. |
| `GET` | `/bully/lider` | - | `{ "idAgencia": 0, "liderAtual": 2 }`. |

As rotas de consenso não exigem JWT porque representam comunicação entre
agências e o painel informativo do aplicativo. O algoritmo converge para a
agência ativa de maior ID; o heartbeat usa o intervalo configurado por
`HEARTBEAT_INTERVALO_SEGUNDOS`.

## Sincronização offline-first

`GET /contas/{id}` continua exigindo JWT e agora inclui o vetor do relógio da
agência:

```json
{ "id": 0, "nomeAluno": "Ana", "saldo": 100.0, "vetorAtual": [1, 0, 0] }
```

`POST /contas/{id}/sincronizar` exige JWT e recebe:

```json
{ "tipo": "DEPOSITO", "valor": 20.0, "vetorConhecido": [1, 0, 0] }
```

Os tipos aceitos são `DEPOSITO` e `SAQUE`. Se o vetor conhecido divergir do
vetor atual, a API retorna `409 CONFLITO_SINCRONIZACAO` com `vetorConhecido`,
`vetorAtual` e `contaAtual`; nenhuma operação é aplicada nesse caso.
