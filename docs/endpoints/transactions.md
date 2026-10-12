# Malvo — Transações & Categorias

> Gerado a partir de `openapi/transactions.json` por `scripts/generate_reference.py`. Não edite à mão.

Endpoints de leitura de transações, categorias de transação, regras de categoria do cliente e busca de estabelecimentos (merchants) por CNPJ na API da Malvo. O contrato wire mantém paths, campos e formatos estáveis. Todos os endpoints exigem o header `X-API-KEY`. As transações cobrem até 12 meses de histórico e refletem o que a última execução do item coletou — estes endpoints não disparam sincronização. Prosa em pt-BR; nomes de campos e enums em inglês, como na wire.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `GET /v2/transactions` — Listar transações (cursor-based, atual)
- `GET /transactions` — Listar transações (page-based, deprecado)
- `GET /transactions/{id}` — Recuperar transação
- `PATCH /transactions/{id}` — Atualizar categoria da transação
- `GET /categories` — Listar categorias
- `GET /categories/{id}` — Recuperar categoria
- `GET /categories/rules` — Listar regras de categoria
- `POST /categories/rules` — Criar regra de categoria
- `GET /merchants` — Buscar estabelecimentos por CNPJ

## GET /v2/transactions — Listar transações (cursor-based, atual)

**Endpoint atual.** Lista as transações de uma conta usando paginação por cursor. Não há parâmetro `pageSize`: o servidor controla o tamanho da página (500 por página). Continue requisitando com a query string retornada em `next` (ou extraia o `after`) até que `next` seja `null`. O cursor codifica `date|id` da última linha (base64) — trate-o como opaco.

Filtra por `accountId` (obrigatório) — não há filtro por `itemId`. `dateFrom` **não pode** ser combinado com `createdAtFrom`. Cobre até 12 meses de histórico.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `accountId` | query | `string (uuid)` | sim | Identificador primário da conta. |
| `ids` | query | `string` | não | Lista de ids de transação separados por vírgula. Máximo de 500 ids por requisição. |
| `dateFrom` | query | `string (date)` | não | Transações com `date >= dateFrom` (inclusive). Formato `yyyy-mm-dd`. **Não pode ser combinado com `createdAtFrom`.** |
| `dateTo` | query | `string (date)` | não | Transações com `date <= dateTo` (inclusive). Formato `yyyy-mm-dd`. |
| `createdAtFrom` | query | `string (date-time)` | não | Filtra por horário de ingestão (`createdAt`) — use para sincronização incremental. Formato `yyyy-mm-ddThh:mm:ss.000Z`. |
| `after` | query | `string` | não | Cursor opaco obtido do campo `next` da resposta anterior. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/v2/transactions?accountId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de transações com cursor para a próxima página.

