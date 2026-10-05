# Registro de validação real - 04/10/2026

Uma instância CloudAMQP RabbitMQ foi conectada usando configuração local ignorada
pelo Git. Nenhuma URL, usuário, senha ou token é registrada neste arquivo.

## Transferência assíncrona

- Conta 0 (Agência 0): R$ 200,00.
- Conta 1 (Agência 1): R$ 10,00.
- Transferência de R$ 30,00: resposta HTTP informou publicação assíncrona.
- Após o consumo: origem R$ 170,00; destino R$ 40,00.

## Resiliência

- A Agência 1 foi parada depois de criar a conta 4.
- A transferência de R$ 20,00 para essa conta retornou publicação confirmada.
- Após reiniciar a Agência 1, a mensagem foi entregue e registrou
  `CREDITO_REMOTO_FALHOU` com `CONTA_NAO_ENCONTRADA`, pois as contas são em memória.

## Causalidade

O mesclador classificou como concorrentes as criações independentes com vetores
`[1, 0, 0]` na Agência 0 e `[0, 1, 0]` na Agência 1. O débito `[2, 0, 0]` e o
crédito remoto `[2, 3, 0]` não foram classificados como concorrentes.

As imagens PNG obrigatórias devem mostrar estas execuções reais com data/hora visível.
