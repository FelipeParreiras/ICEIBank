# Índice de decisões arquiteturais

| ADR | Decisão | Status |
|---|---|---|
| [ADR-001](ADR-001-stack-python-fastapi-react.md) | Python/FastAPI e React | Aceito |
| [ADR-002](ADR-002-funcionalidade-adicional-health-check.md) | Health-check como funcionalidade adicional | Substituído por ADR-004 |
| [ADR-003](ADR-003-autenticacao-e-comunicacao-interna.md) | JWT de usuário e credencial interna separada | Aceito |
| [ADR-004](ADR-004-controle-financeiro-mensal.md) | Controle financeiro mensal como funcionalidade adicional | Aceito |
| [ADR-005](ADR-005-proxy-vite-para-portas-das-agencias.md) | Proxy Vite preservando as portas 4045–4047 no Google Chrome | Aceito |

## Convenção

- Decisões novas recebem numeração sequencial.
- Uma decisão alterada não é apagada; um novo ADR deve substituí-la.
- O status de um ADR proposto só muda para aceito após concordância explícita ou validação durante a implementação.
- Documentos dependentes devem ser atualizados junto da mudança de status.
