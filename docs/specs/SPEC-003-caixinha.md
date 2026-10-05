# SPEC-003: Caixinha com rendimento composto

## Status

Implementado e coberto por testes automatizados em 04/10/2026. As decisões de
tempo e arredondamento foram consolidadas no ADR-008; a exclusão com resgate
automático foi definida no ADR-009.

## Objetivo e escopo

Permitir guardar dinheiro da conta em uma Caixinha e resgatá-lo, com rendimento
simulado de 10% a cada dois dias. Esta é a funcionalidade adicional escolhida
pelo aluno para a Sprint 2, não uma funcionalidade específica imposta pelo roteiro.

## Comportamento confirmado

- Uma conta pode ter várias caixinhas identificadas por nome, com CRUD completo:
  criar, listar/consultar, editar o nome e excluir.
- Cada caixinha pertence exclusivamente à conta que a criou. Esse vínculo é
  obrigatório e não pode ser alterado pela edição da caixinha.
- Listar somente as caixinhas da conta selecionada. Consulta, edição, exclusão,
  depósito e saque devem validar no backend que a caixinha pertence à conta
  informada, antes de acessar ou alterar seus dados.
- Depósitos saem exclusivamente da conta vinculada e saques retornam a ela.
  Uma conta não pode operar a caixinha de outra, mesmo informando seu identificador.
- Dentro da caixinha selecionada, escolher a operação `Depósito` ou `Saque`
  e informar o valor desejado. O depósito cria um lote vinculado exclusivamente
  à caixinha selecionada; o saque corresponde ao resgate FIFO descrito abaixo.
- Guardar um valor reduz o saldo disponível da conta pelo mesmo valor e aumenta
  o saldo da Caixinha.
- Resgatar reduz o saldo da Caixinha e devolve o mesmo valor ao saldo da conta.
- O rendimento é composto: incide sobre o saldo que inclui rendimentos anteriores.
- Cada depósito registra sua data e hora e cumpre seu próprio prazo de rendimento.
  Um novo depósito não herda o tempo já cumprido pelos anteriores.
- Sem novas movimentações, R$ 100,00 tornam-se R$ 110,00 após dois dias e
  R$ 121,00 após quatro dias.

## Resgate em cascata confirmado

O aluno confirmou consumir os depósitos do mais antigo ao mais recente, mantendo
o prazo do depósito que conservar saldo. A regra é FIFO
(primeiro a entrar, primeiro a sair) sobre o saldo completo de cada lote:
principal mais rendimentos acumulados, não apenas sobre os rendimentos.
O FIFO considera somente os lotes da caixinha selecionada para o resgate.
O saldo de outra caixinha não complementa automaticamente a retirada.

## Fluxo de gerenciamento e movimentação

1. Na conta selecionada, criar uma caixinha informando seu nome.
2. Listar as caixinhas da conta e consultar a caixinha desejada.
3. Dentro da caixinha selecionada, escolher `Depósito` ou `Saque`, informar
   o valor e acionar a operação escolhida.
4. Para depósito, validar o valor e o saldo da conta; debitar a conta e registrar
   o novo lote na caixinha selecionada na mesma operação atômica local.
   Para saque, aplicar rendimentos vencidos, validar o saldo da caixinha e
   consumir seus lotes por FIFO, creditando a conta atomicamente com a retirada.
5. Permitir editar o nome sem alterar saldos, lotes ou prazos.
6. Ao excluir, aplicar rendimento vencido, resgatar todo o saldo para a conta e
   remover a Caixinha na mesma transação local.

Caixinha e lote possuem responsabilidades distintas: a caixinha organiza a
reserva por nome; cada lote registra um depósito e controla seu próprio prazo.

## Exemplo de resgate

Exemplo: primeiro lote com R$ 110,00 e segundo com
R$ 220,00 totalizam R$ 330,00. Resgatar R$ 270,00 esgota os R$ 110,00 do primeiro
e retira R$ 160,00 do segundo. Restam R$ 60,00 vinculados ao prazo do segundo.
Resgatar R$ 340,00 nesse estado deve ser rejeitado por saldo insuficiente,
sem movimentar qualquer lote ou saldo da conta.

A regra mantém a próxima data de rendimento do lote parcialmente resgatado;
naquele vencimento, os 10% incidem sobre o saldo restante. O rendimento já
incorporado acompanha o lote, sem iniciar um prazo separado. No exemplo, os
R$ 60,00 tornam-se R$ 66,00 no próximo vencimento, sem outras movimentações.

## Ordem entre rendimento e resgate

