# Evidências da Sprint 1

Esta pasta recebe capturas reais de execução. A rodada complementar de
05/10/2026 está registrada em
[`registro-execucao-2026-10-05.md`](registro-execucao-2026-10-05.md), sem
segredos e sem substituir os PNGs exigidos pelo roteiro.

A implementação atual já incorpora a evolução da Sprint 2: mensageria RabbitMQ
e relógio vetorial substituíram a transferência HTTP direta e o relógio de
Lamport da Sprint 1. Por isso, o registro separa os cenários que foram
reexecutados com honestidade daqueles que precisam da versão histórica da
Sprint 1 para gerar a captura correta.

## Arquivos obrigatórios

- `transferencia-local.png`
- `transferencia-entre-agencias.png`
- `falha-conhecida.png`
- `linha-do-tempo.png`
- `auth-sem-token.png`
- `auth-com-token.png`
- `auth-token-expirado.png`
- `frontend-login.png`
- `frontend-transferencia.png`
- `frontend-erro.png`
- `funcionalidade-adicional.png`

## Regras

- mostrar comportamento em execução, não somente código;
- incluir `Get-Date` quando solicitado pelo roteiro;
- manter respostas, códigos HTTP, saldos e logs relevantes legíveis;
- mostrar origem e destino na transferência entre agências;
- não exibir senha, JWT, hash, token interno ou conteúdo de `.env`;
- conferir cada PNG depois de salvar;
- relacionar a evidência ao teste e ao commit em `RESPOSTAS.md`.

O procedimento completo está em [Plano de testes e evidências](../../docs/PLANO_DE_TESTES_E_EVIDENCIAS.md).

