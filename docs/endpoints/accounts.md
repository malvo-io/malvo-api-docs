# Malvo — Contas & Faturas

> Gerado a partir de `openapi/accounts.json` por `scripts/generate_reference.py`. Não edite à mão.

API de Contas (Accounts) e Faturas de cartão de crédito (Credit Card Bills) da Malvo, com contrato público estável. Autenticação por header X-API-KEY em todas as rotas. Os produtos pendem de um item (itemId = uma conexão usuário↔instituição). Convenção de saldo (campo `balance` em Account): para contas bancárias (type=BANK) representa o dinheiro disponível agora (negativo indica uso de cheque especial); para cartões de crédito (type=CREDIT) representa o valor da fatura atualmente em aberto. Host único: https://api.malvo.io.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `GET /accounts` — Listar contas
- `GET /accounts/{id}` — Recuperar conta
- `GET /accounts/{id}/balance` — Saldo mais recente
- `GET /accounts/{id}/statements` — Listar extratos da conta
- `GET /bills` — Listar faturas
- `GET /bills/{id}` — Recuperar fatura

## GET /accounts — Listar contas

Recupera todas as contas coletadas para o item informado.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemId` | query | `string (uuid)` | sim | Identificador primário do item. |
| `type` | query | `string` | não | Filtra entre contas bancárias e contas de crédito. Valores: `BANK`, `CREDIT`. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/accounts?itemId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado com a lista de contas.

```json
{
  "page": 1,
  "total": 2,
  "totalPages": 1,
  "results": [
    {
      "id": "a658c848-e475-457b-8565-d1fffba127c4",
      "type": "BANK",
      "subtype": "CHECKING_ACCOUNT",
      "number": "0001/12345-0",
      "name": "Conta Corrente",
      "marketingName": "GOLD Conta Corrente",
      "balance": 120950,
      "balanceAvailable": true,
      "balanceUpdatedAt": "2026-07-19T12:00:00.000Z",
      "itemId": "a0922d6f-2007-4169-a181-b961500608db",
      "taxNumber": "416.799.495-01",
      "owner": "John Doe",
      "currencyCode": "BRL",
      "bankData": {
        "transferNumber": "0001/12345-0",
        "closingBalance": 120950,
        "automaticallyInvestedBalance": 100,
        "overdraftContractedLimit": 0,
        "overdraftUsedLimit": 0,
        "unarrangedOverdraftAmount": 0
      }
    },
    {
      "id": "a658c848-e475-457b-8565-d1fffba127c4",
      "type": "CREDIT",
      "subtype": "CREDIT_CARD",
      "number": "xxxx8670",
      "name": "Mastercard Black",
      "marketingName": "BANCO EXEMPLO MASTERCARD BLACK",
      "balance": 120950,
      "balanceAvailable": true,
      "balanceUpdatedAt": "2026-07-19T12:00:00.000Z",
      "itemId": "a0922d6f-2007-4169-a181-b961500608db",
      "taxNumber": "416.799.495-01",
      "owner": "John Doe",
      "currencyCode": "BRL",
      "creditData": {
        "level": "BLACK",
        "brand": "MASTERCARD",
        "balanceCloseDate": "2022-01-03",
        "balanceDueDate": "2022-01-03",
        "availableCreditLimit": 200000,
        "balanceForeignCurrency": 0,
        "minimumPayment": 16190,
        "creditLimit": 300000,
        "status": "ACTIVE",
        "holderType": "MAIN"
      }
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | itemId ausente ou inválido. |  |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /accounts/{id} — Recuperar conta

Recupera uma única conta pelo seu identificador primário.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da conta. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/accounts/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Account.

```json
{
  "id": "a658c848-e475-457b-8565-d1fffba127c4",
  "type": "BANK",
  "subtype": "CHECKING_ACCOUNT",
  "number": "0001/12345-0",
  "name": "Conta Corrente",
  "marketingName": "GOLD Conta Corrente",
  "balance": 120950,
  "balanceAvailable": true,
  "balanceUpdatedAt": "2026-07-19T12:00:00.000Z",
  "itemId": "a0922d6f-2007-4169-a181-b961500608db",
  "taxNumber": "416.799.495-01",
  "owner": "John Doe",
  "currencyCode": "BRL",
  "bankData": {
    "transferNumber": "0001/12345-0",
    "closingBalance": 120950,
    "automaticallyInvestedBalance": 100,
    "overdraftContractedLimit": 0,
    "overdraftUsedLimit": 0,
    "unarrangedOverdraftAmount": 0
  }
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Conta não encontrada. | `ACCOUNT_NOT_FOUND` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /accounts/{id}/balance — Saldo mais recente

Retorna o último saldo persistido pela sincronização do Item; esta leitura não chama a instituição. `updateDateTime` informa quando o provedor coletou o saldo. Em contas multimoeda ou respostas que não admitem um scalar fiel, `balanceAvailable=false`, `balance=null` e `balances` preserva o conjunto recebido.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da conta. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/accounts/3fa85f64-5717-4562-b3fc-2c963f66afa6/balance" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Último saldo coletado.

```json
{
  "balance": 1500.5,
  "balanceAvailable": true,
  "blockedBalance": 0,
  "automaticallyInvestedBalance": 200,
  "currencyCode": "BRL",
  "updateDateTime": "2024-01-15T10:30:00Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Conta não encontrada. |  |
| `500` | Erro ao carregar o saldo persistido. |  |

## GET /accounts/{id}/statements — Listar extratos da conta

Recupera todos os extratos (PDF) coletados para a conta. O campo `url` é uma URL assinada válida por 30 minutos. O formato de `monthYear` é MM-YYYY.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da conta. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/accounts/3fa85f64-5717-4562-b3fc-2c963f66afa6/statements" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado com os extratos.

```json
{
  "total": 2,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
      "monthYear": "01-2025",
      "url": "https://files.example.com/bills/statement.pdf?signature=<SIGNATURE>"
    },
    {
      "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "monthYear": "02-2025",
      "url": "https://files.example.com/bills/statement.pdf?signature=<SIGNATURE>"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | accountId ausente ou inválido. |  |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /bills — Listar faturas

Lista as faturas de uma conta de cartão de crédito. O parâmetro accountId é obrigatório e deve referenciar uma conta de subtipo CREDIT_CARD.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `accountId` | query | `string (uuid)` | sim | Identificador da conta de cartão de crédito (subtipo CREDIT_CARD). |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/bills?accountId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado com a lista de faturas.

```json
{
  "page": 1,
  "total": 1,
  "totalPages": 1,
  "results": [
    {
      "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "dueDate": "2023-07-20T00:00:00",
      "totalAmount": 50000,
      "totalAmountCurrencyCode": "BRL",
      "minimumPaymentAmount": 50000,
      "allowsInstallments": true,
      "financeCharges": [
        {
          "id": "123456bf-c196-47ea-a28c-8251d6bb8777",
          "type": "IOF",
          "amount": 20.51,
          "currencyCode": "BRL",
          "additionalInfo": "NA"
        }
      ]
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | accountId ausente ou inválido. |  |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /bills/{id} — Recuperar fatura

Recupera uma única fatura pelo seu identificador. Na recuperação individual, os campos `accountId` (na fatura) e `creditCardBillId` (em cada finance charge) também são retornados.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da fatura. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/bills/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Bill.

```json
{
  "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
  "accountId": "5e9f8f8f-f8f8-4f8f-8f8f-8f8f8f8f8f8f",
  "dueDate": "2023-07-20T00:00:00",
  "totalAmount": 50000,
  "totalAmountCurrencyCode": "BRL",
  "minimumPaymentAmount": 50000,
  "allowsInstallments": true,
  "financeCharges": [
    {
      "id": "123456bf-c196-47ea-a28c-8251d6bb8777",
      "creditCardBillId": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "type": "IOF",
      "amount": 20.51,
      "currencyCode": "BRL",
      "additionalInfo": "NA"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Fatura não encontrada. | `CREDIT_CARD_BILL_NOT_FOUND` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |
