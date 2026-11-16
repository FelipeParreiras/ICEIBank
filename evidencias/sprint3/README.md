# Evidências - Sprint 3

As imagens abaixo devem ser capturadas em execução real, com `Get-Date` visível
em algum terminal. Não foram geradas artificialmente.

| Arquivo | Cenário a registrar |
|---|---|
| `eleicao-inicial.png` | As três rotas `/bully/lider` convergindo para a Agência 2. |
| `failover.png` | Queda da líder e eleição automática da nova líder. |
| `historico-lideranca.png` | Saída de `python scripts/historico_lideranca.py`. |
| `app-lider-atual.png` | Painel Flutter com a líder atual. |
| `app-failover.png` | Painel Flutter atualizando sem interação após o failover. |
| `conflito-sincronizacao.png` | Resposta HTTP 409 do endpoint de sincronização. |
| `app-offline.png` | Operação otimista pendente com o dispositivo offline. |
| `app-sincronizacao.png` | Fila sendo sincronizada automaticamente após reconectar. |

O backend foi validado localmente com três processos FastAPI isolados: a eleição
convergiu para a Agência 2 e, após sua interrupção, as duas restantes elegeram a
Agência 1. As capturas do app exigem Android SDK + emulador ou dispositivo físico.
