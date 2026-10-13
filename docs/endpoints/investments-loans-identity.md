# Malvo — Investimentos, Crédito & Identidade

> Gerado a partir de `openapi/investments-loans-identity.json` por `scripts/generate_reference.py`. Não edite à mão.

Endpoints de leitura dos produtos de **Investimentos**, **Crédito (Empréstimos/Financiamentos)** e **Identidade** da Malvo. A API mantém paths, campos e enums estáveis e roda sobre um único host: `https://api.malvo.io`.

Todos os produtos pendem de um **item** (`itemId` = uma conexão usuário↔instituição). Estes endpoints apenas leem o que a última execução do item coletou — não disparam sincronização.

**Autenticação:** todo endpoint exige o header `X-API-KEY: <apiKey>`. Uma chave ausente/inválida retorna `403` com `codeDescription: API_KEY_MISSING_OR_INVALID`.

**Convenções:** datas em ISO 8601 UTC; valores monetários sempre como números JSON (nunca strings); códigos de moeda em ISO 4217 (`BRL`, `USD`); ids de recursos em UUID. A prosa é em pt-BR; campos e enums permanecem em inglês.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `GET /investments` — Listar investimentos
- `GET /investments/{id}` — Recuperar investimento
- `GET /investments/{id}/transactions` — Listar movimentações do investimento
- `GET /loans` — Listar operações de crédito
- `GET /loans/{id}` — Recuperar operação de crédito
- `GET /identity` — Buscar identidade por item
- `GET /identity/{id}` — Recuperar identidade

## GET /investments — Listar investimentos

