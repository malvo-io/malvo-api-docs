# Malvo — Items

> Gerado a partir de `openapi/items.json` por `scripts/generate_reference.py`. Não edite à mão.

API de Items da Malvo. Um Item representa uma conexão entre um usuário e um Connector, mantém o vínculo com os consentimentos e é o ponto de entrada para todos os dados de produtos (contas, cartões, transações, investimentos, identidade). Contrato público estável, sem iniciação de pagamento. Autenticação por header `X-API-KEY`.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `GET /auto-sync/defaults` — Consultar padrão de sincronização da aplicação
- `PATCH /auto-sync/defaults` — Configurar padrão de sincronização da aplicação
- `GET /items/{id}/auto-sync` — Consultar sincronização automática do item
- `PATCH /items/{id}/auto-sync` — Configurar sincronização automática do item
- `POST /items` — Criar item
- `GET /items/{id}` — Consultar item
- `PATCH /items/{id}` — Atualizar item / renovar autorização
- `DELETE /items/{id}` — Deletar item / revogar consentimento
- `PATCH /items/{id}/disable-auto-sync` — Desativar auto-sync do item
- `POST /items/{id}/refresh` — Refresh simples do item
- `POST /items/{id}/mfa` — Enviar token MFA

## GET /auto-sync/defaults — Consultar padrão de sincronização da aplicação

Exige API key da aplicação. Tokens do Connect Widget não são aceitos. Veja o guia de configuração de sincronização automática.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/auto-sync/defaults" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Configuração de sincronização automática.

```json
{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 1
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `403` | API key inválida ou acesso à produção bloqueado. |  |
| `404` | Aplicação ou item não encontrado no escopo da API key. |  |

## PATCH /auto-sync/defaults — Configurar padrão de sincronização da aplicação

Exige API key da aplicação. Tokens do Connect Widget não são aceitos. Veja o guia de configuração de sincronização automática. Define o padrão dos próximos itens, criados pela API ou pelo Connect Widget. Por padrão, aplica também aos itens existentes, em uma única transação. Não altera outras aplicações.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `autoSyncEnabled` | `boolean` | não |  |
| `autoSyncFrequency` | `integer` | não | Valores: `1`, `2`, `3`. |
| `applyToExistingItems` | `boolean` | não | Atualiza todos os itens existentes da aplicação junto com o padrão. Envie false para afetar apenas os próximos itens. Padrão: `true`. |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/auto-sync/defaults" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 3
}'
```

### Resposta 200

Configuração de sincronização automática.