Regra confirmada: aplicar os rendimentos dos períodos completos até o instante
do resgate antes de validar o saldo disponível e executar a retirada FIFO.
Um período que vence exatamente naquele instante já está completo.
O resultado não deve depender de o processamento automático ter executado antes.
Períodos já remunerados não podem ser aplicados novamente.

Exemplo: um lote de R$ 100,00 que completa seu primeiro período no instante
do resgate passa a R$ 110,00 e permite resgatar esse total.
A rejeição por saldo insuficiente impede a movimentação do resgate; os
rendimentos devidos são uma atualização distinta da retirada. A política
técnica de efetivação dessa atualização em caso de rejeição ainda será definida.

## Contexto técnico

O projeto usa Python/FastAPI, serviços para regras de negócio, repositórios
sincronizados em memória e `Decimal` para dinheiro. A implementação da Caixinha
deve seguir essas convenções. Ainda não foram definidos endpoints, modelos,
agendamento ou integração com mensageria.

O vínculo conta–caixinha é uma regra de domínio e deve ser validado no serviço,
não apenas por filtragem no frontend. A autorização usuário–conta é uma questão
distinta: a base atual autentica por JWT, mas não restringe contas por titular.
O vínculo aqui definido não equivale a implementar autorização por titularidade;
essa limitação existente deve continuar explícita.

## Decisões técnicas implementadas

- Dois dias equivalem a 48 horas completas por lote.
- Cada ciclo multiplica o saldo do lote por 1,10 e arredonda em centavos com
  `ROUND_HALF_UP`.
- Nomes possuem de 1 a 80 caracteres após trim e são únicos por conta sem
  diferenciação entre maiúsculas e minúsculas.
- O próximo vencimento de cada lote é mantido em memória; rendimentos vencidos
  são aplicados sob demanda e cada ciclo avança esse vencimento.
- Reiniciar a agência apaga Caixinhas e lotes, como as demais estruturas em memória.
- A Caixinha não usa RabbitMQ: é uma regra local e atômica da agência responsável.
- Cada Caixinha mantém em memória o histórico de depósitos, retiradas e
  rendimentos, exibido no detalhe do cartão.
- A exclusão com saldo resgata automaticamente o valor integral para a conta,
  conforme ADR-009.

## Validação planejada

- Criar, listar, consultar, renomear e excluir Caixinhas, confirmando o resgate
  automático do saldo na exclusão.
- Depositar na caixinha selecionada sem alterar saldos ou lotes das demais.
- Criar caixinhas em duas contas e verificar que cada listagem contém somente
  as caixinhas da respectiva conta.
- Tentar consultar, editar, excluir, depositar e sacar usando uma conta diferente
  da vinculada à caixinha; rejeitar sem expor dados nem alterar saldos ou lotes.
- Verificar que a edição do nome não permite trocar a conta vinculada.
- Verificar no frontend a seleção de `Depósito` e `Saque` dentro da caixinha,
  com o valor informado encaminhado à operação correspondente.
- Renomear uma caixinha preserva seus lotes, rendimentos e prazos.
- Resgate FIFO não consome lotes de outra caixinha.
- Guardar e resgatar conservam a soma dos saldos da conta e da Caixinha.
- Apenas o rendimento aumenta essa soma, pelo valor calculado para o período.
- Confirmar a sequência R$ 100,00 → R$ 110,00 → R$ 121,00 sem movimentações.
- Resgatar R$ 270,00 dos lotes de R$ 110,00 e R$ 220,00 deixa R$ 60,00 no
  segundo lote, mantendo seu vencimento; o próximo rendimento é de R$ 6,00.
- Rejeitar resgate de R$ 340,00 sobre R$ 330,00 sem alterar os saldos.
- No instante do primeiro vencimento, permitir resgatar R$ 110,00 de um lote
  inicial de R$ 100,00; antes do vencimento, rejeitar esse valor.
- Após processamento automático do mesmo período, o resgate não reaplica os 10%.
- Cobrir saldo insuficiente, valores inválidos, vencimento exato e concorrência local.

## Referências

- [ADR-006 — Lotes e resgate FIFO](../decisions/ADR-006-caixinha-lotes-fifo.md)
- [ADR-008 — Tempo e arredondamento](../decisions/ADR-008-caixinha-tempo-arredondamento-e-exclusao.md)
- [ADR-009 — Exclusão com resgate automático](../decisions/ADR-009-exclusao-caixinha-com-resgate-automatico.md)
- [Roadmap da Sprint 2](../../ROADMAP_SPRINT_2.md)
- [Guia de desenvolvimento](../GUIA_DE_DESENVOLVIMENTO.md)
- Confirmação do aluno na mentoria: guardar/resgatar movimenta o saldo da conta;
  rendimento acumulado resulta em R$ 121,00 no segundo período.
