# Documentação do ICEIBank

Este diretório centraliza a documentação técnica, operacional e acadêmica do projeto. As Sprints 1 e 2 estão implementadas; as capturas reais de evidência continuam como atividade de entrega separada.

## Estado atual

| Item | Estado |
|---|---|
| Python/FastAPI no backend | Aceito |
| React/Vite com JavaScript no frontend | Aceito |
| Offset 45 e portas 4045–4047 | Aceito |
| Controle Financeiro Mensal como funcionalidade adicional | Aceito |
| JWT de usuário e token interno separado | Aceito e implementado |
| Proxy Vite preservando 4045–4047 no Chrome | Aceito e implementado |
| Código da Sprint 1 | Implementado |
| Código da Sprint 2 | Implementado |
| Persistência local SQLite por agência | Aceito e implementado |
| Testes automatizados do estado atual | 45 aprovados; lint backend/frontend e build frontend aprovados |
| Evidências PNG e vídeo | Pendentes de captura para entrega |

## Como navegar

### Visão geral e planejamento

- [Estado atual do projeto](ESTADO_ATUAL_DO_PROJETO.md): funcionalidades,
  contratos, interface, limitações e situação de qualidade em 05/10/2026.
- [Roadmap da Sprint 2](../ROADMAP_SPRINT_2.md): escopo, implementação e pendências de evidência.
- [SPEC-003 — Caixinha](specs/SPEC-003-caixinha.md): regras e validações da funcionalidade adicional.
- [SPEC-004 — Mensageria e relógio vetorial](specs/SPEC-004-mensageria-e-relogio-vetorial.md): arquitetura distribuída da Sprint 2.
- [README principal](../README.md): apresentação e entrada do repositório.
- [Roadmap da Sprint 1](../ROADMAP_SPRINT_1.md): sequência de trabalho em três semanas.
- [SPEC-001 — Arquitetura da Sprint 1](specs/SPEC-001-arquitetura-sprint-1.md): arquitetura, componentes, fluxos e restrições.
- [SPEC-002 — Controle Financeiro Mensal](specs/SPEC-002-controle-financeiro-mensal.md): meta, gastos, recomendações e limites do extra.

### Implementação

- [Configuração da Sprint 2](CONFIGURACAO_SPRINT_2.md): RabbitMQ e execução das agências.
- [Guia de desenvolvimento](GUIA_DE_DESENVOLVIMENTO.md): responsabilidades, convenções e fluxo de trabalho.
- [Plano de commits](PLANO_DE_COMMITS_SPRINT_1.md): mensagens, arquivos, testes e evidências previstos por commit.
- [Blueprint do backend FastAPI](BACKEND_FASTAPI.md): ciclo de vida, interfaces, dependências e concorrência.
- [Blueprint do frontend React](FRONTEND_REACT.md): estado, componentes, fluxos e erros.
- [Paleta de cores](PALETA_DE_CORES.md): tokens visuais, usos e regras de contraste.
- [Contrato da API](API_SPRINT_1.md): endpoints, corpos, respostas e erros.
- [Contrato da API Sprint 2](API_SPRINT_2.md): mensageria e Caixinhas.
- [Configuração e execução](CONFIGURACAO_E_EXECUCAO.md): variáveis, portas, proxy e comandos validados.
- [Segurança](SEGURANCA.md): JWT, credencial interna, CORS, segredos e limitações.
- [Lamport e observabilidade](LAMPORT_E_OBSERVABILIDADE.md): referência
  histórica da Sprint 1; a implementação atual usa relógio vetorial.

### Qualidade e entrega

- [Requisitos e rastreabilidade](REQUISITOS_E_RASTREABILIDADE_SPRINT_1.md): ligação entre roteiro, arquitetura, testes e nota.
- [Plano de testes e evidências](PLANO_DE_TESTES_E_EVIDENCIAS.md): cenários, massa de dados e prints obrigatórios.
- [Guia de entrega e vídeo](ENTREGA_E_VIDEO.md): auditoria final, Git e roteiro de apresentação.
- [Glossário](GLOSSARIO.md): conceitos e termos usados no projeto.
- [RESPOSTAS.md](../RESPOSTAS.md): estrutura das respostas conceituais e decisões solicitadas.

### Decisões arquiteturais

- [ADR-006 — Caixinha por lotes e resgate FIFO](decisions/ADR-006-caixinha-lotes-fifo.md) — Aceito e implementado.
- [ADR-007 — Mensageria e relógio vetorial](decisions/ADR-007-mensageria-rabbitmq-e-relogio-vetorial.md) — Aceito e implementado.
- [ADR-008 — Tempo e exclusão da Caixinha](decisions/ADR-008-caixinha-tempo-arredondamento-e-exclusao.md) — Aceito e implementado.
- [ADR-009 — Exclusão com resgate automático](decisions/ADR-009-exclusao-caixinha-com-resgate-automatico.md) — Aceito e implementado.
- [ADR-010 — Persistência SQLite por agência](decisions/ADR-010-persistencia-sqlite-por-agencia.md) — Aceito e implementado.
- [Índice de ADRs](decisions/README.md)
- [ADR-001 — Python/FastAPI e React](decisions/ADR-001-stack-python-fastapi-react.md) — Aceito.
- [ADR-002 — Health-check adicional](decisions/ADR-002-funcionalidade-adicional-health-check.md) — Substituído.
- [ADR-003 — JWT e comunicação interna](decisions/ADR-003-autenticacao-e-comunicacao-interna.md) — Aceito.
- [ADR-004 — Controle Financeiro Mensal](decisions/ADR-004-controle-financeiro-mensal.md) — Aceito.
- [ADR-005 — Proxy Vite para as portas das agências](decisions/ADR-005-proxy-vite-para-portas-das-agencias.md) — Aceito.

## Ordem recomendada de leitura

Para implementar:

1. roadmap;
2. SPEC-001;
3. ADRs;
4. guia de desenvolvimento;
5. plano de commits;
6. contrato da API;
7. configuração e execução;
8. plano de testes.

Para revisar a entrega:

1. requisitos e rastreabilidade;
2. plano de testes e evidências;
3. `RESPOSTAS.md`;
4. guia de entrega e vídeo.

## Hierarquia das fontes

Em caso de divergência, utilizar esta ordem:

1. roteiro oficial fornecido pelos professores;
2. ADR aceito mais recente;
3. SPEC vigente;
4. contrato da API e guias especializados;
5. README e comentários de código.

Uma mudança de decisão não deve apagar seu histórico. Ela exige um novo ADR que substitua o anterior e a atualização dos documentos dependentes.

## Regra de honestidade documental

- **Planejado** descreve o comportamento que será implementado.
- **Implementado** só pode ser usado depois de existir código verificável.
- **Validado** só pode ser usado depois de teste executado e registrado.
- Respostas baseadas em observação permanecem com marcador até os testes reais.
- Evidências devem ser capturas reais de execução; não podem ser substituídas por exemplos deste documento.
