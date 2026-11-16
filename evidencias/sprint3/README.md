# Evidências - Sprint 3

As quatro imagens presentes neste diretório foram capturadas em uma execução
real no emulador Android, em `2026-11-15T23:07:35-03:00`. Elas usam somente a
conta de teste `999999` ("Teste Sprint 3 Offline") e não foram geradas ou
montadas artificialmente.

| Arquivo | Situação | Cenário registrado |
|---|---|---|
| `eleicao-inicial.png` | Pendente | As três rotas `/bully/lider` convergindo para a Agência 2, com `Get-Date` visível no terminal. |
| `failover.png` | Pendente | Queda da líder e eleição automática da nova líder, com `Get-Date` visível no terminal. |
| `historico-lideranca.png` | Pendente | Saída de `python scripts/historico_lideranca.py`, com `Get-Date` visível no terminal. |
| `app-lider-atual.png` | Incluída | App conectado, Agência 2 como líder e saldo confirmado da conta de teste. |
| `app-failover.png` | Incluída | App detectando automaticamente a Agência 1 após a interrupção da líder Agência 2. |
| `conflito-sincronizacao.png` | Pendente | Resposta HTTP 409 do endpoint de sincronização, com `Get-Date` visível no terminal. |
| `app-offline.png` | Incluída | Depósito de R$ 7,50 registrado offline: saldo provisório R$ 107,50 e uma pendência. |
| `app-sincronizacao.png` | Incluída | Rede restaurada: fila zerada e saldo de R$ 107,50 confirmado pela agência. |

## Resultado observado

As três agências FastAPI foram executadas localmente. A eleição inicial
convergiu para a Agência 2. Ao interromper somente essa agência, as Agências 0
e 1 convergiram para a Agência 1 e o app atualizou o painel automaticamente. A
Agência 2 foi reiniciada ao final e as três voltaram a convergir para ela.

No teste offline-first, a rede do emulador foi desativada, o depósito foi
enfileirado localmente e, após a reconexão, sincronizado com sucesso. A consulta
direta ao backend confirmou o saldo final de R$ 107,50.
