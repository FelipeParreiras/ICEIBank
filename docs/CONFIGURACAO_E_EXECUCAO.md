# Configuração e execução — Sprint 1

## Status

Guia implementado e validado localmente em 7 de setembro de 2026.

## Pré-requisitos

- Python compatível com a versão fixada em `agencia/pyproject.toml`.
- Node.js compatível com a versão indicada em `frontend/package.json`.
- Git for Windows.
- PowerShell.
- Navegador moderno.
- Cliente REST opcional: Invoke-RestMethod ou Postman.

Node.js será usado para construir o frontend React, não como linguagem do backend.

## Portas

| Processo | Porta |
|---|---:|
| Agência 0 | 4045 |
| Agência 1 | 4046 |
| Agência 2 | 4047 |
| React/Vite | 5173 |

O offset 45 vem dos dois últimos dígitos do RA. Em máquina compartilhada, não trocar essas portas sem atualizar também o frontend e a documentação.

## Configuração do backend

O arquivo real `agencia/.env` não será versionado. `agencia/.env.example` documentará:

```dotenv
PORTA_BASE=4045
NUMERO_AGENCIAS=3
JWT_SECRET=substitua-por-segredo-local-forte
JWT_EXPIRACAO_MINUTOS=15
AUTH_USERNAME=aluno
AUTH_PASSWORD_HASH=substitua-por-hash-local
INTERNAL_TOKEN=substitua-por-token-interno-local
FRONTEND_ORIGIN=http://localhost:5173
TIMEOUT_AGENCIA_SEGUNDOS=3
RABBITMQ_URL=amqps://usuario:senha@host.cloudamqp.com/vhost
```

`AGENCIA_ID` será configurado separadamente em cada terminal e não precisa ficar no `.env` compartilhado.

### Regras para segredos

- nunca copiar os exemplos acima para produção;
- gerar valores localmente;
- não mostrar segredos em prints, logs ou vídeo;
- versionar somente `.env.example`;
- revisar `git diff --cached` antes de cada commit.

## Instalação do backend

```powershell
Set-Location agencia
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Se o PowerShell impedir a ativação do ambiente virtual, ajustar a política apenas para o processo atual, conforme as regras da instituição. Não alterar políticas globais sem entender o impacto.

## Execução das três agências

Abrir três terminais com o ambiente virtual ativado.

Terminal 1:

```powershell
Set-Location agencia
$env:AGENCIA_ID = "0"
python -m uvicorn iceibank.main:app --app-dir src --host 127.0.0.1 --port 4045 --workers 1
```

Terminal 2:

```powershell
Set-Location agencia
$env:AGENCIA_ID = "1"
python -m uvicorn iceibank.main:app --app-dir src --host 127.0.0.1 --port 4046 --workers 1
```

Terminal 3:

```powershell
Set-Location agencia
$env:AGENCIA_ID = "2"
python -m uvicorn iceibank.main:app --app-dir src --host 127.0.0.1 --port 4047 --workers 1
```

Não usar `--workers` maior que 1. Cada worker teria seu próprio relógio e uma conexão concorrente ao mesmo arquivo SQLite, o que está fora do modelo operacional desta entrega.

O modo `--reload` é aceitável durante desenvolvimento: ao reiniciar, a agência reabre seu arquivo SQLite e preserva os dados locais.

## Configuração do frontend

`frontend/.env.example` usa caminhos do proxy local:

```dotenv
VITE_AGENCIA_0_URL=/api/agencia-0
VITE_AGENCIA_1_URL=/api/agencia-1
VITE_AGENCIA_2_URL=/api/agencia-2
```

Instalação e execução:

```powershell
Set-Location frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`.

### Por que existe um proxy no Vite?

As agências permanecem nas portas obrigatórias 4045–4047. Entretanto, o Google Chrome classifica a porta 4045 como insegura e bloqueia requisições HTTP diretas com `ERR_UNSAFE_PORT`. O `vite.config.js` recebe chamadas do React em caminhos da própria porta 5173 e as encaminha no servidor de desenvolvimento:

| Caminho chamado pelo React | Destino real |
|---|---|
| `/api/agencia-0` | `http://127.0.0.1:4045` |
| `/api/agencia-1` | `http://127.0.0.1:4046` |
| `/api/agencia-2` | `http://127.0.0.1:4047` |

Isso não altera as portas do roteiro nem a comunicação direta entre os backends. Para servir o build `dist/` fora do Vite, o servidor web escolhido deverá reproduzir essas três regras de proxy.

## Verificações iniciais

### Cadastro de usuário

Na tela inicial, selecione **Não tenho usuário. Cadastrar**. Informe usuário (3 a 100
caracteres), senha (8 a 256 caracteres) e confirmação. Após cadastrar, o painel abre
automaticamente. Para validar o acesso entre agências, saia e entre com o mesmo usuário
selecionando outra agência. O usuário `aluno` continua disponível para demonstração.

