# Documentação do ICEIBank

O comportamento obrigatório de agentes de IA neste repositório está definido em [AGENTS.md](../AGENTS.md).

Este diretório separa três tipos de documentação:

- [Arquitetura](architecture/README.md): visão estrutural, limites e restrições do sistema.
- [Especificações](specs/README.md): comportamento esperado antes da implementação.
- [ADRs](adrs/README.md): decisões arquiteturais, contexto e consequências.

## Regras de manutenção

1. Mudanças estruturais relevantes exigem um ADR novo; ADRs aceitos não são reescritos para esconder decisões anteriores.
2. Uma funcionalidade deve possuir especificação antes ou junto de sua implementação.
3. Diagramas e textos devem refletir o código entregue, não apenas uma arquitetura desejada.
4. Segredos, credenciais e dados pessoais não devem aparecer na documentação.
