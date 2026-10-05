# Registro de execução real — 05/10/2026

## Escopo e integridade da evidência

Esta rodada complementa o roteiro da Sprint 1 com resultados observados em
execução local, sem gravar senha, JWT, segredo interno ou conteúdo de `.env`.
As capturas PNG exigidas pelo roteiro **não** foram sintetizadas e continuam
pendentes: elas devem exibir o comportamento em execução e `Get-Date` quando
aplicável.

A branch atual já contém a evolução da Sprint 2. Por isso, transferências entre
agências usam RabbitMQ e os logs usam relógios vetoriais; não é correto
reapresentar essa implementação como a comunicação HTTP direta e o relógio de
Lamport solicitados na Sprint 1. Os itens históricos afetados estão indicados
explicitamente abaixo.

## Transferência local e autenticação

- Data/hora local: `2026-10-05 15:24:11 -03:00`.
- Agência usada: 0, em `http://127.0.0.1:4045`.
- Uma consulta sem credencial para a conta 9900 retornou HTTP `401`.
- O login retornou HTTP `200`; o token foi mantido apenas em memória durante a
  rodada e não foi registrado.
- As contas 9900 e 9903 foram criadas com R$ 200,00 e R$ 50,00,
  respectivamente (HTTP `201`).
- A transferência local 9900 → 9903 de R$ 25,00 retornou HTTP `200`, tipo
  `LOCAL`.
- Saldos finais: origem R$ 175,00, destino R$ 75,00 e soma preservada de
  R$ 250,00. A consulta autorizada retornou HTTP `200`.
- O JSONL real da Agência 0 registrou `TRANSFERENCIA_DEBITO` no vetor
  `[6, 0, 0]` e `TRANSFERENCIA_CREDITO` no vetor `[7, 0, 0]`.

Capturas ainda necessárias: `transferencia-local.png`, `auth-sem-token.png` e
`auth-com-token.png`, sem revelar o JWT.

## Funcionalidade adicional — Controle Financeiro

- Conta 9906 criada na Agência 0 com R$ 1.000,00 (HTTP `201`).
- Planejamento para `2026-09`: renda prevista R$ 500,00, meta R$ 100,00;
  limites de Alimentação R$ 150,00, Transporte R$ 100,00, Delivery R$ 80,00 e
  Lazer R$ 70,00; Delivery e Lazer marcados como flexíveis (HTTP `200`).
- Foram registrados quatro gastos com HTTP `201`: R$ 150,00 em Alimentação,
  R$ 80,00 em Transporte, R$ 120,00 em Delivery e R$ 100,00 em Lazer.
- Duas consultas consecutivas do resumo retornaram HTTP `200` e conteúdo
  idêntico: total R$ 450,00, economia projetada R$ 50,00, ajuste R$ 50,00 e
  status `AJUSTE_NECESSARIO`.
- Recomendações calculadas: Delivery R$ 40,00 e Lazer R$ 10,00. O saldo final
  da conta foi R$ 550,00.
- O JSONL real registrou `DEFINIR_PLANEJAMENTO_MENSAL` no vetor `[9, 0, 0]`
  e quatro `REGISTRAR_GASTO`, dos vetores `[10, 0, 0]` a `[13, 0, 0]`.

Captura ainda necessária: `funcionalidade-adicional.png`, com meta, gastos,
totais e recomendações visíveis.

## Evidências que exigem a arquitetura histórica

As seguintes capturas não foram geradas nesta branch porque reproduzi-las como
se fossem da Sprint 1 seria incorreto:

- `transferencia-entre-agencias.png`: a versão atual publica no broker em vez
  de chamar a agência de destino por HTTP direto;
- `falha-conhecida.png`: a semântica atual é de publicação assíncrona e não da
  resposta HTTP `502` com débito mantido do roteiro original;
- `linha-do-tempo.png`: a ferramenta atual ordena vetores causais, não
  timestamps de Lamport.

Para criar essas três imagens, é necessário executar o commit/branch da Sprint
1 antes da migração para a Sprint 2 ou adaptar formalmente o enunciado para a
arquitetura atual. Também permanecem pendentes as capturas de token expirado e
do frontend: `auth-token-expirado.png`, `frontend-login.png`,
`frontend-transferencia.png` e `frontend-erro.png`.

## Rastreabilidade

- Logs consultados: `agencia/data/eventos-agencia-0.jsonl`.
- Commit da árvore no início da rodada: `52af43a`.
- Este registro documenta saídas reais, mas não substitui nenhuma captura PNG
  obrigatória nem o vídeo de apresentação.