A agência 0 deve estar ativa para cadastro e login em qualquer agência. Ela mantém os
usuários no arquivo `data/iceibank-agencia-0.sqlite3`; reiniciá-la preserva os cadastros.
As senhas não são salvas em `.env` nem em arquivos de log. SQLite usa a biblioteca padrão
do Python e não exige servidor de banco adicional.

### Portas ocupadas

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in 4045,4046,4047,5173 }
```

Antes de encerrar um processo, conferir o PID e confirmar que ele pertence ao ICEIBank.

### Login e token

Com as agências em execução:

```powershell
$credenciais = @{
  usuario = "aluno"
  senha = "senha-configurada-localmente"
} | ConvertTo-Json

$login = Invoke-RestMethod -Uri "http://localhost:4045/auth/login" -Method Post -ContentType "application/json" -Body $credenciais
$cabecalhos = @{ Authorization = "Bearer $($login.accessToken)" }
```

O valor do token não deve aparecer nas evidências entregues.

### Massa mínima de contas

```powershell
$conta0 = @{ id = 0; nomeAluno = "Ana"; saldoInicial = 200.00 } | ConvertTo-Json
$conta1 = @{ id = 1; nomeAluno = "Carla"; saldoInicial = 80.00 } | ConvertTo-Json
$conta2 = @{ id = 2; nomeAluno = "Diego"; saldoInicial = 60.00 } | ConvertTo-Json
$conta3 = @{ id = 3; nomeAluno = "Bruno"; saldoInicial = 50.00 } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:4045/contas" -Method Post -Headers $cabecalhos -ContentType "application/json" -Body $conta0
Invoke-RestMethod -Uri "http://localhost:4046/contas" -Method Post -Headers $cabecalhos -ContentType "application/json" -Body $conta1
Invoke-RestMethod -Uri "http://localhost:4047/contas" -Method Post -Headers $cabecalhos -ContentType "application/json" -Body $conta2
Invoke-RestMethod -Uri "http://localhost:4045/contas" -Method Post -Headers $cabecalhos -ContentType "application/json" -Body $conta3
```

## Mesclagem de logs

Com eventos já produzidos:

```powershell
Set-Location agencia
python scripts/mesclar_logs.py
```

O script equivalente em Python preserva o comportamento do exemplo `mesclar-logs.js` do roteiro. Essa adaptação deve ser explicada no README e, se houver dúvida sobre a exigência literal da extensão `.js`, confirmada com o professor.

## Testes

Backend:

```powershell
Set-Location agencia
pytest
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run build
```

Resultado de referência em 5 de outubro de 2026: 43 testes backend aprovados,
`ruff check src tests`, ESLint e build Vite aprovados. Para validar o backend
no ambiente virtual, executar `python -m ruff check src tests` e
`python -m pytest tests` dentro de `agencia`.

## Reinicialização do ambiente

Contas e demais dados locais persistem no arquivo SQLite de cada agência. Reiniciar uma
agência não os apaga, nem deve apagar automaticamente os JSONL. Para reiniciar a massa de
demonstração de modo previsível:

1. encerrar somente os processos do ICEIBank;
2. mover ou limpar conscientemente os logs da execução anterior;
3. se desejar zerar uma agência, remover conscientemente apenas
   `agencia/data/iceibank-agencia-{id}.sqlite3` com o processo dela parado;
4. iniciar as três agências;
5. recriar a massa de contas somente nas agências que foram zeradas;
6. executar os cenários na ordem do plano de testes.

Logs não devem ser removidos por um comando amplo ou recursivo. Confirmar sempre o diretório `agencia/data/` e os arquivos-alvo.

## Problemas comuns

| Sintoma | Causa provável | Verificação |
|---|---|---|
| agência inicia com identidade errada | `AGENCIA_ID` ausente | conferir variável no mesmo terminal |
| conta rejeitada | partição incompatível | calcular `id % 3` |
| React recebe erro de CORS | origem diferente de 5173 | conferir `FRONTEND_ORIGIN` |
| Chrome mostra `ERR_UNSAFE_PORT` | acesso direto à porta 4045 | abrir o React em 5173 e usar o proxy Vite |
| transferência remota retorna 401 | tokens internos diferentes | conferir configuração sem exibir valores |
| transferência remota retorna 502 | destino parado, URL ou timeout | conferir terminal/porta do destino |
| saldo desaparece após 502 | limitação intencional da sprint | registrar evidência; não implementar rollback |
| dados persistentes não aparecem | agência iniciou com outro `AGENCIA_ID` ou outro `data_dir` | conferir a identidade e o arquivo SQLite local |
| clocks divergentes no mesmo ID | mais de um worker | iniciar exatamente um worker |

## Referências

- [Arquitetura](specs/SPEC-001-arquitetura-sprint-1.md)
- [Contrato da API](API_SPRINT_1.md)
- [Plano de testes](PLANO_DE_TESTES_E_EVIDENCIAS.md)
