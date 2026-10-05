# SPEC-002: Controle financeiro mensal

## Status

Implementado. Registrar gasto debita o saldo da conta na mesma seção crítica usada pelo repositório financeiro.

## Objetivo

Permitir que uma pessoa defina quanto pretende economizar em um mês, registre gastos por categoria e receba um diagnóstico objetivo de onde reduzir despesas para alcançar a meta.

Exemplo: para uma renda prevista de R$ 500,00 e meta de economia de R$ 100,00, o limite total de gasto do mês é R$ 400,00. Se os gastos chegarem a R$ 450,00, o sistema informa uma economia projetada de R$ 50,00 e recomenda cortes que somem pelo menos os R$ 50,00 faltantes.

## Escopo

### Incluído no MVP

- um planejamento por conta e competência `AAAA-MM`;
- renda prevista mensal;
- meta de economia mensal;
- limites opcionais por categoria;
- categorias marcadas como flexíveis;
- criação, remoção e ordenação de prioridade de categorias pelo planejamento;
- registro de gasto com descrição, valor, categoria e data;
- listagem dos gastos da competência no resumo;
- cálculo de limite mensal, total gasto, economia projetada e valor faltante;
- recomendações determinísticas de redução;
- débito do valor registrado no saldo da conta;
- eventos Lamport para planejamento e gasto;
- API protegida por JWT;
- interface React;
- armazenamento em memória na agência da conta;
- evidência e commit próprios.

### Fora do escopo

- banco de dados ou histórico após reinício;
- sincronização de planejamento entre contas/agências;
- várias metas simultâneas no mesmo mês;
- edição, exclusão ou estorno de gasto;
- despesas recorrentes;
- importação automática de transações;
- uso automático de saque/transferência como gasto categorizado;
- integração com cartões ou Open Finance;
- gráficos avançados;
- notificações;
- previsão por aprendizado de máquina ou IA generativa;
- aconselhamento financeiro profissional.

## Contexto atual

- A Sprint 1 armazena contas em memória por agência.
- Cada conta pertence a `id_conta % 3`.
- Operações que alteram estado são registradas com Lamport.
- O frontend React acessa qualquer agência usando JWT.
- O extra anterior de health-check foi substituído pelo ADR-004.

## Premissa que requer confirmação

Na implementação, **registrar um gasto representa uma despesa bancária real e também reduz o saldo da conta**. A operação é atômica dentro da agência: ou o gasto é registrado e o saldo debitado, ou nenhum dos dois acontece.

Se a intenção do aluno for apenas catalogar gastos já ocorridos sem tocar no saldo, essa regra deverá ser alterada antes da implementação, pois afeta domínio, testes, eventos e interface.

## Comportamento funcional

### Definir planejamento mensal

A pessoa informa:

- competência no formato `AAAA-MM`;
- renda prevista maior que zero;
- meta de economia maior ou igual a zero e menor ou igual à renda;
- limites opcionais por categoria;
- categorias que podem receber sugestões de corte.

O sistema calcula:

```text
limite_gasto_mensal = renda_prevista - meta_economia
```

O planejamento pode ser criado ou substituído com `PUT`. Atualizá-lo não altera o saldo e não apaga gastos existentes.

A soma dos limites configurados por categoria não pode ultrapassar o limite mensal de gasto. Ela pode ser menor, pois nem toda categoria precisa possuir limite específico.

Se o novo limite ficar abaixo do total já gasto, o resumo passa imediatamente para “ajuste necessário”.

### Registrar gasto

A pessoa informa:

- descrição não vazia;
- valor positivo com até duas casas decimais;
- categoria previamente configurada no planejamento;
- data;
- competência derivada da data.

Regras:

- a conta precisa pertencer à agência chamada;
- a conta e o planejamento da competência precisam existir;
- o saldo precisa cobrir o valor;
- o gasto recebe ID gerado pelo servidor;
- saldo e gasto são alterados na mesma seção crítica local;
- o evento `REGISTRAR_GASTO` registra saldo resultante, categoria e competência;
- uma falha de validação não altera saldo, gasto ou relógio.

### Consultar resumo

A consulta retorna:

- planejamento;
- total gasto no mês;
- economia projetada;
- limite de gasto e valor ainda disponível;
- valor que precisa ser reduzido para atingir a meta;
- total por categoria;
- recomendações;
- lista de gastos da competência.

A consulta é somente leitura e não incrementa Lamport.

## Modelo de domínio

### PlanejamentoMensal

