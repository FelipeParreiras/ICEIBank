# ADR-0002: Uma base de código para três processos de agência

- Estado: Aceito
- Data: 2026-08-24

## Contexto

O projeto exige três agências independentes, mas não três implementações divergentes. A identidade da agência e o deslocamento de portas variam por ambiente.

## Decisão

Construir um único pacote e iniciar três processos com configurações diferentes por variáveis de ambiente. O identificador da agência será `ICEIBANK_AGENCIA_ID`; portas serão derivadas de uma base e de `ICEIBANK_PORT_OFFSET`.

## Consequências

- Correções e evoluções serão aplicadas igualmente às três agências.
- Cada processo terá memória, relógio e arquivo de eventos próprios.
- Inicialização inválida deverá falhar cedo, por exemplo quando o identificador estiver fora de 0 a 2.
- A execução local precisará de três terminais ou de um mecanismo de orquestração futuro.
