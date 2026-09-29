# ADR-003: JWT de usuário e credencial interna separada

## Status

Aceito

## Data

2026-09-07

## Contexto

O roteiro exige JWT para as rotas que leem ou modificam contas e pede uma decisão explícita para autenticar a chamada de crédito entre agências. Reutilizar o JWT do usuário acoplaria uma operação de infraestrutura à sessão do frontend. Deixar a rota remota sem proteção permitiria créditos não autorizados.

## Decisão

- autenticar usuários por `POST /auth/login` e emitir JWT com expiração;
- usar o mesmo segredo JWT nas três instâncias para permitir troca da agência de entrada;
- proteger rotas de contas, transferências e controle financeiro com JWT;
- proteger `/contas/{id}/creditar-remoto` com uma credencial interna compartilhada apenas pelos backends;
- nunca enviar a credencial interna ao React;
- configurar segredos por ambiente e ignorar `.env` no Git;
- reconhecer que a Sprint 1 autentica o usuário, mas não autoriza operações por titularidade.

## Alternativas consideradas

### Repassar o JWT do usuário para a agência de destino

- Prós: não exige uma segunda credencial.
- Contras: acopla chamadas internas à sessão do usuário e amplia a propagação do token.
- Motivo da rejeição: identidade de serviço e identidade de usuário possuem responsabilidades distintas.

### Deixar a rota interna sem autenticação

- Prós: implementação mínima.
- Contras: qualquer cliente com acesso à porta poderia creditar contas.
- Motivo da rejeição: viola o objetivo de proteção das operações financeiras.

### Implementar autorização por conta

- Prós: aproxima o sistema de um banco real.
- Contras: exige cadastro, associação usuário-conta e mais regras fora do escopo obrigatório.
- Motivo da rejeição: será documentada como evolução futura, não implementada na Sprint 1.

## Consequências

- A transferência remota continua funcionando mesmo sem propagar o JWT do navegador.
- O projeto passa a administrar dois tipos de segredo.
- Todas as agências precisam receber a mesma configuração de autenticação interna e assinatura JWT.
- Um usuário autenticado ainda poderá operar contas de outros usuários; essa limitação deve aparecer em `RESPOSTAS.md`.
- A rota interna precisa de testes para credencial ausente, inválida e válida.

## Referências

- [SPEC-001](../specs/SPEC-001-arquitetura-sprint-1.md)
- Parte F do roteiro da Sprint 1.
