# Malvo — Autenticação & Conectores

> Gerado a partir de `openapi/auth.json` por `scripts/generate_reference.py`. Não edite à mão.

API da Malvo para autenticação por credenciais de cliente, emissão de tokens do Connect Widget, consulta de conectores e consentimentos de Open Finance. Contrato público estável, sem iniciação de pagamentos.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `POST /auth` — Troca credenciais de cliente por uma apiKey
- `POST /connect_token` — Emite um token com escopo do Connect Widget
- `GET /connectors` — Lista os conectores disponíveis
- `GET /connectors/{id}` — Consulta um conector pelo id
- `GET /consents` — Lista consentimentos de um item
- `GET /consents/{id}` — Consulta um consentimento pelo id

## POST /auth — Troca credenciais de cliente por uma apiKey

Recebe `clientId` e `clientSecret` (emitidos no Dashboard, uso server-side apenas) e devolve uma `apiKey` com TTL de 2 horas. A apiKey é enviada no header `X-API-KEY` nas demais chamadas server-side. Esta operação NÃO exige header de autenticação.

**Autenticação:** nenhuma. Esta rota não usa o header `X-API-KEY`.

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `clientId` | `string (uuid)` | sim | Emitido no Dashboard por Application. |
| `clientSecret` | `string` | sim | Segredo opaco emitido junto ao clientId; uso server-side apenas. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/auth" \
  -H "Content-Type: application/json" \
  -d '{
  "clientId": "<CLIENT_ID>",
  "clientSecret": "<CLIENT_SECRET>"
}'
```

### Resposta 200

apiKey emitida com sucesso (TTL de 2 horas).

```json
{
  "apiKey": "<API_KEY>"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | Credenciais inválidas (`CLIENT_KEYS_UNAUTHORIZED`) ou Application desabilitada (`CLIENT_DISABLED`). | `CLIENT_KEYS_UNAUTHORIZED`, `CLIENT_DISABLED` |
| `500` | Falha interna do servidor — repetir com backoff. | `INTERNAL_SERVER_ERROR` |

## POST /connect_token — Emite um token com escopo do Connect Widget

Gera um `accessToken` de 30 minutos para dirigir o Connect Widget. Todos os campos são opcionais — um corpo `{}` retorna um token para criar um novo item. Passe `itemId` apenas para colocar o widget em modo de atualização de um item existente. ATENÇÃO: falha de autenticação aqui retorna 403 (não 401) — trate como "renove a apiKey via POST /auth e tente novamente".

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `itemId` | `string (uuid)` | não | Informe apenas para colocar o widget em modo de atualização de um item existente (re-auth / MFA / renovação de consentimento). Omita para criar um novo item. |
| `options` | `ConnectTokenOptions` | não | Opções de conexão por token, todas opcionais. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/connect_token" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "itemId": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "options": {
    "clientUserId": "my-user-42",
    "webhookUrl": "https://your.app/webhooks/malvo",
    "oauthRedirectUri": "https://your.app/oauth/callback",
    "avoidDuplicates": true,
    "products": [
      "ACCOUNTS",
      "TRANSACTIONS"
    ]
  }
}'
```

### Resposta 201

Token do widget emitido com sucesso (TTL de 30 minutos).

```json
{
  "accessToken": "<CONNECT_TOKEN>"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `402` | Saldo de créditos pré-pagos zerado (`CREDITS_EXHAUSTED`). Novas conexões ficam pausadas até a recarga; os dados existentes continuam acessíveis. Ativo para contas novas desde 04/10/2026 e para as existentes a partir de 01/12/2026 — veja [Créditos pré-pagos](https://docs.malvo.io/dashboard/credits). | `CREDITS_EXHAUSTED` |
| `403` | Header `X-API-KEY` ausente, malformado ou expirado. Diferente das demais rotas, aqui a falha de autenticação surge como 403, não 401. |  |
| `404` | O `itemId` informado para atualização não existe ou foi removido. | `ITEM_NOT_FOUND` |
| `500` | Falha interna do servidor — repetir com backoff. | `INTERNAL_SERVER_ERROR` |

## GET /connectors — Lista os conectores disponíveis

Retorna o envelope paginado de conectores acessíveis à Application autenticada. O catálogo real é dinâmico: Open Finance Brasil e instituições AIS internacionais nas jurisdições habilitadas. Trate ids como opacos e use `isOpenFinance=true`, `countries`, `types` e `products` para filtrar.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `name` | query | `string` | não | Busca parcial e case-insensitive no `name` do conector. |
| `countries` | query | `string` | não | Filtra por país ISO-3166-1 alpha-2. Aceita lista separada por vírgula, ex.: `BR` ou `FI,SE,GB`. |
| `types` | query | `string` | não | Filtra por `type` do conector. Aceita lista separada por vírgula do enum de tipos. |
| `sandbox` | query | `boolean` | não | Em aplicação de produção, `true` inclui conectores sandbox. Aplicações SANDBOX enxergam somente conectores `isSandbox: true`. Padrão: `false`. |
| `isOpenFinance` | query | `boolean` | não | `true` retorna conectores regulados de Open Finance/Open Banking; não infira esse valor pela faixa do id. |
| `products` | query | `string` | não | Retorna apenas conectores que suportam TODOS os produtos listados. Lista separada por vírgula do enum de produtos. |
| `supportsPaymentInitiation` | query | `boolean` | não | Aceito por compatibilidade de wire. Na Malvo, `true` sempre resulta em conjunto vazio (sem iniciação de pagamentos). |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/connectors" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado de conectores.

```json
{
  "total": 1,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": 612,
      "name": "Nubank",
      "institutionUrl": "https://nubank.com.br",
      "imageUrl": "https://malvo.io/connectors/nubank.svg",
      "primaryColor": "820AD1",
      "country": "BR",
      "type": "PERSONAL_BANK",
      "credentials": [
        {
          "label": "CPF",
          "name": "cpf",
          "type": "number",
          "placeholder": "999.999.999-99",
          "validation": "^\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2}$",
          "validationMessage": "CPF deve ter 11 dígitos",
          "optional": false
        }
      ],
      "products": [
        "ACCOUNTS",
        "CREDIT_CARDS",
        "TRANSACTIONS",
        "INVESTMENTS",
        "IDENTITY"
      ],
      "isOpenFinance": true,
      "isSandbox": false,
      "oauth": true,
      "oauthUrl": null,
      "hasMFA": false,
      "supportsPaymentInitiation": false,
      "health": {
        "status": "ONLINE",
        "stage": null
      },
      "createdAt": "2024-06-01T00:00:00.000Z",
      "updatedAt": "2025-01-01T00:00:00.000Z"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente, inválido ou expirado. | `CLIENT_KEYS_UNAUTHORIZED` |
| `429` | Limite de requisições por IP/minuto excedido. | `TOO_MANY_REQUESTS` |
| `500` | Falha interna do servidor — repetir com backoff. | `INTERNAL_SERVER_ERROR` |

## GET /connectors/{id} — Consulta um conector pelo id

Retorna um único conector pelo seu id inteiro. Conectores sandbox não são visíveis sem o opt-in de sandbox.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `integer` | sim | Id inteiro do conector. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/connectors/612" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Conector encontrado.

```json
{
  "id": 612,
  "name": "Nubank",
  "institutionUrl": "https://nubank.com.br",
  "imageUrl": "https://malvo.io/connectors/nubank.svg",
  "primaryColor": "820AD1",
  "country": "BR",
  "type": "PERSONAL_BANK",
  "credentials": [
    {
      "label": "CPF",
      "name": "cpf",
      "type": "number",
      "placeholder": "999.999.999-99",
      "validation": "^\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2}$",
      "validationMessage": "CPF deve ter 11 dígitos",
      "optional": false
    }
  ],
  "products": [
    "ACCOUNTS",
    "CREDIT_CARDS",
    "TRANSACTIONS",
    "INVESTMENTS",
    "IDENTITY"
  ],
  "isOpenFinance": true,
  "isSandbox": false,
  "oauth": true,
  "oauthUrl": null,
  "hasMFA": false,
  "supportsPaymentInitiation": false,
  "health": {
    "status": "ONLINE",
    "stage": null
  },
  "createdAt": "2024-06-01T00:00:00.000Z",
  "updatedAt": "2025-01-01T00:00:00.000Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente, inválido ou expirado. | `CLIENT_KEYS_UNAUTHORIZED` |
| `404` | Conector desconhecido ou visível apenas em sandbox. |  |

## GET /consents — Lista consentimentos de um item

Retorna o envelope paginado de consentimentos vinculados ao `itemId` informado.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemId` | query | `string (uuid)` | sim | Id (UUID) do item dono dos consentimentos. Obrigatório. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/consents?itemId=a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado de consentimentos.

```json
{
  "total": 1,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": "c1d2e3f4-0000-4abc-9def-111213141516",
      "itemId": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
      "status": "AUTHORISED",
      "products": [
        "ACCOUNTS",
        "TRANSACTIONS"
      ],
      "openFinancePermissionsGranted": [
        "ACCOUNTS",
        "BALANCES",
        "TRANSACTIONS"
      ],
      "createdAt": "2025-01-01T00:00:00.000Z",
      "updatedAt": "2025-01-01T00:05:00.000Z",
      "expiresAt": "2025-06-30T00:00:00.000Z",
      "revokedAt": null
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente, inválido ou expirado. | `CLIENT_KEYS_UNAUTHORIZED` |
| `500` | Falha interna do servidor — repetir com backoff. | `INTERNAL_SERVER_ERROR` |

## GET /consents/{id} — Consulta um consentimento pelo id

Retorna um único consentimento pelo seu id (UUID).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Id (UUID) do consentimento. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/consents/c1d2e3f4-0000-4abc-9def-111213141516" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Consentimento encontrado.

```json
{
  "id": "c1d2e3f4-0000-4abc-9def-111213141516",
  "itemId": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "status": "AUTHORISED",
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS",
    "INVESTMENTS"
  ],
  "openFinancePermissionsGranted": [
    "ACCOUNTS_READ",
    "ACCOUNTS_BALANCES_READ",
    "RESOURCES_READ"
  ],
  "createdAt": "2025-01-01T00:00:00.000Z",
  "updatedAt": "2025-01-01T00:05:00.000Z",
  "expiresAt": null,
  "revokedAt": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente, inválido ou expirado. | `CLIENT_KEYS_UNAUTHORIZED` |
| `404` | Consentimento desconhecido. |  |
