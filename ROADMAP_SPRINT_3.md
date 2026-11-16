# Roadmap - Sprint 3

## Escopo implementado

- Eleição de líder com algoritmo Bully, mensagens de eleição/coordenador e
  heartbeat configurável.
- Histórico de eventos de liderança em `agencia/scripts/historico_lideranca.py`.
- Consulta de saldo com relógio vetorial e endpoint de sincronização que rejeita
  conflitos com HTTP 409.
- App Flutter em `app_mobile/` com fluxo bancário, painel de líder, cache local,
  fila offline e sincronização automática.

## Validação executada

- `53 passed` na suíte Python e `ruff check src tests` aprovado.
- `flutter analyze` e `flutter test` aprovados.
- Três agências reais iniciadas localmente: convergência inicial para a Agência
  2 e failover automático para a Agência 1 após a queda da líder.

## Pendências humanas de entrega

- Instalar/configurar Android SDK e emulador ou conectar dispositivo físico.
- Rodar o app em modo avião e capturar as evidências PNG reais exigidas pelo
  roteiro em `evidencias/sprint3/`.
- Revisar as respostas e a declaração de uso de IA antes da entrega acadêmica.
