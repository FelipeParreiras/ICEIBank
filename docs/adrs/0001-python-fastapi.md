# ADR-0001: Python e FastAPI no backend

- Estado: Aceito
- Data: 2026-08-24

## Contexto

O roteiro exige Java ou Python e a linguagem escolhida deverá continuar nas quatro sprints. O sistema precisa expor uma API REST, validar contratos, autenticar com JWT e realizar comunicação HTTP entre agências.

## Decisão

Usar Python 3.13 e FastAPI. Pydantic será usado para contratos e configuração; HTTPX para chamadas HTTP; PyJWT para tokens; Uvicorn para execução ASGI.

## Consequências

- A documentação OpenAPI poderá ser gerada automaticamente.
- Contratos terão validação e tipagem explícitas.
- O ambiente será isolado em `.venv` e reproduzível pelo `pyproject.toml`.
- Cada processo de agência deverá rodar com um worker, pois o estado da Sprint 1 será mantido em memória.
- O relógio lógico deverá ser protegido contra acesso concorrente dentro do processo.