| Campo | Tipo | Regra |
|---|---|---|
| `contaId` | inteiro | conta local existente |
| `competencia` | `AAAA-MM` | mês válido |
| `rendaPrevista` | decimal | maior que zero |
| `metaEconomia` | decimal | entre zero e a renda |
| `limitesPorCategoria` | mapa categoria → decimal | valores não negativos |
| `categoriasFlexiveis` | conjunto de categorias | usadas nas recomendações |
| `categoriasOrdenadas` | lista ordenada de categorias | primeira posição é a mais importante |

Chave lógica: `(contaId, competencia)`.

### Gasto

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | gerado pelo servidor |
| `contaId` | inteiro | conta local existente |
| `descricao` | texto | obrigatório |
| `valor` | decimal | maior que zero |
| `categoria` | texto normalizado | deve existir no planejamento da competência |
| `data` | data ISO | define a competência |
| `registradoEm` | instante UTC | auditoria |

### Categorias gerenciadas no planejamento

O planejamento possui uma lista própria de categorias. A interface começa com sugestões comuns, mas a pessoa pode adicionar ou remover tipos de gasto e reorganizá-los por arrastar e soltar. Os nomes são normalizados, não podem ficar vazios, têm no máximo 60 caracteres e não podem se repetir no mesmo planejamento.

`categoriasOrdenadas` preserva essa lista no backend. A posição `0` representa a categoria mais importante. A ordem não muda os valores nem substitui limites; ela é usada somente como critério de desempate das recomendações, protegendo a categoria mais importante quando os valores financeiros forem equivalentes.

Ao remover uma categoria, novos gastos nela deixam de ser aceitos. Gastos já registrados permanecem no histórico e nos totais da competência para não perder auditoria.

## Cálculos

```text
total_gasto = soma(gastos da conta e competência)
limite_gasto_mensal = renda_prevista - meta_economia
economia_projetada = renda_prevista - total_gasto
saldo_para_gastar = max(0, limite_gasto_mensal - total_gasto)
valor_ajuste = max(0, meta_economia - economia_projetada)
```

Estados:

- `META_ATINGIVEL`: `economia_projetada >= meta_economia`;
- `AJUSTE_NECESSARIO`: `economia_projetada < meta_economia`;
- `RENDA_EXCEDIDA`: `total_gasto > renda_prevista`.

`economia_projetada` pode ser negativa quando os gastos superam a renda. O valor não deve ser truncado, pois ele comunica o déficit.

## Algoritmo de recomendação

O algoritmo é determinístico e auditável:

1. calcular `valor_ajuste`;
2. se for zero, retornar lista vazia e informar que a meta está atingível;
3. calcular o excesso de cada categoria que possui limite;
4. considerar apenas categorias marcadas como flexíveis;
5. ordenar primeiro pelo maior excesso sobre o limite; em empate, priorizar o corte da categoria menos importante segundo `categoriasOrdenadas`;
6. recomendar a redução do excesso, sem ultrapassar o `valor_ajuste` restante;
7. se ainda faltar redução, ordenar categorias flexíveis pelo total gasto e, em empate, pela menor prioridade; propor redução adicional de até 20% do gasto de cada uma, descontando valores já recomendados;
8. parar quando a soma recomendada cobrir o ajuste;
9. se não for possível cobrir tudo, retornar também o valor ainda não coberto.

Cada recomendação informa:

- categoria;
- total gasto;
- limite configurado, quando existir;
- redução sugerida;
- motivo (`ACIMA_DO_LIMITE` ou `MAIOR_GASTO_FLEXIVEL`).

O algoritmo nunca sugere corte em categoria não marcada como flexível.

## Exemplo verificável

Planejamento da conta 6 para `2026-09`:

```json
{
  "rendaPrevista": 500.00,
  "metaEconomia": 100.00,
  "limitesPorCategoria": {
    "Alimentação": 150.00,
    "Transporte": 100.00,
    "Delivery": 80.00,
    "Lazer": 70.00
  },
  "categoriasFlexiveis": ["Delivery", "Lazer", "Compras", "Assinaturas"],
  "categoriasOrdenadas": ["Alimentação", "Transporte", "Delivery", "Lazer", "Compras", "Assinaturas"]
}
```

Gastos:

| Categoria | Total |
|---|---:|
| Alimentação | 150,00 |
| Transporte | 80,00 |
| Delivery | 120,00 |
| Lazer | 100,00 |
| **Total** | **450,00** |

Resultado:

- limite de gasto: R$ 400,00;
- economia projetada: R$ 50,00;
- ajuste necessário: R$ 50,00;
- sugestão: reduzir R$ 40,00 em Delivery e R$ 10,00 em Lazer.

## Contrato HTTP resumido

