---
name: commit
description: Analisar exclusivamente todos os arquivos já staged no Git e gerar uma mensagem resumida em uma única frase no formato tipo/ descrição. Use quando o estudante pedir uma mensagem de commit ou solicitar o commit do conteúdo staged; nunca adicione arquivos ao staging.
---

# Commit

Respeite primeiro o protocolo definido no `AGENTS.md`. Esta skill realiza somente uma operação mecânica sobre conteúdo que o estudante já escolheu colocar em staging.

## Procedimento

1. Execute `git diff --cached --name-status`, `git diff --cached --stat` e `git diff --cached` para considerar todos os arquivos staged e somente eles.
2. Se não houver mudanças staged, informe isso e não gere uma mensagem fictícia.
3. Determine o tipo predominante pelo efeito conjunto das mudanças, não apenas pelo nome dos arquivos.
4. Produza exatamente uma linha no formato `tipo/ descrição resumida`.
5. Não use ponto final, lista, corpo, escopo entre parênteses, prefixo adicional ou múltiplas frases.
6. Não mencione detalhes que não estejam comprovados no diff staged.

## Tipos

- `docs`: somente documentação ou comentários documentais.
- `feat`: nova capacidade observável.
- `fix`: correção de comportamento defeituoso.
- `refactor`: reorganização sem alterar comportamento esperado.
- `test`: inclusão ou ajuste exclusivo de testes.
- `perf`: melhoria de desempenho.
- `build`: dependências, empacotamento ou processo de build.
- `ci`: automação de integração ou entrega contínua.
- `style`: formatação sem mudança lógica.
- `chore`: manutenção que não se encaixa nos tipos anteriores.

Quando houver tipos mistos, escolha o tipo que melhor representa o objetivo principal do conjunto staged. A descrição deve estar em português, ser específica, curta e resumir o resultado compartilhado por todos os arquivos relevantes.

## Execução do commit

Por padrão, apenas apresente a mensagem. Execute `git commit -m "tipo/ descrição"` somente quando o estudante pedir explicitamente para criar o commit. Nunca execute `git add`, `git commit --amend`, `git push` ou altere o staging por conta própria.