```json
{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 1,
  "applied": 0
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `403` | API key inválida ou acesso à produção bloqueado. |  |
| `404` | Aplicação ou item não encontrado no escopo da API key. |  |
| `400` | Corpo inválido, campos desconhecidos, ausência dos campos de configuração ou frequência diferente de 1, 2 ou 3. |  |
| `409` | CLIENT_HAS_ITEM_UPDATES_DISABLED: atualizações bloqueadas para a aplicação. |  |

## GET /items/{id}/auto-sync — Consultar sincronização automática do item

Exige API key da aplicação. Tokens do Connect Widget não são aceitos. Veja o guia de configuração de sincronização automática.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim |  |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/items/3fa85f64-5717-4562-b3fc-2c963f66afa6/auto-sync" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Configuração de sincronização automática.

```json
{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 1,
  "nextAutoSyncAt": "2026-01-15T12:00:00.000Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `403` | API key inválida ou acesso à produção bloqueado. |  |
| `404` | Aplicação ou item não encontrado no escopo da API key. |  |

## PATCH /items/{id}/auto-sync — Configurar sincronização automática do item

Exige API key da aplicação. Tokens do Connect Widget não são aceitos. Veja o guia de configuração de sincronização automática. Altera apenas o agendamento; não dispara refresh imediato. Campos omitidos preservam o valor atual. Itens sem consentimento válido aguardam autorização antes de receber o próximo horário.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim |  |

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `autoSyncEnabled` | `boolean` | não |  |
| `autoSyncFrequency` | `integer` | não | Valores: `1`, `2`, `3`. |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/items/3fa85f64-5717-4562-b3fc-2c963f66afa6/auto-sync" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 3
}'
```

### Resposta 200

Configuração de sincronização automática.

```json
{
  "autoSyncEnabled": true,
  "autoSyncFrequency": 1,
  "nextAutoSyncAt": "2026-01-15T12:00:00.000Z"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `403` | API key inválida ou acesso à produção bloqueado. |  |
| `404` | Aplicação ou item não encontrado no escopo da API key. |  |
| `400` | Corpo inválido, campos desconhecidos, ausência dos campos de configuração ou frequência diferente de 1, 2 ou 3. |  |
| `409` | CLIENT_HAS_ITEM_UPDATES_DISABLED: atualizações bloqueadas para a aplicação. |  |

## POST /items — Criar item

Cria um Item para um Connector. Envie `connectorId` e somente os campos declarados em `connector.credentials`: conectores de sandbox podem pedir user/password, enquanto Connectors Open Finance usam os identificadores ou seleções de jornada anunciados pelo catálogo. A Malvo expõe exclusivamente Connectors Open Finance nas rotas operacionais; Connectors diretos não são expostos. Para retornar à sua própria aplicação, informe `oauthRedirectUri`; sem ele, o fluxo usa a finalização hospedada. A resposta traz a URL efêmera em `connector.oauthUrl` quando houver OAuth; durante a autorização, o Item usa `status=LOGIN_IN_PROGRESS` e `executionStatus=USER_AUTHORIZATION_PENDING`.

No Brasil, a carga inicial busca até 365 dias; no Open Banking internacional busca o maior histórico permitido pelo ASPSP. Use `clientUserId` estável e `avoidDuplicates: true` para reaproveitar a conexão sem duplicar o Item.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `connectorId` | `integer` | sim | Id do connector (de `GET /connectors`). |
| `parameters` | `object` | sim | Pares exigidos por `connector.credentials`. No Brasil normalmente use CPF/CNPJ; em jornadas sem entrada prévia use `{}` salvo quando o Connector anunciar uma seleção de método. As rotas operacionais aceitam somente Connectors Open Finance, nunca credenciais de Connectors diretos. Nomes iniciados por `_` são reservados. |
| `clientUserId` | `string` | não | Identificador estável do usuário no sistema integrador. Recomendado nas rotas de compatibilidade e internacional para correlação e avoidDuplicates. |
| `webhookUrl` | `string (uri)` | não | Notificado nos eventos deste item (`item/created`, `item/updated`, `item/error`, `item/waiting_user_input`, `item/waiting_user_action`, `item/login_succeeded`, `transactions/*`). |
| `oauthRedirectUri` | `string (uri)` | não | Destino final depois do callback Malvo. Use HTTPS absoluto ou deep link de esquema seguro; a Malvo anexa itemId/status/message e, quando o redirect veio de um Connect Token, o malvoFlowId reservado. |
| `products` | `array<string>` | não | Subconjunto anunciado por connector.products. Os conectores podem oferecer ACCOUNTS, TRANSACTIONS, CREDIT_CARDS, INVESTMENTS, INVESTMENTS_TRANSACTIONS, IDENTITY e LOANS; quando TRANSACTIONS é solicitado, a Malvo também ativa internamente PAYMENT_DATA se o Connector oferecer esse enriquecimento. O Open Banking internacional oferece ACCOUNTS e TRANSACTIONS. |
| `avoidDuplicates` | `boolean` | não | Se `true`, reutiliza uma conexão existente da mesma instituição/documento; nas rotas de compatibilidade e internacional, usa clientUserId quando ainda não existe CPF/CNPJ. |

### Exemplo de requisição

**Connector de sandbox (user/password)**

```bash
curl -X POST "https://api.malvo.io/items" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "connectorId": 0,
  "parameters": {
    "user": "user-ok",
    "password": "password-ok"
  },
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ]
}'
```

**Open Finance Brasil (cpf + oauthRedirectUri)**

```bash
curl -X POST "https://api.malvo.io/items" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "connectorId": 612,
  "parameters": {
    "cpf": "12345678901"
  },
  "oauthRedirectUri": "https://your.app/oauth/callback",
  "clientUserId": "my-user-42"
}'
```

**Open Banking internacional (sem credencial bancária)**

```bash
curl -X POST "https://api.malvo.io/items" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "connectorId": 742,
  "parameters": {},
  "oauthRedirectUri": "https://your.app/oauth/callback",
  "clientUserId": "my-user-42",
  "avoidDuplicates": true,
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ]
}'
```

### Resposta 201

Item criado. O corpo é o objeto Item completo (§4.1). Para connectors regulados aguardando OAuth, `status=LOGIN_IN_PROGRESS` e `executionStatus=USER_AUTHORIZATION_PENDING` até o usuário concluir o consentimento.

```json
{
  "id": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false,
    "oauth": true,
    "oauthUrl": "https://auth.example/authorize"
  },
  "status": "LOGIN_IN_PROGRESS",
  "executionStatus": "USER_AUTHORIZATION_PENDING",
  "createdAt": "2025-01-01T12:00:00.000Z",
  "updatedAt": "2025-01-01T12:00:00.000Z",
  "lastUpdatedAt": null,
  "nextAutoSyncAt": null,
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ],
  "consentExpiresAt": null,
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": null,
  "error": null,
  "parameter": null,
  "userAction": null,
  "oauthRedirectUri": "https://your.app/oauth/callback"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `402` | Saldo de créditos pré-pagos zerado (`CREDITS_EXHAUSTED`). Novas conexões ficam pausadas até a recarga; os dados existentes continuam acessíveis. Ativo para contas novas desde 04/10/2026 e para as existentes a partir de 01/12/2026 — veja [Créditos pré-pagos](https://docs.malvo.io/dashboard/credits). | `CREDITS_EXHAUSTED` |
| `400` | Parâmetros inválidos. O corpo traz `errors[]` com `code`, `message` e `parameter` (§2.3). |  |
| `409` | Conflito. `ITEM_IS_ALREADY_UPDATING`: outra requisição já está criando a autorização Open Finance deste item; repita a mesma requisição depois do `Retry-After` (o corpo traz o status atual do item em `data`). `ITEM_CREATION_LIMIT_EXCEEDED`: a aplicação atingiu o limite de itens; reutilize um item existente ou exclua itens sem uso. | `ITEM_IS_ALREADY_UPDATING`, `ITEM_CREATION_LIMIT_EXCEEDED` |
| `500` | Erro interno do servidor — repita com backoff. | `INTERNAL_SERVER_ERROR` |
| `501` | Connector não suportado (`CONNECTOR_NOT_SUPPORTED`). Apenas connectors de sandbox e Open Finance são suportados para criação de item. | `CONNECTOR_NOT_SUPPORTED` |
| `503` | Open Finance indisponível (`OPEN_FINANCE_NOT_AVAILABLE`). A conectividade Open Finance está temporariamente indisponível nesta aplicação/ambiente. | `OPEN_FINANCE_NOT_AVAILABLE` |

## GET /items/{id} — Consultar item

Retorna o objeto Item completo. Após criar ou atualizar, faça polling deste endpoint (ou, de preferência, consuma webhooks) até o `status` sair de `UPDATING`/`LOGIN_IN_PROGRESS` — `LOGIN_IN_PROGRESS` pode levar até 5 minutos. Items deletados ou desconhecidos retornam `404` (`ITEM_NOT_FOUND`).

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Exemplo de requisição

```bash
curl -X GET "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Objeto Item completo (§4.1).

```json
{
  "id": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false
  },
  "status": "UPDATED",
  "executionStatus": "SUCCESS",
  "createdAt": "2025-01-01T12:00:00.000Z",
  "updatedAt": "2025-01-02T08:00:00.000Z",
  "lastUpdatedAt": "2025-01-02T08:00:00.000Z",
  "nextAutoSyncAt": "2025-01-03T08:00:00.000Z",
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "CREDIT_CARDS",
    "TRANSACTIONS"
  ],
  "consentExpiresAt": null,
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": {
    "accounts": {
      "isUpdated": true,
      "lastUpdatedAt": "2025-01-02T08:00:00.000Z",
      "warnings": []
    },
    "creditCards": {
      "isUpdated": true,
      "lastUpdatedAt": "2025-01-02T08:00:00.000Z",
      "warnings": []
    },
    "transactions": {
      "isUpdated": false,
      "lastUpdatedAt": "2025-01-01T08:00:00.000Z",
      "warnings": [
        {
          "code": "423",
          "message": "Open Finance monthly rate limit reached for transactions",
          "providerMessage": null
        }
      ]
    },
    "investments": null,
    "identity": null,
    "paymentData": null
  },
  "error": null,
  "parameter": null,
  "userAction": null,
  "oauthRedirectUri": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Item desconhecido ou deletado. | `ITEM_NOT_FOUND` |

## PATCH /items/{id} — Atualizar item / renovar autorização

Dispara uma atualização do item. Todos os campos são opcionais; um corpo `{}` dispara um re-sync simples. Use `parameters` para enviar os identificadores ou seleções anunciados em `connector.credentials` e/ou valores de MFA, `products` para ajustar o conjunto de produtos coletados daqui em diante, `webhookUrl` para alterar o destino de webhook e `clientUserId` para atualizar o vínculo. Quando a atualização inicia um novo consentimento, a resposta inclui a URL efêmera em `connector.oauthUrl`.

Um item Open Finance saudável reaproveita o consentimento vigente: a atualização vira um re-sync simples e a resposta **não** traz `connector.oauthUrl`. Para um botão de "reconectar" acionado pelo usuário, envie `reconsent: true` — assim um novo consentimento é emitido mesmo quando o item ainda parece ativo aqui, o que cobre o consentimento derrubado no banco que ainda não foi observado.

**Rate limit: 20 requisições/min por IP — o limite mais baixo da API.** Este endpoint é apenas para atualizações **disparadas pelo usuário**; fluxos de atualização em massa/lote não são permitidos e são limitados (`ITEM_CREATION_LIMIT_EXCEEDED`). Atualizações periódicas devem usar o auto-sync. Se o banco exigir autenticação nova ou MFA, o item transiciona para `WAITING_USER_INPUT` até o usuário responder.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `parameters` | `object` | não | Identificadores ou seleções anunciados em `connector.credentials` e/ou valores de MFA. Na primeira adoção de um snapshot importado, CPF/CNPJ omitido pode ser recuperado das contas quando houver um único documento compatível; casos ambíguos continuam exigindo o campo explícito. |
| `webhookUrl` | `string (uri)` | não | Atualiza o destino de webhook do item. |
| `oauthRedirectUri` | `string (uri)` | não | Atualiza o destino final do OAuth. HTTPS ou deep link seguro. |
| `connectorId` | `integer` | não | Conector Open Finance para adoção/reconexão de snapshot importado; não use para trocar uma conexão nativa de banco. |
| `reconsent` | `boolean` | não | Força um novo consentimento Open Finance mesmo que o item ainda pareça saudável, retornando uma nova `connector.oauthUrl`. Use quando o usuário final pedir para reconectar: um consentimento derrubado no banco pode continuar lendo como ativo aqui até a releitura no detentor confirmar o contrário, e sem esta flag o PATCH degrada para um re-sync simples e responde sem URL de autorização. Ignorado em conectores sandbox/diretos, que não emitem consentimento. |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "parameters": {
    "cpf": "12345678901"
  },
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ]
}'
```

### Resposta 200

Item agora em `UPDATING` ou, quando um novo consentimento foi iniciado, em `LOGIN_IN_PROGRESS` com a URL efêmera em `connector.oauthUrl`. O corpo é o objeto Item completo (§4.1).

```json
{
  "id": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false
  },
  "status": "UPDATING",
  "executionStatus": "CREATED",
  "createdAt": "2025-01-01T12:00:00.000Z",
  "updatedAt": "2025-01-02T09:00:00.000Z",
  "lastUpdatedAt": "2025-01-02T08:00:00.000Z",
  "nextAutoSyncAt": "2025-01-03T08:00:00.000Z",
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ],
  "consentExpiresAt": null,
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": null,
  "error": null,
  "parameter": null,
  "userAction": null,
  "oauthRedirectUri": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Validação (`errors[]`) ou `ITEM_ORIGINAL_CONNECTED_WITH_DIFFERENT_ACCOUNT` (usuário deve reconectar com a conta original). |  |
| `404` | Item desconhecido ou deletado. | `ITEM_NOT_FOUND` |
| `409` | Conflito. `ITEM_IS_ALREADY_UPDATING`: outra requisição já está atualizando a conexão Open Finance deste item; repita a mesma requisição depois do `Retry-After`, sem criar item novo nem pedir reconexão. O corpo traz `data.status`, `data.executionStatus`, `data.lastUpdatedAt` e `data.retryAfterSeconds`; os webhooks `item/updated` e `item/error` avisam quando a atualização termina. `CLIENT_HAS_ITEM_UPDATES_DISABLED`: atualizações bloqueadas para a aplicação; repetir não resolve, fale com o suporte. | `ITEM_IS_ALREADY_UPDATING`, `CLIENT_HAS_ITEM_UPDATES_DISABLED` |
| `429` | Limite de 20 requisições/min por IP excedido (veja o header `Retry-After` em segundos). | `TOO_MANY_REQUESTS` |

## DELETE /items/{id} — Deletar item / revogar consentimento

Remove o item e revoga o consentimento Open Finance correspondente. Após a deleção, `GET /items/{id}` retorna `404` e **todos os dados vinculados (contas, transações, etc.) tornam-se permanentemente inacessíveis pela API**.

**LGPD / Open Finance (obrigatório):** integradores devem sempre expor uma ação "Desconectar banco / Revogar consentimento" que chama este endpoint, sempre disponível ao usuário, para conformidade com a regulação de Open Banking. O usuário ainda pode revogar o registro de consentimento separadamente do lado do banco.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Exemplo de requisição

```bash
curl -X DELETE "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 204

Item deletado com sucesso. Sem conteúdo.

Sem corpo de resposta.

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Item desconhecido ou já deletado. | `ITEM_NOT_FOUND` |

## PATCH /items/{id}/disable-auto-sync — Desativar auto-sync do item

Desativa as atualizações automáticas deste Item. O Item e os dados já persistidos permanecem disponíveis; `nextAutoSyncAt` passa a `null`. Atualizações manuais continuam disponíveis.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Exemplo de requisição

```bash
curl -X PATCH "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a/disable-auto-sync" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Auto-sync desativado. Retorna o Item atualizado com `nextAutoSyncAt=null`.

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false
  },
  "status": "CREATING",
  "executionStatus": "CREATED",
  "createdAt": "2026-01-15T12:00:00.000Z",
  "updatedAt": "2026-01-15T12:00:00.000Z",
  "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
  "nextAutoSyncAt": "2026-01-15T12:00:00.000Z",
  "clientUserId": "string",
  "webhookUrl": "https://your.app/callback",
  "products": [
    "string"
  ],
  "consentExpiresAt": "2026-01-15T12:00:00.000Z",
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": {
    "accounts": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "creditCards": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "transactions": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "investments": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "identity": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "paymentData": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "loans": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    },
    "investmentsTransactions": {
      "isUpdated": true,
      "lastUpdatedAt": "2026-01-15T12:00:00.000Z",
      "warnings": [
        {
          "code": "string",
          "message": "string",
          "providerMessage": "string"
        }
      ]
    }
  },
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "The provided credentials are incorrect",
    "providerMessage": "Senha inválida. Você tem mais 2 tentativas.",
    "attributes": {
      "remainingAttempts": "2"
    }
  },
  "parameter": {},
  "userAction": {
    "instructions": "string",
    "attributes": {},
    "expiresAt": "2026-01-15T12:00:00.000Z"
  },
  "oauthRedirectUri": "string"
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `404` | Item desconhecido ou deletado. | `ITEM_NOT_FOUND` |
| `502` | O Open Finance não confirmou a desativação; tente novamente com backoff. | `ITEM_NOT_FOUND` |

## POST /items/{id}/refresh — Refresh simples do item

Dispara um re-sync sem alterar credenciais. Corpo vazio. No Open Finance brasileiro, a execução sempre avalia a janela corrente de transações (aproximadamente os últimos 7 dias) e consulta o provedor imediatamente enquanto houver capacidade no balde diário daquela rota e recurso. Não existe intervalo entre as chamadas permitidas: em uma capacidade de 10 chamadas/dia, as chamadas 1 a 10 podem ser consecutivas e somente a 11ª fica bloqueada até a virada do dia brasileiro. O contador independe da configuração de auto-sync, embora auto-sync e refresh manual compartilhem a capacidade efetivamente consumida no Open Finance. A cota mensal absoluta e o cooldown da instituição continuam valendo; quando o balde diário está esgotado, mantém o último valor coletado. Não responde `409` por sincronização em andamento: chamadas repetidas se juntam numa única execução; o `409` aqui é só `ITEM_NEEDS_RECONSENT` ou `CLIENT_HAS_ITEM_UPDATES_DISABLED`. Prefira este endpoint (ou `PATCH`) a criar um item novo — items novos consomem cota da rede Open Finance.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Corpo da requisição

Schema: `object`. Veja o exemplo na requisição.

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a/refresh" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Resposta 200

Item agora em `UPDATING`. O corpo é o objeto Item completo (§4.1).

```json
{
  "id": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false
  },
  "status": "UPDATING",
  "executionStatus": "CREATED",
  "createdAt": "2025-01-01T12:00:00.000Z",
  "updatedAt": "2025-01-02T09:30:00.000Z",
  "lastUpdatedAt": "2025-01-02T08:00:00.000Z",
  "nextAutoSyncAt": "2025-01-03T08:00:00.000Z",
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "CREDIT_CARDS",
    "TRANSACTIONS"
  ],
  "consentExpiresAt": null,
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": null,
  "error": null,
  "parameter": null,
  "userAction": null,
  "oauthRedirectUri": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `409` | Conflito. O refresh nunca responde 409 por sincronização em andamento: chamadas repetidas se juntam numa única execução. `ITEM_NEEDS_RECONSENT`: o consentimento não está autorizado; reconecte com `PATCH /items/{id}` e `{"reconsent": true}`. `CLIENT_HAS_ITEM_UPDATES_DISABLED`: atualizações bloqueadas para a aplicação; fale com o suporte. | `ITEM_NEEDS_RECONSENT`, `CLIENT_HAS_ITEM_UPDATES_DISABLED` |

