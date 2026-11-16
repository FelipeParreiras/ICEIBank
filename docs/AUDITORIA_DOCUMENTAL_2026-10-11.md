# Auditoria documental — 11/10/2026

## Objetivo

Consolidar a documentação das Sprints 1 e 2 com o estado verificável do
repositório, distinguindo claramente a baseline histórica da Sprint 1 do fluxo
operacional atual. Esta auditoria não transforma evidências planejadas em
evidências entregues: capturas PNG e vídeo continuam pendentes.

## Base verificada

- Backend: `agencia/src/iceibank`, incluindo SQLite por agência, RabbitMQ,
  relógio vetorial, Caixinhas e controle financeiro.
- Frontend: `frontend/src`, incluindo marca oficial, tema verde/dourado,
  `SelectField` próprio e variante rolável de categorias.
- Qualidade executada nesta revisão:
  - `agencia/.venv/Scripts/python.exe -m pytest -q`: **45 testes aprovados**;
  - `agencia/.venv/Scripts/python.exe -m ruff check src tests`: **aprovado**;
  - em `frontend`: `npm run lint` e `npm run build`: **aprovados**.

`ruff check .` não é declarado como aprovado nesta auditoria: o escopo de
qualidade documentado é `src tests`; há pendências de estilo no script histórico
`agencia/scripts/mesclar_logs.py` se ele for incluído na verificação ampla.

## Fontes de verdade revisadas

| Grupo | Estado após a auditoria | Referência principal |
|---|---|---|
| Arquitetura da Sprint 1 | Mantida como baseline histórica; Lamport e HTTP remoto não são fluxo ativo | [SPEC-001](specs/SPEC-001-arquitetura-sprint-1.md) |
| Controle financeiro | Implementado com categorias ordenadas, débito atômico e SQLite | [SPEC-002](specs/SPEC-002-controle-financeiro-mensal.md) |
| Caixinhas | Implementadas com lotes FIFO, rendimento sob demanda, cor, ordem e resgate na exclusão | [SPEC-003](specs/SPEC-003-caixinha.md) |
| Mensageria | Implementada com RabbitMQ, publisher confirm e relógio vetorial | [SPEC-004](specs/SPEC-004-mensageria-e-relogio-vetorial.md) |
| Decisões | ADRs 001–010 revisados; substituições explícitas preservadas | [Índice de ADRs](decisions/README.md) |
| API | Sprint 1 identificada como histórica nos pontos substituídos; Sprint 2 descreve o fluxo atual | [API Sprint 1](API_SPRINT_1.md), [API Sprint 2](API_SPRINT_2.md) |
| Operação e qualidade | Portas, proxy, SQLite, comandos de validação e limitações revisados | [Configuração](CONFIGURACAO_E_EXECUCAO.md), [Testes](PLANO_DE_TESTES_E_EVIDENCIAS.md) |
| Frontend e identidade | Componentes, acessibilidade de marca, paleta e interação de selects registrados | [Frontend](FRONTEND_REACT.md), [Paleta](PALETA_DE_CORES.md) |

## Relações entre decisões

1. O ADR-001 mantém Python/FastAPI e React/Vite como stack vigente.
2. O ADR-003 continua valendo para JWT, mas seu trecho de crédito remoto HTTP
   foi substituído pelo ADR-007.
3. O ADR-004 define o controle financeiro; o ADR-010 passou a fornecer sua
   persistência local.
4. O ADR-006 define lotes e FIFO; ADR-008 define tempo/arredondamento; ADR-009
   substitui apenas a exclusão protegida por resgate automático; ADR-010 torna
   o estado das Caixinhas durável no SQLite local.
5. A SPEC-004 é a fonte de verdade para transferência remota atual. A SPEC-001
   permanece necessária para explicar a evolução e requisitos da Sprint 1.

## Regras de manutenção

- Não reescrever evidências históricas como se fossem execuções atuais.
- Marcar documentos de Sprint 1 que descrevem Lamport ou crédito HTTP como
  históricos e apontar para a SPEC-004.
- Alterações de arquitetura exigem novo ADR, sem apagar decisões substituídas.
- Alterações de contrato devem atualizar a SPEC correspondente, a API, testes,
  o documento de estado atual e o guia de execução quando afetarem operação.
- Só declarar uma validação após executar e registrar o comando e o resultado.

## Pendências honestas

- Capturar e salvar os PNGs e o vídeo de entrega exigidos pelos roteiros.
- Corrigir o lint amplo de `agencia/scripts/mesclar_logs.py` antes de mudar a
  declaração de qualidade de `ruff check src tests` para `ruff check .`.
- RabbitMQ real foi validado em 04/10/2026; esta auditoria não repetiu essa
  conexão nem substitui suas evidências reais.

## Referências

- [Estado atual do projeto](ESTADO_ATUAL_DO_PROJETO.md)
- [Índice de documentação](README.md)
- [Índice de ADRs](decisions/README.md)
- [Plano de testes e evidências](PLANO_DE_TESTES_E_EVIDENCIAS.md)
