# ADR-001: Python/FastAPI e React na Sprint 1

## Status

Aceito

## Data

2026-09-07

## Contexto

O roteiro exige Java ou Python para o backend e um frontend web em tecnologia livre. A tecnologia escolhida deve continuar sendo usada na evolução do projeto ao longo das quatro sprints. O aluno possui experiência com Python e React, considera Python mais prático para esta implementação e precisa reduzir o custo de aprender ferramentas enquanto aplica conceitos distribuídos novos.

## Decisão

- usar Python com FastAPI para as APIs das agências;
- usar Pydantic para contratos e validação;
- usar React com Vite e JavaScript modular para o frontend;
- separar controladores, serviços, modelos/schemas e repositórios para preservar as responsabilidades de MVC;
- fixar versões das dependências ao criar os projetos e versionar os lockfiles.

## Alternativas consideradas

### Java com Spring Boot

- Prós: concorrência explícita, ecossistema empresarial maduro e forte estrutura arquitetural.
- Contras: maior quantidade de configuração e menor familiaridade do aluno.
- Motivo da rejeição: aumentaria a carga acidental da sprint sem melhorar os conceitos avaliados.

### Python com Flask

- Prós: pequeno, conhecido e flexível.
- Contras: validação, injeção de dependências e documentação de contratos exigiriam mais decisões manuais.
- Motivo da rejeição: FastAPI fornece uma base mais direta para contratos tipados e testes da API.

### Frontend sem framework

- Prós: menos dependências e build simples.
- Contras: menor aderência à experiência já adquirida pelo aluno e organização manual do estado.
- Motivo da rejeição: React permite aproveitar conhecimento existente e organizar login, agência e mensagens de erro.

### React com TypeScript

- Prós: contratos mais seguros no frontend.
- Contras: adiciona custo de tipagem e configuração nesta primeira sprint.
- Motivo da rejeição: JavaScript modular é suficiente para o escopo acadêmico. A adoção futura de TypeScript pode ser registrada em novo ADR.

## Consequências

- O aluno trabalha em tecnologias que consegue explicar durante a apresentação.
- Os modelos Pydantic tornam erros de entrada previsíveis.
- Será necessário traduzir os exemplos Node.js do roteiro, preservando comportamento e não sintaxe.
- A separação MVC precisará ser documentada porque FastAPI e React não implementam MVC clássico automaticamente.
- Python não elimina os riscos de concorrência; relógio, saldo e arquivo de eventos ainda precisam de sincronização.
- O projeto terá dois gerenciadores de dependências e dois processos de desenvolvimento.

## Referências

- [SPEC-001](../specs/SPEC-001-arquitetura-sprint-1.md)
- [Roadmap da Sprint 1](../../ROADMAP_SPRINT_1.md)