## POST /items/{id}/mfa — Enviar token MFA

Envia um token de MFA de dois fatores. Usado quando `status = WAITING_USER_INPUT` / `executionStatus = WAITING_USER_INPUT`; o campo `parameter` do item descreve a entrada esperada. Em sucesso, a execução retoma (`LOGIN_MFA_IN_PROGRESS`). Token errado/expirado leva ao `executionStatus` final `INVALID_CREDENTIALS_MFA`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `id` | path | `string (uuid)` | sim | Identificador (UUID) do item. |

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `parameters` | `object` | sim | Mapa de parâmetros de MFA preenchidos pelo usuário. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/items/a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a/mfa" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "parameters": {
    "token": "123456"
  }
}'
```

### Resposta 200

Execução retomada (`LOGIN_MFA_IN_PROGRESS`). O corpo é o objeto Item completo (§4.1).

```json
{
  "id": "a8f4f3e1-7b2c-4d4e-8f9a-0b1c2d3e4f5a",
  "connector": {
    "id": 612,
    "name": "Nubank",
    "type": "PERSONAL_BANK",
    "imageUrl": "https://malvo.io/connectors/nubank.svg",
    "primaryColor": "820AD1",
    "isOpenFinance": true,
    "isSandbox": false
  },
  "status": "UPDATING",
  "executionStatus": "LOGIN_MFA_IN_PROGRESS",
  "createdAt": "2025-01-01T12:00:00.000Z",
  "updatedAt": "2025-01-01T12:01:30.000Z",
  "lastUpdatedAt": null,
  "nextAutoSyncAt": null,
  "clientUserId": "my-user-42",
  "webhookUrl": "https://your.app/webhooks/malvo",
  "products": [
    "ACCOUNTS",
    "TRANSACTIONS"
  ],
  "consentExpiresAt": null,
  "consecutiveFailedLoginAttempts": 0,
  "statusDetail": null,
  "error": null,
  "parameter": null,
  "userAction": null,
  "oauthRedirectUri": null
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | O item não está aguardando entrada do usuário. |  |
| `404` | Item desconhecido. | `ITEM_NOT_FOUND` |