Recupera todas as posições de investimento coletadas para o item informado. Resposta no formato de página `{ page, total, totalPages, results }`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemId` | query | `string (uuid)` | sim | Identificador primário do item. |
| `type` | query | `string` | não | Filtra por tipo de investimento. Valores: `COE`, `EQUITY`, `ETF`, `FIXED_INCOME`, `MUTUAL_FUND`, `SECURITY`, `OTHER`. |
| `pageSize` | query | `integer` | não | Tamanho da página. Padrão 500. Padrão: `500`. |
| `page` | query | `integer` | não | Página (1-based). Padrão 1. Padrão: `1`. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/investments?itemId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de investimentos.

```json
{
  "page": 1,
  "total": 3,
  "totalPages": 1,
  "results": [
    {
      "id": "f77eccf4-7714-498e-92a9-1bebe70335d9",
      "code": "12.345.678/0001-00",
      "name": "Bahia AM Advisory FIC de FIM",
      "balance": 1359.39,
      "currencyCode": "BRL",
      "type": "MUTUAL_FUND",
      "subtype": "MULTIMARKET_FUND",
      "lastMonthRate": 0.24,
      "annualRate": 3.24,
      "lastTwelveMonthsRate": 3,
      "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
      "value": 500,
      "quantity": 3,
      "amount": 1500,
      "taxes": 40.61,
      "taxes2": 100,
      "date": "2020-07-19T18:27:41.802Z",
      "owner": "John Doe",
      "number": null,
      "amountProfit": 310.5,
      "amountWithdrawal": 1310.5,
      "amountOriginal": 1000,
      "status": "ACTIVE"
    },
    {
      "id": "2a96b873-53bb-4d16-a3d8-385a57e78d7e",
      "number": null,
      "name": "CDB1194KL0Z - BANCO MAXIMA S/A",
      "balance": 2000,
      "currencyCode": "BRL",
      "type": "FIXED_INCOME",
      "subtype": "CDB",
      "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
      "code": "0001-02",
      "amount": 2500,
      "taxes": null,
      "taxes2": null,
      "date": "2020-07-19T18:27:41.802Z",
      "owner": "John Doe",
      "rate": 30,
      "rateType": "CDI",
      "fixedAnnualRate": 10.5,
      "amountProfit": null,
      "amountWithdrawal": 2000,
      "amountOriginal": 1000,
      "issuer": "Banco Exemplo S.A.",
      "issuerCNPJ": "08.050.608/0001-33",
      "issueDate": "2020-07-19T18:27:41.802Z",
      "purchaseDate": "2020-07-15T10:00:00.000Z",
      "status": "ACTIVE"
    },
    {
      "id": "ded7d2f1-6b90-44a8-9ace-de747b9f5bfe",
      "number": "123456-2",
      "name": "Previdência Exemplo",
      "balance": 1359.39,
      "currencyCode": "BRL",
      "type": "SECURITY",
      "subtype": "RETIREMENT",
      "annualRate": 3.24,
      "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
      "code": null,
      "value": 500,
      "quantity": 3,
      "amount": 1500,
      "taxes": 0,
      "taxes2": 0,
      "date": "2020-07-19T18:27:41.802Z",
      "owner": "John Doe",
      "amountProfit": 359.39,
      "amountWithdrawal": 1310.5,
      "status": "ACTIVE"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | `itemId` ausente ou inválido. |  |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /investments/{id} — Recuperar investimento

Retorna uma única posição de investimento pelo seu identificador.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário do investimento. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/investments/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Investment.

```json
{
  "id": "2a96b873-53bb-4d16-a3d8-385a57e78d7e",
  "number": null,
  "name": "CDB1194KL0Z - BANCO MAXIMA S/A",
  "balance": 2000,
  "currencyCode": "BRL",
  "type": "FIXED_INCOME",
  "subtype": "CDB",
  "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
  "code": "0001-02",
  "amount": 2500,
  "taxes": null,
  "taxes2": null,
  "date": "2020-07-19T18:27:41.802Z",
  "owner": "John Doe",
  "rate": 30,
  "rateType": "CDI",
  "fixedAnnualRate": 10.5,
  "amountProfit": null,
  "amountWithdrawal": 2000,
  "amountOriginal": 1000,
  "issuer": "Banco Exemplo S.A.",
  "issuerCNPJ": "08.050.608/0001-33",
  "issueDate": "2020-07-19T18:27:41.802Z",
  "purchaseDate": "2020-07-15T10:00:00.000Z",
  "status": "ACTIVE"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Investimento não encontrado. | `INVESTMENT_NOT_FOUND` |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /investments/{id}/transactions — Listar movimentações do investimento

Lista as movimentações (aplicações, resgates, impostos, juros, amortizações) de um investimento. Resposta no formato de página `{ total, totalPages, page, results }`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador do investimento. |
| `pageSize` | query | `integer` | não | Tamanho da página. Padrão 500. Padrão: `500`. |
| `page` | query | `integer` | não | Página (1-based). Padrão 1. Padrão: `1`. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/investments/3fa85f64-5717-4562-b3fc-2c963f66afa6/transactions" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de movimentações do investimento.

```json
{
  "total": 2,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": "910419d2-e833-41f2-af43-080693f7ef8a",
      "amount": 60000,
      "description": null,
      "value": 1200,
      "quantity": 50,
      "tradeDate": "2021-09-15T00:00:00.000Z",
      "date": "2021-09-15T00:00:00.000Z",
      "type": "SELL",
      "movementType": "DEBIT",
      "netAmount": null,
      "agreedRate": null,
      "brokerageNumber": null,
      "expenses": {}
    },
    {
      "id": "f24f7eec-5a5b-4e54-8727-d40b0b91115a",
      "amount": 110000,
      "description": null,
      "value": 1100,
      "quantity": 100,
      "tradeDate": "2021-09-01T00:00:00.000Z",
      "date": "2021-09-01T00:00:00.000Z",
      "type": "BUY",
      "movementType": "CREDIT",
      "netAmount": 10000,
      "agreedRate": null,
      "brokerageNumber": "1234",
      "expenses": {}
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /loans — Listar operações de crédito

Recupera todas as operações de crédito coletadas para o item informado. Resposta no formato de página `{ page, total, totalPages, results }` (página única).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemId` | query | `string (uuid)` | sim | Identificador primário do item. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/loans?itemId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de operações de crédito.

```json
{
  "page": 1,
  "total": 1,
  "totalPages": 1,
  "results": [
    {
      "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "itemId": "5e9f8f8f-f8f8-4f8f-8f8f-8f8f8f8f8f8f",
      "contractNumber": "000000721792794",
      "ipocCode": "92792126019929279212650822221989319252576",
      "productName": "Crédito Pessoal Consignado",
      "type": "CREDITO_PESSOAL_COM_CONSIGNACAO",
      "kind": "LOAN",
      "date": "2023-07-20T00:00:00",
      "contractDate": "2022-08-01T00:00:00",
      "disbursementDates": [
        "2018-01-15T00:00:00"
      ],
      "settlementDate": "2018-01-15T00:00:00",
      "contractAmount": 50000,
      "currencyCode": "BRL",
      "dueDate": "2028-01-15T00:00:00",
      "installmentPeriodicity": "MONTHLY",
      "installmentPeriodicityAdditionalInfo": "",
      "firstInstallmentDueDate": "2018-02-15T00:00:00",
      "CET": 0.29,
      "amortizationScheduled": "SAC",
      "amortizationScheduledAdditionalInfo": "",
      "cnpjConsignee": "60.500.998/0001-35",
      "interestRates": [
        {
          "taxType": "EFETIVA",
          "interestRateType": "SIMPLES",
          "taxPeriodicity": "AA",
          "calculation": "21/252",
          "referentialRateIndexerType": "PRE_FIXADO",
          "referentialRateIndexerSubType": "TJLP",
          "referentialRateIndexerAdditionalInfo": "",
          "preFixedRate": 0.6,
          "postFixedRate": 0.55,
          "additionalInfo": ""
        }
      ],
      "contractedFees": [
        {
          "name": "Renovação de cadastro",
          "code": "CADASTRO",
          "chargeType": "UNICA",
          "charge": "MINIMO",
          "amount": 100000.04,
          "rate": 0.062
        }
      ],
      "contractedFinanceCharges": [
        {
          "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
          "chargeAdditionalInfo": "",
          "chargeRate": 0.07
        }
      ],
      "warranties": [
        {
          "currencyCode": "BRL",
          "type": "CESSAO_DIREITOS_CREDITORIOS",
          "subtype": "NOTAS_PROMISSORIAS_OUTROS_DIREITOS_CREDITO",
          "amount": 1000.04
        }
      ],
      "installments": {
        "typeNumberOfInstallments": "MONTH",
        "totalNumberOfInstallments": 130632,
        "typeContractRemaining": "DAY",
        "contractRemainingNumber": 14600,
        "paidInstallments": 73,
        "dueInstallments": 57,
        "pastDueInstallments": 73,
        "balloonPayments": [
          {
            "dueDate": "2021-05-21T00:00:00",
            "amount": {
              "value": 1000.04,
              "currencyCode": "BRL"
            }
          }
        ]
      },
      "payments": {
        "contractOutstandingBalance": 1000.04,
        "releases": [
          {
            "isOverParcelPayment": true,
            "installmentId": "WGx0aExYcEJMVm93TFRsZFcyRXRla0V0V2pBdE9Wd3RYWH",
            "paidDate": "2021-05-21T00:00:00",
            "currencyCode": "BRL",
            "paidAmount": 1000.04,
            "overParcel": {
              "fees": [
                {
                  "name": "Reavaliação periódica do bem",
                  "code": "aval_bem",
                  "amount": 100000.04
                }
              ],
              "charges": [
                {
                  "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
                  "additionalInfo": "",
                  "amount": 1000.04
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | `itemId` ausente ou inválido. |  |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /loans/{id} — Recuperar operação de crédito

Retorna uma única operação de crédito pelo seu identificador.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da operação de crédito. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/loans/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Loan.

```json
{
  "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
  "itemId": "5e9f8f8f-f8f8-4f8f-8f8f-8f8f8f8f8f8f",
  "contractNumber": "000000721792794",
  "ipocCode": "92792126019929279212650822221989319252576",
  "productName": "Crédito Pessoal Consignado",
  "type": "CREDITO_PESSOAL_COM_CONSIGNACAO",
  "kind": "LOAN",
  "date": "2023-07-20T00:00:00",
  "contractDate": "2022-08-01T00:00:00",
  "disbursementDates": [
    "2018-01-15T00:00:00"
  ],
  "settlementDate": "2018-01-15T00:00:00",
  "contractAmount": 50000,
  "currencyCode": "BRL",
  "dueDate": "2028-01-15T00:00:00",
  "installmentPeriodicity": "MONTHLY",
  "installmentPeriodicityAdditionalInfo": "",
  "firstInstallmentDueDate": "2018-02-15T00:00:00",
  "CET": 0.29,
  "amortizationScheduled": "SAC",
  "amortizationScheduledAdditionalInfo": "",
  "cnpjConsignee": "60.500.998/0001-35",
  "interestRates": [
    {
      "taxType": "EFETIVA",
      "interestRateType": "SIMPLES",
      "taxPeriodicity": "AA",
      "calculation": "21/252",
      "referentialRateIndexerType": "PRE_FIXADO",
      "referentialRateIndexerSubType": "TJLP",
      "referentialRateIndexerAdditionalInfo": "",
      "preFixedRate": 0.6,
      "postFixedRate": 0.55,
      "additionalInfo": ""
    }
  ],
  "contractedFees": [
    {
      "name": "Renovação de cadastro",
      "code": "CADASTRO",
      "chargeType": "UNICA",
      "charge": "MINIMO",
      "amount": 100000.04,
      "rate": 0.062
    }
  ],
  "contractedFinanceCharges": [
    {
      "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
      "chargeAdditionalInfo": "",
      "chargeRate": 0.07
    }
  ],
  "warranties": [
    {
      "currencyCode": "BRL",
      "type": "CESSAO_DIREITOS_CREDITORIOS",
      "subtype": "NOTAS_PROMISSORIAS_OUTROS_DIREITOS_CREDITO",
      "amount": 1000.04
    }
  ],
  "installments": {
    "typeNumberOfInstallments": "MONTH",
    "totalNumberOfInstallments": 130632,
    "typeContractRemaining": "DAY",
    "contractRemainingNumber": 14600,
    "paidInstallments": 73,
    "dueInstallments": 57,
    "pastDueInstallments": 73,
    "balloonPayments": [
      {
        "dueDate": "2021-05-21T00:00:00",
        "amount": {
          "value": 1000.04,
          "currencyCode": "BRL"
        }
      }
    ]
  },
  "payments": {
    "contractOutstandingBalance": 1000.04,
    "releases": [
      {
        "isOverParcelPayment": true,
        "installmentId": "WGx0aExYcEJMVm93TFRsZFcyRXRla0V0V2pBdE9Wd3RYWH",
        "paidDate": "2021-05-21T00:00:00",
        "currencyCode": "BRL",
        "paidAmount": 1000.04,
        "overParcel": {
          "fees": [
            {
              "name": "Reavaliação periódica do bem",
              "code": "aval_bem",
              "amount": 100000.04
            }
          ],
          "charges": [
            {
              "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
              "additionalInfo": "",
              "amount": 1000.04
            }
          ]
        }
      }
    ]
  }
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Operação de crédito não encontrada. | `LOAN_NOT_FOUND` |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /identity — Buscar identidade por item

Retorna os dados cadastrais do titular do item informado. **A resposta é um objeto único `IdentityResponse`** — NÃO é um envelope paginado.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemId` | query | `string (uuid)` | sim | Identificador primário do item. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/identity?itemId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto IdentityResponse.

```json
{
  "id": "42888436-62f5-49d2-8cf9-e312c7939509",
  "itemId": "a0922d6f-2007-4169-a181-b961500608db",
  "fullName": "Francisco Sousa",
  "companyName": "Empresa Exemplo Ltda",
  "document": "076.630.975-49",
  "taxNumber": "38.512.121/0001-96",
  "documentType": "CPF",
  "jobTitle": "Comercial",
  "birthDate": "1991-05-01T00:00:00.000Z",
  "establishmentCode": "001",
  "establishmentName": "Estabelecimento Exemplo",
  "addresses": [
    {
      "fullAddress": "Av. Lúcio Costa 1234, Copacabana, Rio de Janeiro, Brasil",
      "country": "Brasil",
      "state": "RJ",
      "city": "Rio de Janeiro",
      "postalCode": "22620-171",
      "primaryAddress": "Av. Lúcio Costa, 1234",
      "type": "Personal",
      "additionalInfo": "Apartamento 101"
    }
  ],
  "phoneNumbers": [
    {
      "type": "Personal",
      "value": "+54 911 12345678"
    }
  ],
  "emails": [
    {
      "type": "Personal",
      "value": "maria.silva@example.com"
    }
  ],
  "relations": [
    {
      "type": "Father",
      "name": "Juan Gonzalez"
    },
    {
      "type": "Spouse",
      "name": "Laura Garcia"
    }
  ],
  "createdAt": "2020-09-30T14:38:12.724Z",
  "updatedAt": "2020-09-30T14:38:12.724Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | `itemId` inválido. |  |
| `404` | Identidade não encontrada. | `IDENTITY_NOT_FOUND` |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |

## GET /identity/{id} — Recuperar identidade

Retorna os dados cadastrais pelo identificador da identidade. **A resposta é um objeto único `IdentityResponse`** — NÃO é um envelope paginado.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da identidade. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/identity/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto IdentityResponse.

```json
{
  "id": "42888436-62f5-49d2-8cf9-e312c7939509",
  "itemId": "a0922d6f-2007-4169-a181-b961500608db",
  "fullName": "Francisco Sousa",
  "companyName": "Empresa Exemplo Ltda",
  "document": "076.630.975-49",
  "taxNumber": "38.512.121/0001-96",
  "documentType": "CPF",
  "jobTitle": "Comercial",
  "birthDate": "1991-05-01T00:00:00.000Z",
  "establishmentCode": "001",
  "establishmentName": "Estabelecimento Exemplo",
  "addresses": [
    {
      "fullAddress": "Av. Lúcio Costa 1234, Copacabana, Rio de Janeiro, Brasil",
      "country": "Brasil",
      "state": "RJ",
      "city": "Rio de Janeiro",
      "postalCode": "22620-171",
      "primaryAddress": "Av. Lúcio Costa, 1234",
      "type": "Personal",
      "additionalInfo": "Apartamento 101"
    }
  ],
  "phoneNumbers": [
    {
      "type": "Personal",
      "value": "+54 911 12345678"
    }
  ],
  "emails": [
    {
      "type": "Personal",
      "value": "maria.silva@example.com"
    }
  ],
  "relations": [
    {
      "type": "Father",
      "name": "Juan Gonzalez"
    },
    {
      "type": "Spouse",
      "name": "Laura Garcia"
    }
  ],
  "createdAt": "2020-09-30T14:38:12.724Z",
  "updatedAt": "2020-09-30T14:38:12.724Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Identificador inválido. |  |
| `404` | Identidade não encontrada. | `IDENTITY_NOT_FOUND` |
| `403` | Chave de API ausente ou inválida. | `API_KEY_MISSING_OR_INVALID` |
| `500` | Erro interno. | `INTERNAL_SERVER_ERROR` |
