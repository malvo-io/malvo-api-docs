# Malvo — Webhooks Management API

> Gerado a partir de `openapi/webhooks.json` por `scripts/generate_reference.py`. Não edite à mão.

Endpoints de gerenciamento (CRUD) de webhooks da Malvo. Registre, liste, atualize e remova webhooks que recebem notificações de eventos de itens, transações e conectores.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `POST /webhooks` — Criar webhook
- `GET /webhooks` — Listar webhooks
- `GET /webhooks/{id}` — Recuperar webhook
- `PATCH /webhooks/{id}` — Atualizar webhook
- `DELETE /webhooks/{id}` — Remover webhook

## POST /webhooks — Criar webhook

Registra um novo webhook na sua aplicação. A `url` deve usar `https://` e não pode ser `localhost`/host privado. O `event` deve ser um valor válido do enum (`all` cobre todos os eventos disparados). O campo `headers` é write-only: aceito aqui, mas nunca retornado.

**Dica:** prefira `event: "all"` com um único endpoint e roteie internamente, evitando o limite de 5 webhooks por tipo de evento.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `url` | `string (uri)` | sim | URL de destino. Deve ser `https://` e não pode ser `localhost`/host privado. |
| `event` | `WebhookEvent` | sim | Tipo de evento a assinar. Aceita qualquer valor do enum. |
| `headers` | `object` | não | **Write-only / API-only.** Mapa nome→valor de headers enviados verbatim em cada entrega. Nunca é retornado em respostas nem visível/editável no Dashboard. Use para autenticação das entregas (ex.: `Authorization: Bearer ...`). |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/webhooks" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "url": "https://api.your-app.com/webhooks/malvo",
  "event": "all",
  "headers": {
    "Authorization": "Bearer <your-shared-secret>",
    "X-CLIENT-ID": "<secret>"
  }
}'
```

### Resposta 201

Webhook criado. O corpo é o objeto Webhook (sem `headers`).

```json
{
  "id": "39e1d11f-3c12-44a8-a788-75c5747e1a8e",
  "event": "all",
  "url": "https://api.your-app.com/webhooks/malvo",
  "createdAt": "2026-06-10T12:00:00.000Z",
  "updatedAt": "2026-06-10T12:00:00.000Z",
  "disabled": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | URL inválida (`http://`/`localhost`/host privado), valor de `event` desconhecido, corpo malformado, ou limite atingido (`Webhook limit reached` — já existem 5 webhooks para esse tipo de evento). | `VALIDATION_ERROR` |
| `401` | `X-API-KEY` ausente ou expirado (TTL de 2h). Regenere a apiKey via `POST /auth`. | `UNAUTHORIZED` |
| `429` | Limite de taxa excedido. Aplique backoff exponencial com jitter e respeite o header `Retry-After`. | `RATE_LIMIT_EXCEEDED` |
| `500` | Erro transitório do lado da plataforma. Tente novamente com backoff; se persistir, consulte a status page. | `INTERNAL_ERROR` |

## GET /webhooks — Listar webhooks

Lista todos os webhooks da sua aplicação no envelope paginado padrão da Malvo. O campo `headers` é omitido de todos os resultados (write-only).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/webhooks" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Envelope paginado com os webhooks da aplicação.

```json
{
  "total": 2,
  "totalPages": 1,
  "page": 1,
  "results": [
    {
      "id": "39e1d11f-3c12-44a8-a788-75c5747e1a8e",
      "event": "all",
      "url": "https://api.your-app.com/webhooks/malvo",
      "createdAt": "2026-06-10T12:00:00.000Z",
      "updatedAt": "2026-06-10T12:00:00.000Z",
      "disabled": null
    },
    {
      "id": "7d2a02c1-9c1b-43c5-b144-1bb39b0e8f3c",
      "event": "item/error",
      "url": "https://api.your-app.com/webhooks/malvo-errors",
      "createdAt": "2026-06-01T09:30:00.000Z",
      "updatedAt": "2026-06-01T09:30:00.000Z",
      "disabled": null
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente ou expirado (TTL de 2h). Regenere a apiKey via `POST /auth`. | `UNAUTHORIZED` |
| `429` | Limite de taxa excedido. Aplique backoff exponencial com jitter e respeite o header `Retry-After`. | `RATE_LIMIT_EXCEEDED` |
| `500` | Erro transitório do lado da plataforma. Tente novamente com backoff; se persistir, consulte a status page. | `INTERNAL_ERROR` |

## GET /webhooks/{id} — Recuperar webhook

Recupera um único webhook pelo `id`. O campo `headers` nunca é retornado. Retorna `404` se o id não existir ou pertencer a outra aplicação.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do webhook. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/webhooks/39e1d11f-3c12-44a8-a788-75c5747e1a8e" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Webhook (sem `headers`).

```json
{
  "id": "39e1d11f-3c12-44a8-a788-75c5747e1a8e",
  "event": "all",
  "url": "https://api.your-app.com/webhooks/malvo",
  "createdAt": "2026-06-10T12:00:00.000Z",
  "updatedAt": "2026-06-10T12:00:00.000Z",
  "disabled": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente ou expirado (TTL de 2h). Regenere a apiKey via `POST /auth`. | `UNAUTHORIZED` |
| `404` | Webhook não encontrado, ou pertence a outra aplicação. | `NOT_FOUND` |
| `429` | Limite de taxa excedido. Aplique backoff exponencial com jitter e respeite o header `Retry-After`. | `RATE_LIMIT_EXCEEDED` |
| `500` | Erro transitório do lado da plataforma. Tente novamente com backoff; se persistir, consulte a status page. | `INTERNAL_ERROR` |

## PATCH /webhooks/{id} — Atualizar webhook

Atualiza parcialmente um webhook. Apenas os campos enviados são alterados. Campos atualizáveis: `url`, `event`, `headers`, `disabled`.

**Rotação de segredos:** como `headers` não pode ser editado no Dashboard por design, este endpoint é o mecanismo para rotacionar os segredos de autenticação das entregas. Para reativar um webhook desabilitado, envie `"disabled": null`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do webhook. |

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `url` | `string (uri)` | não | Nova URL de destino (HTTPS, não-localhost). |
| `event` | `WebhookEvent` | não | Novo tipo de evento assinado. |
| `headers` | `object` | não | **Write-only / API-only.** Substitui os headers customizados de entrega. Mecanismo para rotacionar segredos de autenticação. Nunca é retornado. |
| `disabled` | `string \| null (date-time)` | não | Defina um timestamp ISO 8601 para desabilitar o webhook, ou `null` para reativá-lo. |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/webhooks/39e1d11f-3c12-44a8-a788-75c5747e1a8e" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "headers": {
    "Authorization": "Bearer <rotated-secret>"
  }
}'
```

### Resposta 200

Objeto Webhook atualizado (sem `headers`).

```json
{
  "id": "39e1d11f-3c12-44a8-a788-75c5747e1a8e",
  "event": "all",
  "url": "https://api.your-app.com/webhooks/malvo",
  "createdAt": "2026-06-10T12:00:00.000Z",
  "updatedAt": "2026-06-12T08:15:00.000Z",
  "disabled": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | URL inválida (`http://`/`localhost`/host privado), valor de `event` desconhecido, ou corpo malformado. | `VALIDATION_ERROR` |
| `401` | `X-API-KEY` ausente ou expirado (TTL de 2h). Regenere a apiKey via `POST /auth`. | `UNAUTHORIZED` |
| `404` | Webhook não encontrado, ou pertence a outra aplicação. | `NOT_FOUND` |
| `429` | Limite de taxa excedido. Aplique backoff exponencial com jitter e respeite o header `Retry-After`. | `RATE_LIMIT_EXCEEDED` |
| `500` | Erro transitório do lado da plataforma. Tente novamente com backoff; se persistir, consulte a status page. | `INTERNAL_ERROR` |

## DELETE /webhooks/{id} — Remover webhook

Remove permanentemente um webhook. Retorna `200` com corpo vazio (`{}`). Retorna `404` se o webhook não for encontrado.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do webhook. |

### Exemplo de requisição

```bash
curl -X DELETE "https://api.malvo.io/webhooks/39e1d11f-3c12-44a8-a788-75c5747e1a8e" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Webhook removido. Corpo vazio.

```json
{}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `401` | `X-API-KEY` ausente ou expirado (TTL de 2h). Regenere a apiKey via `POST /auth`. | `UNAUTHORIZED` |
| `404` | Webhook não encontrado, ou pertence a outra aplicação. | `NOT_FOUND` |
| `429` | Limite de taxa excedido. Aplique backoff exponencial com jitter e respeite o header `Retry-After`. | `RATE_LIMIT_EXCEEDED` |
| `500` | Erro transitório do lado da plataforma. Tente novamente com backoff; se persistir, consulte a status page. | `INTERNAL_ERROR` |
