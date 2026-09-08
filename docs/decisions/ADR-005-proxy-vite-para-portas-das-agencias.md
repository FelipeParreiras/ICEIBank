# ADR-005: Proxy Vite para as portas das agências

## Status

Aceito

## Data

2026-09-07

## Contexto

O RA terminado em 45 fixa as agências nas portas 4045, 4046 e 4047. Durante a validação real no Google Chrome, uma chamada direta à Agência 0 falhou com `ERR_UNSAFE_PORT`: o navegador bloqueia a porta 4045 antes de enviar a requisição. Trocar as portas violaria o roteiro, e remover a Agência 0 da interface tornaria o frontend incompleto.

## Decisão

- manter os processos FastAPI exatamente nas portas 4045–4047;
- fazer o React chamar caminhos relativos `/api/agencia-0`, `/api/agencia-1` e `/api/agencia-2`;
- configurar o servidor Vite na porta 5173 para encaminhar esses caminhos aos backends correspondentes;
- manter a comunicação entre agências direta, sem passar pelo Vite;
- exigir proxy equivalente do servidor web caso o build de produção seja publicado fora do Vite.

## Alternativas consideradas

### Chamar as portas diretamente no React

- Prós: configuração mais simples.
- Contras: a Agência 0 não funciona no Google Chrome.
- Motivo da rejeição: falha observada durante o teste integrado obrigatório.

### Trocar a porta base

- Prós: poderia evitar a lista de portas bloqueadas.
- Contras: descumpre o cálculo de porta definido a partir do RA.
- Motivo da rejeição: a porta base 4045 é requisito do projeto.

### Pedir ao usuário para iniciar o Chrome com flags inseguras

- Prós: dispensaria o proxy.
- Contras: reduz segurança e torna a execução dependente de configuração especial do navegador.
- Motivo da rejeição: o projeto deve rodar com uma inicialização normal do Google Chrome.

## Consequências

- O fluxo completo funciona em `http://localhost:5173` sem mudar as portas das agências.
- O modo de desenvolvimento depende das regras de proxy em `vite.config.js`.
- Um deploy estático precisa de Nginx, Apache ou serviço equivalente reproduzindo as regras.
- Requisições REST feitas por Postman, PowerShell e pelos próprios backends continuam usando diretamente 4045–4047.

## Referências

- [SPEC-001](../specs/SPEC-001-arquitetura-sprint-1.md)
- [Configuração e execução](../CONFIGURACAO_E_EXECUCAO.md)
- `frontend/vite.config.js`
- `frontend/src/api/cliente.js`
