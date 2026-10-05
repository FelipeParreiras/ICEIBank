# ADR-004: Controle financeiro mensal como funcionalidade adicional

## Status

Aceito

## Data

2026-09-07

## Contexto

O roteiro exige uma funcionalidade adicional com comportamento novo, evidência, documentação e commit próprio. O health-check havia sido proposto por baixo risco, mas o aluno escolheu uma funcionalidade com maior valor para o domínio bancário: controlar gastos, definir uma meta de economia mensal e indicar onde reduzir despesas.

A escolha precisa permanecer viável dentro da Sprint 1, que já inclui API, Lamport, transferências, JWT e React. Por isso, o controle financeiro será um MVP determinístico, e não um produto completo de finanças pessoais.

## Decisão

Implementar um Controle Financeiro Mensal por conta com:

- planejamento de renda prevista e meta de economia para uma competência mensal;
- limite mensal de gasto calculado a partir da meta;
- limites opcionais por categoria e indicação das categorias flexíveis;
- registro de gastos categorizados;
- resumo do total gasto, economia projetada e distância da meta;
- recomendações transparentes de redução por categoria;
- visualização no frontend React;
- eventos vetoriais para alterações do planejamento e registros de gastos;
- estado local na agência responsável pela conta; a persistência SQLite foi
  adicionada posteriormente pelo ADR-010.

As recomendações serão produzidas por regras matemáticas explicáveis. A funcionalidade não chamará um modelo de IA ou serviço externo.

### Evolução de categorias

O catálogo fixo foi substituído por categorias gerenciadas no próprio planejamento mensal. Essa evolução preserva o caráter determinístico: cada planejamento persiste a lista ordenada `categoriasOrdenadas`; a primeira posição é a mais importante e só é usada para desempatar recomendações com o mesmo impacto financeiro. A mudança permite personalização sem introduzir dependência externa ou alterar gastos já registrados.

## Alternativas consideradas

### Health-check por agência

- Prós: baixo risco e fácil demonstração.
- Contras: menor valor percebido para a pessoa usuária do banco.
- Motivo da substituição: o aluno preferiu uma funcionalidade diretamente ligada à gestão financeira.

### Assistente financeiro com IA generativa

- Prós: recomendações em linguagem natural e maior flexibilidade.
- Contras: exige serviço externo, credenciais, custos, tratamento de privacidade e comportamento não determinístico.
- Motivo da rejeição: desvia dos conceitos avaliados e aumenta muito o risco da sprint.

### Sistema financeiro completo

- Prós: poderia incluir recorrências, gráficos históricos, múltiplas metas e previsão futura.
- Contras: escopo incompatível com uma funcionalidade adicional de uma sprint já extensa.
- Motivo da rejeição: esses itens ficam como evolução futura.

## Consequências

- A funcionalidade adicional passa a exigir modelos, repositório, serviço, controller, componentes React e testes próprios.
- O commit do extra será maior que o antigo health-check, mas continuará isolado.
- O aluno precisará explicar o algoritmo de recomendação e suas limitações.
- Gastos e planejamentos serão perdidos quando a agência reiniciar, como as contas da Sprint 1.
- A implementação deve evitar que o extra atrase os requisitos que valem 19 pontos.
- Registrar um gasto debita o saldo da conta atomicamente com a inclusão no repositório financeiro, conforme implementado na SPEC-002.

## Referências

- [SPEC-002](../specs/SPEC-002-controle-financeiro-mensal.md)
- [ADR-002 substituído](ADR-002-funcionalidade-adicional-health-check.md)
- [Plano de commits](../PLANO_DE_COMMITS_SPRINT_1.md)
- Seção 2.1 do roteiro da Sprint 1.
