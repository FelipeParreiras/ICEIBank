# ICEIBank

Projeto acadêmico de um banco distribuído, desenvolvido incrementalmente ao longo de quatro sprints.

O repositório está atualmente na fase de preparação arquitetural. Ainda não há funcionalidades implementadas.

## Ambiente local

Requisitos:

- Python 3.13
- PowerShell 7 (recomendado no Windows)

Preparação inicial:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Ativação nas próximas sessões:

```powershell
.\.venv\Scripts\Activate.ps1
```

Comandos de qualidade disponíveis após a instalação:

```powershell
ruff check .
ruff format --check .
mypy src
pytest
```

## Organização

- `src/iceibank`: código-fonte futuro, organizado por responsabilidade.
- `tests`: testes unitários e de integração futuros.
- `docs/architecture`: visão e restrições arquiteturais.
- `docs/specs`: especificações funcionais e técnicas.
- `docs/adrs`: registros de decisões arquiteturais (ADRs).
- `roteiro.md`: roteiro acadêmico original do projeto.

Consulte [docs/README.md](docs/README.md) para navegar pela documentação.
