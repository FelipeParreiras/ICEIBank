# Atributos de qualidade

## Prioridades

1. **Clareza didática:** a aplicação do relógio lógico deve ser observável no código e nos logs.
2. **Corretude:** uma agência não pode operar uma conta pertencente a outra partição.
3. **Testabilidade:** domínio e serviços devem ser testáveis sem subir servidores reais.
4. **Observabilidade:** eventos devem identificar agência, tipo, timestamp lógico, horário físico e detalhes.
5. **Segurança básica:** segredos ficam fora do Git; tokens inválidos ou expirados são rejeitados.
6. **Evolução:** a estrutura deve acomodar mensageria, consenso e transações distribuídas nas próximas sprints.

## Não objetivos atuais

- Alta disponibilidade real.
- Persistência durável das contas.
- Escala horizontal de uma mesma agência.
- Resolver atomicidade entre agências antes da Sprint 4.
