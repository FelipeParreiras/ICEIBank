# Arquitetura

## Objetivo

O ICEIBank será um sistema distribuído didático. O mesmo artefato de agência será executado três vezes, com identidade e porta próprias. Cada instância será responsável por uma partição exclusiva das contas.

## Contexto

```text
Frontend web
     |
     | HTTP + JWT
     v
Agência 0 <---- HTTP interno ----> Agência 1
     ^                                  ^
     |                                  |
     +-------- HTTP interno ------------+----> Agência 2

Cada agência: memória de contas + relógio lógico + log JSONL próprio
```

## Limites internos planejados

```text
api -> services -> domain
 |        |
 |        +------> infrastructure (por interfaces/adaptadores)
 +---------------> schemas
```

- `api`: protocolo HTTP e composição da aplicação.
- `services`: casos de uso e coordenação.
- `domain`: regras bancárias independentes de framework.
- `schemas`: contratos externos validados.
- `infrastructure`: arquivos e comunicação entre processos.
- `core`: configuração e preocupações transversais.

## Restrições da Sprint 1

- Uma única base de código executada como três processos.
- Particionamento determinado por `id_conta % 3`.
- Estado de contas em memória; reiniciar uma agência elimina seu estado.
- Um único worker por instância, evitando relógios e mapas independentes dentro da mesma agência.
- Eventos persistidos localmente em JSONL.
- Transferências remotas via HTTP direto, sem atomicidade distribuída nesta sprint.
- Rotas externas protegidas por JWT; o mecanismo de confiança entre agências será especificado antes da implementação.

## Princípios

- Dependências apontam para o domínio, não para o framework.
- Configuração vem do ambiente.
- Contratos e decisões importantes são documentados antes do código.
- A limitação de consistência da Sprint 1 deve permanecer visível e testável.
