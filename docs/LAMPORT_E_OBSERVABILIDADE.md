# Relógio de Lamport e observabilidade

## Objetivo

Definir como cada agência ordena eventos lógicos, como o timestamp atravessa uma transferência remota e como os três logs são unidos para análise.

## Modelo mental

Cada agência possui um contador próprio. O contador não mede segundos e não precisa se aproximar do relógio do computador. Ele representa progresso lógico e preserva relações causais conhecidas.

## Regras

### Evento local

```text
contador = contador + 1
```

Usado antes de registrar uma alteração local, como criação, depósito, saque, débito ou crédito local.

### Envio de mensagem

```text
contador = contador + 1
enviar contador junto da mensagem
```

Usado pela agência de origem imediatamente antes do `POST` de crédito remoto.

### Recebimento de mensagem

```text
contador = max(contador_local, timestamp_recebido) + 1
```

Isso garante que o recebimento fique logicamente depois da história local do destino e do evento de envio da origem.

Exemplo: se a Agência 0 está em 10 e recebe timestamp 3, o novo valor é 11. Adotar diretamente 3 faria o relógio local regredir e perderia a ordem construída pelos eventos anteriores.

## Garantia e limite

Se A causa B, então:

```text
Lamport(A) < Lamport(B)
```

A volta não é garantida. Ver `Lamport(A) < Lamport(B)` não prova sozinho que A causou B; os eventos podem ter ocorrido independentemente em processos distintos.

Dois eventos de agências diferentes podem ter o mesmo timestamp. Isso normalmente indica que não houve comunicação suficiente para estabelecer uma ordem entre eles, mas o relógio de Lamport sozinho não é uma ferramenta completa para decidir concorrência. Essa limitação motiva o relógio vetorial da Sprint 2.

## Eventos implementados

| Tipo | Regra Lamport | Detalhes mínimos |
|---|---|---|
| `CRIAR_CONTA` | evento local | `id`, `nomeAluno`, `saldoInicial` |
| `DEPOSITO` | evento local | `id`, `valor`, `novoSaldo` |
| `SAQUE` | evento local | `id`, `valor`, `novoSaldo` |
| `TRANSFERENCIA_DEBITO` | evento local | `idOrigem`, `idDestino`, `valor` |
| `TRANSFERENCIA_CREDITO` | evento local | `idOrigem`, `idDestino`, `valor` |
| `TRANSFERENCIA_CREDITO_REMOTO` | recebimento | `idConta`, `valor`, `origemAgencia` |
| `TRANSFERENCIA_FALHOU` | evento local | `idOrigem`, `idDestino`, `valor`, `erro` resumido |
| `DEFINIR_PLANEJAMENTO_MENSAL` | evento local | `contaId`, `competencia`, `rendaPrevista`, `metaEconomia` |
| `REGISTRAR_GASTO` | evento local | `gastoId`, `contaId`, `competencia`, `categoria`, `valor`, `novoSaldo` |

O incremento de `ao_enviar` é transportado na mensagem. Um evento adicional de envio pode ser registrado se a implementação mantiver a sequência prevista e documentar esse novo tipo, mas não é obrigatório pelo exemplo do roteiro.

## Formato JSON Lines

Cada evento ocupa uma linha independente:

```json
{"agencia":"agencia-0","tipo":"DEPOSITO","timestampLamport":4,"horaParede":"2026-09-07T18:00:00Z","detalhes":{"id":0,"valor":25.00,"novoSaldo":225.00}}
```

Arquivos:

```text
agencia/data/eventos-agencia-0.jsonl
agencia/data/eventos-agencia-1.jsonl
agencia/data/eventos-agencia-2.jsonl
```

Regras:

- codificação UTF-8;
- append de uma linha completa sob lock;
- JSON válido sem linhas parciais;
- criação do diretório quando necessário;
- nenhum segredo nos detalhes;
- arquivos ignorados pelo Git.

## Ordem da transferência remota

Origem:

1. valida origem, saldo e valor;
2. chama `evento_local` e aplica/registra o débito;
3. chama `ao_enviar`;
4. envia esse timestamp à agência responsável pelo destino.

Destino:

1. autentica a agência de origem e valida o corpo;
2. chama `ao_receber(timestamp_recebido)`;
3. consulta e credita a conta local;
4. registra `TRANSFERENCIA_CREDITO_REMOTO` usando o novo valor.

Se a conta não existir, o recebimento válido já ocorreu e o relógio pode avançar mesmo com a rejeição da regra de negócio.

## Falha conhecida

Se o destino estiver indisponível:

1. o débito da origem já foi aplicado;
2. a chamada REST falha ou expira;
3. a origem chama `evento_local`;
4. registra `TRANSFERENCIA_FALHOU`;
5. retorna 502;
6. não executa rollback.

Essa sequência torna a inconsistência visível. Não adicionar compensação, retry automático ou idempotência sem revisar o escopo, pois isso alteraria o experimento da Sprint 1.

## Controle financeiro

Criar ou alterar um planejamento e registrar gasto modificam estado, portanto usam `evento_local`. Consultar o resumo e suas recomendações é somente leitura e não incrementa o relógio.

## Linha do tempo unificada

`scripts/mesclar_logs.py` deve:

1. localizar apenas `*.jsonl` na pasta de dados;
2. ignorar linhas vazias;
3. informar arquivo/linha em JSON inválido;
4. combinar os eventos;
5. ordenar primariamente por `timestampLamport`;
6. usar agência e posição original apenas como desempate estável de apresentação;
7. imprimir todos os campos necessários para análise.

O desempate não cria causalidade. A saída deve explicar que eventos empatados não possuem ordem total estabelecida pelo Lamport.

## Hora de parede

`horaParede` serve para:

- localizar a execução;
- apoiar diagnóstico;
- comparar de forma ilustrativa com a ordem lógica.

Ela não substitui Lamport, pois relógios físicos podem ter resolução, ajuste e sincronização diferentes.

## Concorrência

- um relógio por processo;
- todas as operações do contador sob o mesmo lock;
- um lock separado ou estratégia coordenada para escrita do log;
- um worker por agência;
- não criar uma instância de relógio por requisição;
- testes concorrentes devem confirmar que timestamps locais não se repetem.

## Validação

- sequência local 0 → 1 → 2;
- receber 3 quando local é 10 resulta em 11;
- receber 20 quando local é 10 resulta em 21;
- envio incrementa e o recebimento fica acima do timestamp enviado;
- eventos independentes podem empatar;
- falha remota gera evento posterior ao envio;
- mesclador processa os três arquivos e gera a evidência exigida.

## Referências

- [Arquitetura](specs/SPEC-001-arquitetura-sprint-1.md)
- [Plano de testes](PLANO_DE_TESTES_E_EVIDENCIAS.md)
- Seções 6, 8 e 10 do roteiro da Sprint 1.