| Método | Rota | Finalidade |
|---|---|---|
| `PUT` | `/contas/{id}/controle-financeiro/{competencia}/planejamento` | criar/substituir planejamento |
| `POST` | `/contas/{id}/controle-financeiro/gastos` | registrar gasto e debitar saldo |
| `GET` | `/contas/{id}/controle-financeiro/{competencia}` | consultar resumo e recomendações |

Todas as rotas exigem JWT e validam a partição.

## Design técnico

### Backend

- `models/planejamento_financeiro.py`
- `models/gasto.py`
- `schemas/controle_financeiro.py`
- `repositories/controle_financeiro_repository.py`
- `services/controle_financeiro_service.py`
- `services/recomendacao_economia_service.py`
- `controllers/controle_financeiro_controller.py`

O serviço financeiro coordena o `ContaRepository` ao registrar gasto. Os dois repositórios precisam compartilhar a mesma seção crítica ou uma operação de domínio coordenada para evitar gasto sem débito ou débito sem gasto.

### Frontend

- formulário de planejamento mensal;
- gestão de categorias com criação, remoção e reordenação por arrastar e soltar;
- formulário de gasto;
- resumo da meta;
- totais por categoria;
- lista de recomendações;
- histórico de gastos do mês.

## Eventos Lamport

### `DEFINIR_PLANEJAMENTO_MENSAL`

Detalhes:

- `contaId`;
- `competencia`;
- `rendaPrevista`;
- `metaEconomia`;
- `limiteGastoMensal`.

### `REGISTRAR_GASTO`

Detalhes:

- `gastoId`;
- `contaId`;
- `competencia`;
- `categoria`;
- `valor`;
- `novoSaldo`.

Consultas de resumo não geram evento porque não alteram estado.

## Segurança e privacidade

- todas as rotas usam JWT;
- um usuário autenticado ainda pode operar qualquer conta, pois a Sprint 1 não possui autorização por titularidade;
- descrições de gastos podem conter informações pessoais e devem ser tratadas como dados sensíveis;
- não registrar descrições completas no terminal se não forem necessárias à evidência;
- não enviar dados a serviços externos;
- nunca apresentar recomendação como aconselhamento profissional.

## Restrições e premissas

- dados em memória e perdidos no reinício;
- uma moeda implícita: BRL;
- uma meta por conta/mês;
- datas e competência validadas;
- recomendações baseadas apenas nos gastos cadastrados por essa funcionalidade;
- depósitos, saques e transferências não entram automaticamente nas categorias;
- o saldo bancário e a renda prevista representam conceitos diferentes;
- o frontend apenas apresenta; o cálculo oficial pertence ao backend.

## Riscos

| Risco | Tratamento |
|---|---|
| extra consome a sprint inteira | implementar somente o MVP depois dos obrigatórios |
| gasto debita saldo e registro falha | operação local coordenada/atômica |
| recomendações parecem arbitrárias | algoritmo explícito e motivos retornados |
| limites de categoria não cobrem o ajuste | retornar parcela ainda não coberta |
| usuário confunde renda com saldo | textos claros na interface |
| reinício apaga planejamento | mensagem no README/interface de desenvolvimento |
| uso de `float` altera cálculos | `Decimal` em todo o domínio |
| descrição expõe informação pessoal | evitar logs e evidências com dados reais |
| reenvio duplica gasto e débito | desabilitar envio durante carregamento e documentar ausência de idempotência |
| remoção confunde categorias já usadas | manter histórico e totais; bloquear somente novos gastos na categoria removida |

## Validação

- rejeitar renda zero/negativa;
- rejeitar meta maior que renda;
- criar e substituir planejamento;
- preservar gastos ao alterar planejamento;
- rejeitar gasto sem planejamento;
- rejeitar gasto maior que saldo;
- garantir gasto e débito atômicos;
- calcular cenário dentro da meta;
- calcular cenário com ajuste necessário;
- calcular renda excedida;
- sugerir primeiro excessos flexíveis;
- nunca sugerir categorias não flexíveis;
- aceitar categorias personalizadas e preservar a ordem de prioridade definida;
- rejeitar novo gasto em categoria ausente do planejamento;
- no frontend, adicionar, remover e reordenar uma categoria sem perder seus dados de limite e flexibilidade;
- retornar valor não coberto quando necessário;
- consulta não incrementa Lamport;
- frontend mostra meta de R$ 100,00, gastos e recomendações;
- salvar `evidencias/sprint1/funcionalidade-adicional.png`;
- manter tudo no commit exclusivo do extra.

## Referências

- [ADR-004](../decisions/ADR-004-controle-financeiro-mensal.md)
- [Arquitetura da Sprint 1](SPEC-001-arquitetura-sprint-1.md)
- [Contrato da API](../API_SPRINT_1.md)
- [Plano de commits](../PLANO_DE_COMMITS_SPRINT_1.md)
