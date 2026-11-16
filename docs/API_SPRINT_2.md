# Contrato da API - Sprint 2

## Status

Implementado e revisado em 11/10/2026. Complementa a API da Sprint 1 para o
fluxo remoto assíncrono e para Caixinhas; a rota HTTP legada de crédito remoto
não existe na execução vigente.

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
| PUT | `/contas/{contaId}/caixinhas/ordem` | Persiste a ordem visual com `{ "caixinhasIds": ["uuid-1", "uuid-2"] }`. A lista deve conter cada Caixinha da conta uma única vez. |
| GET | `/contas/{contaId}/caixinhas/{caixinhaId}` | Consulta uma Caixinha vinculada. |
| PATCH | `/contas/{contaId}/caixinhas/{caixinhaId}` | Atualiza nome e/ou cor, por exemplo `{ "nome": "Férias" }` ou `{ "cor": "azul" }`. |
| DELETE | `/contas/{contaId}/caixinhas/{caixinhaId}` | Aplica rendimento, resgata todo o saldo e exclui. |
| POST | `/contas/{contaId}/caixinhas/{caixinhaId}/guardar` | Debita conta e cria lote. |
| POST | `/contas/{contaId}/caixinhas/{caixinhaId}/resgatar` | Aplica rendimentos e resgata FIFO. |

Guardar e resgatar recebem `{ "valor": 10.00 }` e retornam a Caixinha atual e
`saldoConta`. A Caixinha inclui `rendimentoTotal` e o histórico `movimentos`,
com depósitos, retiradas e rendimentos. A Caixinha inclui a cor persistida `cor`;
novas Caixinhas usam `verde` por padrão e a atualização aceita `caramelo`,
`verde`, `azul`, `roxo` ou `coral`. O
`DELETE` retorna `saldoConta` e `valorResgatado`. Nomes têm de 1 a 80 caracteres após espaços externos e são
únicos por conta sem diferenciar maiúsculas. Os erros de domínio incluem
`CAIXINHA_NAO_ENCONTRADA`, `CAIXINHA_INVALIDA` e `SALDO_INSUFICIENTE`. A
resposta da Caixinha inclui `ordem`, usada pela listagem para manter a posição
definida pela pessoa usuária.

## Referências

- [SPEC-003](specs/SPEC-003-caixinha.md)
- [SPEC-004](specs/SPEC-004-mensageria-e-relogio-vetorial.md)
