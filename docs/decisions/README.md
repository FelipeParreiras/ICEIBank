# Índice de decisões arquiteturais

| ADR | Decisão | Status |
|---|---|---|
| [ADR-001](ADR-001-stack-python-fastapi-react.md) | Python/FastAPI e React | Aceito |
| [ADR-002](ADR-002-funcionalidade-adicional-health-check.md) | Health-check como funcionalidade adicional | Substituído por ADR-004 |
| [ADR-003](ADR-003-autenticacao-e-comunicacao-interna.md) | JWT de usuário e credencial interna separada | Aceito |
| [ADR-004](ADR-004-controle-financeiro-mensal.md) | Controle financeiro mensal como funcionalidade adicional | Aceito |
| [ADR-005](ADR-005-proxy-vite-para-portas-das-agencias.md) | Proxy Vite preservando as portas 4045–4047 no Google Chrome | Aceito |
| [ADR-006](ADR-006-caixinha-lotes-fifo.md) | Caixinha por lotes e resgate FIFO | Aceito e implementado |
| [ADR-007](ADR-007-mensageria-rabbitmq-e-relogio-vetorial.md) | RabbitMQ durável e relógio vetorial | Aceito e implementado |
| [ADR-008](ADR-008-caixinha-tempo-arredondamento-e-exclusao.md) | Tempo, arredondamento e exclusão da Caixinha | Aceito e implementado |
| [ADR-009](ADR-009-exclusao-caixinha-com-resgate-automatico.md) | Exclusão com resgate automático | Aceito e implementado |

## Convenção

- Decisões novas recebem numeração sequencial.
- Uma decisão alterada não é apagada; um novo ADR deve substituí-la.
- O status de um ADR proposto só muda para aceito após concordância explícita ou validação durante a implementação.
- Documentos dependentes devem ser atualizados junto da mudança de status.
