# Contrato da API - Sprint 2

## Transferências

`POST /transferencias` continua exigindo JWT e recebe `idOrigem`, `idDestino` e
`valor`. Para contas de agências diferentes, uma resposta 200 é:

```json
{
  "mensagem": "Transferência publicada para a agência de destino (entrega assíncrona).",
  "tipo": "ENTRE_AGENCIAS"
}
```

Ela comprova publicação confirmada pelo broker, não o saldo já creditado no
destino. Se o RabbitMQ não estiver configurado ou confirmar falha, retorna 503
`MENSAGERIA_INDISPONIVEL` e a origem não é debitada. A rota HTTP interna de
crédito remoto foi removida.

## Caixinhas

Todas as rotas exigem JWT e a conta deve pertencer à agência atual.

| Método | Rota | Efeito |
|---|---|---|
| POST | `/contas/{contaId}/caixinhas` | Cria com `{ "nome": "Viagem" }`. |
| GET | `/contas/{contaId}/caixinhas` | Lista apenas as Caixinhas da conta. |
| GET | `/contas/{contaId}/caixinhas/{caixinhaId}` | Consulta uma Caixinha vinculada. |
| PATCH | `/contas/{contaId}/caixinhas/{caixinhaId}` | Renomeia com `{ "nome": "Férias" }`. |
| DELETE | `/contas/{contaId}/caixinhas/{caixinhaId}` | Exclui apenas quando o saldo é zero. |
| POST | `/contas/{contaId}/caixinhas/{caixinhaId}/guardar` | Debita conta e cria lote. |
| POST | `/contas/{contaId}/caixinhas/{caixinhaId}/resgatar` | Aplica rendimentos e resgata FIFO. |

Guardar e resgatar recebem `{ "valor": 10.00 }` e retornam a Caixinha atual e
`saldoConta`. Nomes têm de 1 a 80 caracteres após espaços externos e são únicos
por conta sem diferenciar maiúsculas. Os erros de domínio incluem
`CAIXINHA_NAO_ENCONTRADA`, `CAIXINHA_INVALIDA`, `CAIXINHA_COM_SALDO` e
`SALDO_INSUFICIENTE`.

## Referências

- [SPEC-003](specs/SPEC-003-caixinha.md)
- [SPEC-004](specs/SPEC-004-mensageria-e-relogio-vetorial.md)