```json
{
  "results": [
    {
      "id": "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
      "description": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
      "descriptionRaw": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
      "currencyCode": "BRL",
      "amount": -212.45,
      "date": "2020-10-15T00:00:00.000Z",
      "balance": 4439.4,
      "category": "Fixed Income Investment",
      "accountId": "562b795d-1653-429f-be86-74ead9502813",
      "providerCode": null,
      "status": "POSTED",
      "paymentData": null,
      "type": "DEBIT",
      "providerId": null
    }
  ],
  "next": "?accountId=562b795d-1653-429f-be86-74ead9502813&after=MjAyMC0xMC0xNVQwMDowMDowMC4wMDBafGE4NTM0Yzg1LTUzY2UtNGYyMS05NGQ3LTUwZTlkMmVlNDk1Nw=="
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Parâmetros inválidos: `accountId` ausente/inválido, cursor inválido ou excesso de ids. | `IDS_PARAMETER_EXCEEDS_MAX_LENGTH` |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /transactions — Listar transações (page-based, deprecado)

> **Depreciada.**

**Deprecado.** Lista as transações de uma conta usando paginação por página (envelope `{ total, totalPages, page, results }`). Mantido por compatibilidade. Prefira `GET /v2/transactions` (cursor-based).

Filtra por `accountId` (obrigatório) — não há filtro por `itemId`. Se `ids` for informado, `from`/`to` são descartados. Cobre até 12 meses de histórico.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `accountId` | query | `string (uuid)` | sim | Identificador primário da conta. |
| `ids` | query | `array<string (uuid)>` | não | Lista de ids de transação. Se informado, `from`/`to` são descartados. |
| `from` | query | `string (date)` | não | Filtra `date >= from`. Formato `yyyy-mm-dd`. |
| `to` | query | `string (date)` | não | Filtra `date <= to`. Formato `yyyy-mm-dd`. |
| `pageSize` | query | `integer` | não | Tamanho da página (1–500). Padrão 500. Padrão: `500`. |
| `page` | query | `integer` | não | Página (1-based). Padrão 1. Padrão: `1`. |
| `createdAtFrom` | query | `string (date-time)` | não | Filtra por horário de ingestão. Formato `yyyy-mm-ddThh:mm:ss.000Z`. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/transactions?accountId=3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de transações (envelope paginado).

```json
{
  "total": 8,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
      "description": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
      "descriptionRaw": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
      "currencyCode": "BRL",
      "amount": -212.45,
      "date": "2020-10-15T00:00:00.000Z",
      "balance": 4439.4,
      "category": "Fixed Income Investment",
      "accountId": "562b795d-1653-429f-be86-74ead9502813",
      "providerCode": null,
      "status": "POSTED",
      "paymentData": null,
      "type": "DEBIT",
      "providerId": null
    },
    {
      "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "description": "PAGO NETFLIX SERV",
      "descriptionRaw": "PAGO NETFLIX SERV",
      "currencyCode": "USD",
      "amount": -58,
      "amountInAccountCurrency": -298.19,
      "date": "2020-10-15T00:00:00.000Z",
      "balance": 4651.85,
      "category": "Video streaming",
      "accountId": "562b795d-1653-429f-be86-74ead9502813",
      "providerCode": null,
      "status": "POSTED",
      "paymentData": null,
      "type": "DEBIT",
      "providerId": null,
      "merchant": {
        "name": "Netflix",
        "businessName": "NETFLIX ENTRETENIMENTO BRASIL LTDA.",
        "cnpj": "00000000000000",
        "category": "Video streaming",
        "cnae": "5911100"
      }
    },
    {
      "id": "ff9ed929-edc4-408c-a959-d51f79ab1814",
      "description": "MERCADOLIVRE*2PRODUTOS",
      "currencyCode": "BRL",
      "amount": 159.2,
      "date": "2020-10-14T00:00:00.000Z",
      "balance": 2468.84,
      "category": "Investment",
      "accountId": "562b795d-1653-429f-be86-74ead9502813",
      "providerCode": null,
      "status": "POSTED",
      "paymentData": null,
      "type": "CREDIT",
      "creditCardMetadata": {
        "totalAmount": 320,
        "totalInstallments": 2,
        "installmentNumber": 2,
        "purchaseDate": "2020-09-14T00:00:00.000Z",
        "payeeMCC": 1234,
        "cardNumber": "0597",
        "billId": "abced929-edc4-408c-a959-d51f79ab1123"
      },
      "providerId": null
    },
    {
      "id": "6ec156fe-e8ac-4d9a-a4b3-7770529ab01c",
      "description": "TED Example",
      "descriptionRaw": null,
      "currencyCode": "BRL",
      "amount": 1500,
      "date": "2020-10-14T00:00:00.000Z",
      "balance": 3500,
      "category": "Transfer",
      "accountId": "03cc0eff-4ec5-495c-adb3-1ef9611624fc",
      "providerCode": "123456",
      "type": "CREDIT",
      "status": "POSTED",
      "operationType": "TED",
      "paymentData": {
        "payer": {
          "name": "Tiago Rodrigues Santos",
          "branchNumber": "090",
          "accountNumber": "1234-5",
          "routingNumber": "001",
          "documentNumber": {
            "type": "CPF",
            "value": "882.937.076-24"
          }
        },
        "reason": "Taxa de serviço",
        "receiver": {
          "name": "Loja Exemplo Ltda",
          "branchNumber": "999",
          "accountNumber": "9876-1",
          "routingNumber": "002",
          "documentNumber": {
            "type": "CNPJ",
            "value": "08.050.608/0001-33"
          }
        },
        "paymentMethod": "TED",
        "referenceNumber": "123456789"
      },
      "providerId": null
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Parâmetros inválidos (ex.: `accountId` ausente ou não-UUID). |  |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /transactions/{id} — Recuperar transação

Recupera uma transação pelo seu identificador primário.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da transação. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/transactions/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Transaction.

```json
{
  "id": "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
  "description": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
  "descriptionRaw": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
  "currencyCode": "BRL",
  "amount": -212.45,
  "date": "2020-10-15T00:00:00.000Z",
  "balance": 4439.4,
  "category": "Fixed Income Investment",
  "accountId": "562b795d-1653-429f-be86-74ead9502813",
  "providerCode": null,
  "status": "POSTED",
  "paymentData": null,
  "type": "DEBIT",
  "providerId": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Transação não encontrada. | `TRANSACTION_NOT_FOUND` |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## PATCH /transactions/{id} — Atualizar categoria da transação

Recategoriza uma transação. A correção é persistida (leituras subsequentes retornam a categoria corrigida), alimenta o classificador e cria automaticamente uma **Category Rule** para o cliente (veja `POST /categories/rules`).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador primário da transação. |

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `categoryId` | `string` | sim | Id da categoria a atribuir (8 dígitos numéricos). |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/transactions/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "categoryId": "07010000"
}'
```

### Resposta 200

A transação atualizada (objeto completo, com `category` + `categoryId` novos).

```json
{
  "id": "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
  "description": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
  "descriptionRaw": "* PROV * COMPRA TESOURO DIRETO CLIENTES",
  "currencyCode": "BRL",
  "amount": -212.45,
  "date": "2020-10-15T00:00:00.000Z",
  "balance": 4439.4,
  "category": "Telecommunications",
  "categoryId": "07010000",
  "accountId": "562b795d-1653-429f-be86-74ead9502813",
  "providerCode": null,
  "status": "POSTED",
  "paymentData": null,
  "type": "DEBIT",
  "providerId": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Id de transação inválido ou corpo malformado. |  |
| `404` | Transação não encontrada. |  |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /categories — Listar categorias

Lista o catálogo de categorias de transação. Informe `parentId` para retornar apenas os filhos de uma categoria. Envelope paginado de página única (`totalPages` é sempre 1).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `parentId` | query | `string` | não | Retorna apenas os filhos dessa categoria. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/categories" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de categorias.

```json
{
  "page": 1,
  "total": 2,
  "totalPages": 1,
  "results": [
    {
      "id": "01000000",
      "description": "Income",
      "descriptionTranslated": "Renda"
    },
    {
      "id": "01010000",
      "description": "Salary/pro-labore",
      "descriptionTranslated": "Salário",
      "parentId": "01000000",
      "parentDescription": "Income"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /categories/{id} — Recuperar categoria

Recupera uma categoria pelo seu id (8 dígitos numéricos).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string` | sim | Id da categoria (8 dígitos numéricos). |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/categories/01010000" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Category.

```json
{
  "id": "01010000",
  "description": "Salary/pro-labore",
  "descriptionTranslated": "Salário",
  "parentId": "01000000",
  "parentDescription": "Income"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Categoria não encontrada. | `CATEGORY_NOT_FOUND` |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /categories/rules — Listar regras de categoria

Lista as regras de categoria do cliente (page shape). As regras são **client-wide** (escopadas ao `clientId` da API), não por item nem por usuário.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/categories/rules" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Página de regras de categoria.

```json
{
  "page": 1,
  "total": 1,
  "totalPages": 1,
  "results": [
    {
      "description": "uber payment",
      "category": "Salary/pro-labore",
      "categoryId": "05000000",
      "clientId": "03cc0eff-4ec5-495c-adb3-1ef9611624fc",
      "transactionType": "DEBIT",
      "accountType": "CHECKING_ACCOUNT"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## POST /categories/rules — Criar regra de categoria

Cria uma regra de categoria do cliente. O texto em `description` é casado contra as descrições das transações (case-insensitive). As regras são aplicadas ANTES do classificador. `category` na resposta é a descrição resolvida de `categoryId`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `description` | `string` | sim | Texto casado contra as descrições das transações (case-insensitive). |
| `categoryId` | `string` | sim | Categoria a atribuir. |
| `transactionType` | `string` | não | Restringe a regra a transações `DEBIT` ou `CREDIT`. Valores: `DEBIT`, `CREDIT`. |
| `accountType` | `string` | não | Restringe a regra a contas `CHECKING_ACCOUNT` ou `CREDIT_CARD`. Valores: `CHECKING_ACCOUNT`, `CREDIT_CARD`. |
| `matchType` | `string` | não | Modo de correspondência. Padrão `exact`. Valores: `exact`, `contains`, `startsWith`, `endsWith`. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/categories/rules" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "description": "uber payment",
  "categoryId": "05000000",
  "transactionType": "DEBIT",
  "accountType": "CHECKING_ACCOUNT"
}'
```

### Resposta 200

A regra criada.

```json
{
  "description": "uber payment",
  "category": "Salary/pro-labore",
  "categoryId": "05000000",
  "clientId": "03cc0eff-4ec5-495c-adb3-1ef9611624fc",
  "transactionType": "DEBIT",
  "accountType": "CHECKING_ACCOUNT"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Corpo inválido (ex.: `description` ausente/não-string). |  |
| `404` | `categoryId` não corresponde a nenhuma categoria. | `CATEGORY_NOT_FOUND` |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |

## GET /merchants — Buscar estabelecimentos por CNPJ

Resolve uma lista de CNPJs em registros de estabelecimento. Cada CNPJ submetido cai em exatamente um dos três buckets: `foundMerchants`, `notFoundMerchants` (CNPJs válidos ausentes da base) ou `invalidCnpjs` (entradas malformadas).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `cnpjs` | query | `string` | sim | Lista de CNPJs separados por vírgula, **somente dígitos** (ex.: `00000000000192,60701190000105`). |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/merchants?cnpjs=00000000000192,60701190000105" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Resultado da busca, particionado em três buckets.

```json
{
  "foundMerchants": [
    {
      "businessName": "BANCO EXEMPLO S.A.",
      "cnpj": "00000000000192",
      "name": "BANCO DO BRASIL",
      "cnae": "6422100",
      "category": "Banking"
    }
  ],
  "notFoundMerchants": [],
  "invalidCnpjs": []
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Parâmetro `cnpjs` ausente ou malformado. |  |
| `500` | Erro interno do servidor. | `INTERNAL_SERVER_ERROR` |
