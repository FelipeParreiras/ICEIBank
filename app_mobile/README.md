# ICEIBank Mobile - Sprint 3

Cliente Flutter do ICEIBank. Implementa login JWT, consulta de saldo, depósito,
saque, transferência, painel de liderança e modo offline-first.

## Execução

1. Inicie as três agências FastAPI nas portas 4045, 4046 e 4047.
2. Em um emulador Android, execute:

   ```powershell
   Set-Location app_mobile
   flutter pub get
   flutter run --dart-define=API_HOST=10.0.2.2
   ```

Para dispositivo físico, substitua `10.0.2.2` pelo IP LAN da máquina que roda as
agências. O app deriva a agência responsável de cada conta por `id % 3`.

## Offline-first

O app persiste sessão, saldos consultados, vetores e a fila de depósitos/saques
pendentes em `shared_preferences`. Quando uma escrita falha por falta de conexão,
o saldo local é atualizado de forma provisória e a operação é enviada para
`POST /contas/{id}/sincronizar` após a reconexão. Uma resposta 409 preserva a
operação como conflito e atualiza na tela o saldo confirmado pela agência.

O painel de consenso consulta periodicamente `/bully/lider` e tenta as três
agências antes de declarar o estado indisponível.
