# Glossário do ICEIBank

## Agência

Instância independente do serviço bancário. Na Sprint 1 existem três, cada uma com identidade, porta, contas, relógio e log próprios.

## Partição

Divisão de dados em que cada conta pertence a exatamente uma agência. Não há cópia da mesma conta nas demais agências.

## Agência responsável

Resultado de `id_conta % 3`. Uma operação enviada à agência errada deve ser recusada.

## Relógio lógico

Contador usado para ordenar eventos com base em causalidade conhecida, sem depender do horário físico.

## Relógio de Lamport

Relógio lógico escalar que incrementa em eventos locais/envios e usa `max(local, recebido) + 1` ao receber mensagens.

## Causalidade

Relação na qual um evento pode ter influenciado outro, diretamente ou por uma cadeia de mensagens.

## Evento concorrente

Evento sem relação causal estabelecida com outro. “Concorrente” não exige que os dois tenham ocorrido no mesmo milissegundo.

## Hora de parede

Horário físico do computador. É útil para operação, mas não substitui o relógio lógico em um sistema distribuído.

## JSON Lines / JSONL

Formato em que cada linha de um arquivo é um objeto JSON completo. Permite acrescentar eventos sem reescrever o arquivo inteiro.

## REST

Estilo de API baseado em recursos, métodos HTTP, representações e códigos de resposta. O ICEIBank usa JSON sobre HTTP local.

## MVC

Separação entre Model, View e Controller. No projeto, FastAPI e React não impõem MVC clássico, mas as responsabilidades são mantidas entre modelos/serviços, respostas/componentes e controladores/handlers.

## JWT

Token assinado que carrega claims como identidade e expiração. A assinatura permite detectar alteração sem consultar uma sessão em memória.

## Claim

Campo do JWT, como `sub`, `iat`, `exp` ou `iss`.

## Autenticação

Processo de verificar quem está fazendo a requisição.

## Autorização

Processo de decidir se uma identidade autenticada pode executar determinada ação. A Sprint 1 não implementa autorização por titularidade.

## Token interno

Credencial compartilhada apenas entre backends para proteger a rota de crédito remoto. Não é o mesmo JWT enviado pelo React.

## CORS

Política aplicada pelo navegador que controla quais origens podem chamar uma API. Não protege comunicação servidor-servidor.

## Atomicidade

Propriedade “tudo ou nada”. A transferência local é atômica dentro de uma agência; a remota não é atômica nesta sprint.

## Consistência eventual

Modelo no qual réplicas ou etapas podem ficar temporariamente divergentes, convergindo depois. Será relevante em soluções como Saga.

## 2PC

Two-Phase Commit: protocolo que separa preparação e confirmação de uma transação distribuída. É tema de evolução futura.

## Saga

Sequência de transações locais com ações compensatórias para desfazer efeitos quando uma etapa posterior falha.

## Idempotência

Propriedade de repetir uma operação sem aplicar o efeito mais de uma vez. Não faz parte do MVP de Controle Financeiro Mensal.

## Competência

Mês de referência de um planejamento ou gasto, representado por `AAAA-MM`.

## Meta de economia

Valor que a pessoa deseja preservar da renda prevista ao final da competência.

## Limite de gasto mensal

Resultado de `renda prevista - meta de economia`.

## Economia projetada

Resultado de `renda prevista - total de gastos registrados`.

## Categoria flexível

Categoria que a pessoa autoriza o sistema a considerar em recomendações de redução.

## Worker

Processo que atende requisições. Mais de um worker para a mesma agência criaria
relógios independentes e concorrência fora do modelo operacional do SQLite
local; por isso, não será usado na Sprint 1.

## Lock

Mecanismo de exclusão usado para impedir que operações concorrentes modifiquem contador, saldo ou arquivo de modo inconsistente.

## Causas de 502 na sprint

Falha em contatar ou obter sucesso da agência de destino depois que o débito remoto já ocorreu. O código torna essa inconsistência explícita.

## Evidência

Captura real de execução usada para comprovar um requisito. Código-fonte sozinho não substitui evidência operacional.
