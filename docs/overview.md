# Malvo API: visão geral

A Malvo é uma camada de dados de Open Finance Brasil e Open Banking AIS (Europa e Reino Unido). A API agrega e categoriza dados de contas, cartões e faturas, transações, investimentos, empréstimos e identidade. A Malvo faz **apenas agregação de dados**: não há iniciação de pagamentos (ITP), Pix nem boletos.

A referência de cada endpoint, com exemplos em `curl` e respostas JSON, está em [`endpoints/`](endpoints). A documentação completa fica em https://docs.malvo.io.

## Base URL

Toda a API vive sob um único host: `https://api.malvo.io`. Não existem subdomínios de API.

## Autenticação

| Credencial | Onde fica | Header | Validade | Uso |
|---|---|---|---|---|
| `clientId` / `clientSecret` | Apenas no servidor | — | até a rotação | Trocar por `apiKey` em `POST /auth` |
| `apiKey` | Servidor | `X-API-KEY` | 2 horas | Acesso server-side a items, dados de produto, webhooks e conectores |
| `connectToken` | Entregue ao browser | usado pelo Connect Widget | 30 minutos | Só dirigir o Connect Widget e ler o próprio item |

1. No servidor, chame `POST /auth` com `clientId` e `clientSecret`. A resposta traz uma `apiKey` válida por 2 horas.
2. Envie a `apiKey` no header `X-API-KEY` em todas as outras chamadas.
3. A `apiKey` é stateless; emitir uma nova não invalida as anteriores. Guarde-a em cache no servidor e renove por volta de 1h50 ou no primeiro `401`.
4. Em `POST /connect_token`, a `apiKey` ausente, malformada ou expirada retorna `403`, não `401`: renove a `apiKey` e repita.

```bash
curl -X POST "https://api.malvo.io/auth" \
  -H "Content-Type: application/json" \
  -d '{"clientId": "<CLIENT_ID>", "clientSecret": "<CLIENT_SECRET>"}'
```

### Front-end e apps móveis

`clientId`, `clientSecret` e `apiKey` nunca podem chegar ao browser ou a apps móveis. Gere no servidor um `connectToken` com `POST /connect_token` e entregue só ele ao Connect Widget. Com um `connectToken`, a leitura de dados de produto (contas, transações, cartões) retorna `403`.

O `onSuccess` do Connect Widget é best-effort: o usuário pode fechar a aba antes do callback. Os webhooks são a fonte da verdade do estado do Item.

## Conectores

O catálogo de conectores é dinâmico. Não fixe IDs de conectores no código: consulte `GET /connectors` em tempo de execução e filtre por `isOpenFinance`, `countries`, `types` e `products`.

## Consentimento

Ofereça ao usuário uma ação "Desconectar banco / Revogar consentimento", disponível a qualquer momento, que chame `DELETE /items/{id}`.

## Paginação

| Tipo | Onde | Fim da iteração |
|---|---|---|
| Por página | Maioria das listas (`/connectors`, `/accounts/{id}/statements`, `/bills`, `/investments`, `/categories`, `/webhooks`) | `page >= totalPages` |
| Por cursor | Só `GET /v2/transactions` | `next` é `null` |

- Por página: parâmetros `page` (base 1, padrão `1`) e `pageSize`; a resposta traz `page`, `total`, `totalPages` e `results`.
- Por cursor: a resposta traz `results` e `next`; siga `next` até ele ser `null`.
- Use `GET /v2/transactions` em integrações novas; `GET /transactions` está depreciado.

## Erros

Todos os erros usam o envelope `GlobalErrorResponse`:

```json
{
  "code": 429,
  "message": "Too many requests. Please try again later (see Retry-After header in seconds)",
  "codeDescription": "TOO_MANY_REQUESTS"
}
```

Trate erros pelo `codeDescription`, que é estável. O texto de `message` não é estável: nunca faça parse dele.

## Rate limit

- Respostas `429` trazem os headers `RateLimit-Limit`, `RateLimit-Reset` (segundos até o contador zerar) e `Retry-After`.
- No `429`, aguarde `RateLimit-Reset` (ou `Retry-After`) e repita. No `429` e no `500`, use backoff exponencial com jitter.
- `PATCH /items/{id}` tem o menor limite da API: 20 requisições por minuto por IP.

## Webhooks

Toda entrega inclui o header `Malvo-Signature`:

```http
Malvo-Signature: t=<unix>,v1=<hex>
```

- A assinatura é HMAC-SHA256 de `{t}.{corpo HTTP cru}`, em hex minúsculo, com o signing secret da aplicação. Use os bytes exatos do POST, nunca `JSON.parse` seguido de `JSON.stringify`.
- Compare em tempo constante e aceite qualquer `v1` do header (durante uma rotação podem vir dois).
- A janela de replay padrão é de 5 minutos.
- Verifique a assinatura antes de aplicar qualquer efeito e deduplique por `eventId`: o mesmo `eventId` é reusado em todas as reentregas de um evento.
- O SDK `@malvo/server` oferece `verifyWebhookSignature(body, header, secrets)`.
- Padrão recomendado: o webhook é o gatilho e a API REST é a fonte da verdade.
