# Malvo — Inteligência & Enriquecimento

> Gerado a partir de `openapi/intelligence.json` por `scripts/generate_reference.py`. Não edite à mão.

APIs de Inteligência e Enriquecimento da Malvo, servidas no host único `https://api.malvo.io` e com contrato wire estável. Autenticação por header `X-API-KEY` em todas as operações. Estas APIs entregam KPIs agregados por item (Item Insights), enriquecimento/categorização de transações próprias do cliente (Enrich) e detecção de pagamentos recorrentes (assinaturas, salários, contas). Não há iniciação de pagamento (sem ITP). Prosa em pt-BR; nomes de campos e enums em inglês, conforme a especificação.

- Base URL: `https://api.malvo.io`
- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.
- Formato: JSON (`Content-Type: application/json`).
- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).

## Operações

- `POST /book` — Gerar Item Insights
- `POST /categorization` — Categorizar e enriquecer transações
- `POST /recurring-payments` — Detectar pagamentos recorrentes

## POST /book — Gerar Item Insights

Retorna KPIs agregados e pré-computados por item e por classe de conta. Computa fluxo de caixa (débitos vs. créditos), distribuições de contagem de transações por faixa de data-do-mês (`1-5`, `6-10`, `11-15`, `16-20`, `21-25`, `26-31`) e por faixa de valor (`0-50`, `50-100`, … até `50000-MAX`), razão crédito/débito (`creditDebitRatio`), média/mínimo/máximo de valor, breakdown por categoria e breakdown por subtipo de conta (`SAVINGS_ACCOUNT` vs. `CHECKING_ACCOUNT`). Os KPIs são entregues nas janelas temporais `M1`, `M3`, `M12` e `allTime`. O parâmetro `itemIds` aceita um ou mais ids de item (CSV); a resposta agrupa os insights por item e por classe de conta (`bankAccount`, `creditCard`). Recomputado quando o item é re-sincronizado — chame novamente após uma sincronização.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Parâmetros

| Nome | Onde | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| `itemIds` | query | `string` | sim | Lista de ids de item separados por vírgula (1 ou mais). Ex.: `a0922d6f-2007-4169-a181-b961500608db,207f5bcd-312a-439c-abbe-166b6632c980`. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/book?itemIds=a0922d6f-2007-4169-a181-b961500608db" \
  -H "X-API-KEY: $MALVO_API_KEY"
```

### Resposta 200

Array de insights agregados, um objeto `ItemInsights` por `itemId` solicitado.

```json
[
  {
    "itemId": "a0922d6f-2007-4169-a181-b961500608db",
    "bankAccount": {
      "M1": {
        "count": 42,
        "amount": 12345.67,
        "avg": 293.94,
        "min": 1,
        "max": 1200,
        "creditDebitRatio": 0.8,
        "categories": {
          "Transfers": 5230.5,
          "Third-party transfers": 1200,
          "Credit-card fees": 89.9,
          "Uncategorized": 410.2
        },
        "byDate": {
          "1-5": 6,
          "6-10": 8,
          "11-15": 7,
          "16-20": 5,
          "21-25": 9,
          "26-31": 7
        },
        "byAmount": {
          "0-50": 12,
          "50-100": 9,
          "100-500": 14,
          "500-1000": 4,
          "1000-50000": 3,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CHECKING_ACCOUNT": 11800.47,
          "SAVINGS_ACCOUNT": 545.2
        },
        "byType": {
          "CREDIT": 6890.3,
          "DEBIT": 5455.37
        }
      },
      "M3": {
        "count": 128,
        "amount": 37210.11,
        "avg": 290.7,
        "min": 1,
        "max": 4200,
        "creditDebitRatio": 0.92,
        "categories": {
          "Transfers": 15800.1,
          "Uncategorized": 980.4
        },
        "byDate": {
          "1-5": 20,
          "6-10": 22,
          "11-15": 21,
          "16-20": 18,
          "21-25": 25,
          "26-31": 22
        },
        "byAmount": {
          "0-50": 38,
          "50-100": 27,
          "100-500": 41,
          "500-1000": 12,
          "1000-50000": 10,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CHECKING_ACCOUNT": 35100.0,
          "SAVINGS_ACCOUNT": 2110.11
        },
        "byType": {
          "CREDIT": 19200.5,
          "DEBIT": 18009.61
        }
      },
      "M12": {
        "count": 503,
        "amount": 148922.4,
        "avg": 296.07,
        "min": 1,
        "max": 12000,
        "creditDebitRatio": 0.97,
        "categories": {
          "Transfers": 62000.0,
          "Uncategorized": 3120.5
        },
        "byDate": {
          "1-5": 80,
          "6-10": 86,
          "11-15": 83,
          "16-20": 79,
          "21-25": 90,
          "26-31": 85
        },
        "byAmount": {
          "0-50": 150,
          "50-100": 110,
          "100-500": 160,
          "500-1000": 45,
          "1000-50000": 38,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CHECKING_ACCOUNT": 140000.0,
          "SAVINGS_ACCOUNT": 8922.4
        },
        "byType": {
          "CREDIT": 75500.0,
          "DEBIT": 73422.4
        }
      },
      "allTime": {
        "count": 1290,
        "amount": 402311.88,
        "avg": 311.87,
        "min": 1,
        "max": 25000,
        "creditDebitRatio": 1.01,
        "categories": {
          "Transfers": 180000.0,
          "Uncategorized": 9800.2
        },
        "byDate": {
          "1-5": 205,
          "6-10": 218,
          "11-15": 212,
          "16-20": 201,
          "21-25": 230,
          "26-31": 224
        },
        "byAmount": {
          "0-50": 380,
          "50-100": 280,
          "100-500": 410,
          "500-1000": 120,
          "1000-50000": 100,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CHECKING_ACCOUNT": 380000.0,
          "SAVINGS_ACCOUNT": 22311.88
        },
        "byType": {
          "CREDIT": 203000.0,
          "DEBIT": 199311.88
        }
      }
    },
    "creditCard": {
      "M1": {
        "count": 18,
        "amount": 4210.55,
        "avg": 233.92,
        "min": 9.9,
        "max": 980,
        "creditDebitRatio": 0.0,
        "categories": {
          "Eating out": 1200.3,
          "Video streaming": 58,
          "Uncategorized": 210.0
        },
        "byDate": {
          "1-5": 3,
          "6-10": 4,
          "11-15": 2,
          "16-20": 3,
          "21-25": 4,
          "26-31": 2
        },
        "byAmount": {
          "0-50": 8,
          "50-100": 4,
          "100-500": 5,
          "500-1000": 1,
          "1000-50000": 0,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CREDIT_CARD": 4210.55
        },
        "byType": {
          "DEBIT": 4210.55,
          "CREDIT": 0
        }
      },
      "M3": {
        "count": 51,
        "amount": 12880.0,
        "avg": 252.55,
        "min": 9.9,
        "max": 1500,
        "creditDebitRatio": 0.0,
        "categories": {
          "Eating out": 3400.0,
          "Uncategorized": 620.0
        },
        "byDate": {
          "1-5": 9,
          "6-10": 10,
          "11-15": 8,
          "16-20": 7,
          "21-25": 9,
          "26-31": 8
        },
        "byAmount": {
          "0-50": 22,
          "50-100": 12,
          "100-500": 14,
          "500-1000": 2,
          "1000-50000": 1,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CREDIT_CARD": 12880.0
        },
        "byType": {
          "DEBIT": 12880.0,
          "CREDIT": 0
        }
      },
      "M12": {
        "count": 205,
        "amount": 51200.0,
        "avg": 249.76,
        "min": 5.5,
        "max": 3200,
        "creditDebitRatio": 0.0,
        "categories": {
          "Eating out": 13800.0,
          "Uncategorized": 2400.0
        },
        "byDate": {
          "1-5": 34,
          "6-10": 36,
          "11-15": 33,
          "16-20": 32,
          "21-25": 36,
          "26-31": 34
        },
        "byAmount": {
          "0-50": 90,
          "50-100": 48,
          "100-500": 55,
          "500-1000": 8,
          "1000-50000": 4,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CREDIT_CARD": 51200.0
        },
        "byType": {
          "DEBIT": 51200.0,
          "CREDIT": 0
        }
      },
      "allTime": {
        "count": 540,
        "amount": 138900.0,
        "avg": 257.22,
        "min": 5.5,
        "max": 6800,
        "creditDebitRatio": 0.0,
        "categories": {
          "Eating out": 37000.0,
          "Uncategorized": 6100.0
        },
        "byDate": {
          "1-5": 88,
          "6-10": 92,
          "11-15": 86,
          "16-20": 84,
          "21-25": 95,
          "26-31": 95
        },
        "byAmount": {
          "0-50": 230,
          "50-100": 130,
          "100-500": 150,
          "500-1000": 20,
          "1000-50000": 10,
          "50000-MAX": 0
        },
        "bySubtype": {
          "CREDIT_CARD": 138900.0
        },
        "byType": {
          "DEBIT": 138900.0,
          "CREDIT": 0
        }
      }
    }
  }
]
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `401` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `429` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `500` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |

## POST /categorization — Categorizar e enriquecer transações

Executa transações de propriedade do cliente através do classificador (não requer item). Aceita até 5.000 transações por requisição (divida lotes maiores). Para cada transação são obrigatórios `id`, `amount`, `date` e `description`; os campos opcionais (`accountType`, `isBusinessAccount`, `paymentData`, `creditCardMcc`) melhoram materialmente a precisão. Retorna, por transação, a identificação do merchant, a `description` normalizada, a `category` e a tipagem `DEBIT`/`CREDIT`.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `transactions` | `array<EnrichTransactionInput>` | sim | Lista de transações a enriquecer. Máximo de 5.000 itens por requisição. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/categorization" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "transactions": [
    {
      "id": "tx-001",
      "amount": -89.9,
      "date": "2026-04-12",
      "description": "PAGTO PIX MERCADO PAO",
      "accountType": "CHECKING_ACCOUNT",
      "isBusinessAccount": false,
      "paymentData": {
        "payer": {
          "document": "12345678900"
        },
        "receiver": {
          "document": "11222333000182"
        }
      },
      "creditCardMcc": 5411
    }
  ]
}'
```

### Resposta 200

Resultados do enriquecimento, um por transação enviada.

```json
{
  "results": [
    {
      "id": "tx-001",
      "amount": -89.9,
      "date": "2026-04-12",
      "description": "Mercado Pão",
      "type": "DEBIT",
      "merchant": {
        "name": "Mercado Pão",
        "businessName": "Mercado Pão Ltda",
        "cnpj": "11.222.333/0001-82"
      },
      "category": "Eating out"
    }
  ]
}
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `401` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `429` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `500` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |

## POST /recurring-payments — Detectar pagamentos recorrentes

Detecta assinaturas, salários, contas (utilities) e outros movimentos de caixa repetitivos a partir das transações de um item. Regras de detecção: ao menos 3 ocorrências; cadência aproximadamente mensal dentro de uma janela de ±5 dias; variância de valor ≤ 10%; descrições são convertidas para minúsculas e têm caracteres especiais removidos antes do casamento. A resposta é um array de padrões recorrentes.

**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).

### Corpo da requisição

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `itemId` | `string (uuid)` | sim | Identificador primário do item cujas transações serão analisadas. |

### Exemplo de requisição

```bash
curl -X POST "https://api.malvo.io/recurring-payments" \
  -H "X-API-KEY: $MALVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "itemId": "aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
}'
```

### Resposta 200

Array de padrões de pagamento recorrente detectados.

```json
[
  {
    "description": "netflix",
    "averageAmount": -58.0,
    "occurrences": [
      "a8534c85-53ce-4f21-94d7-50e9d2ee4957",
      "05c693bf-c196-47ea-a28c-8251d6bb8a06",
      "ff9ed929-edc4-408c-a959-d51f79ab1814"
    ],
    "regularityScore": 0.97
  },
  {
    "description": "salario empresa xyz",
    "averageAmount": 7500.0,
    "occurrences": [
      "6ec156fe-e8ac-4d9a-a4b3-7770529ab01c",
      "123456bf-c196-47ea-a28c-8251d6bb8777",
      "abced929-edc4-408c-a959-d51f79ab1123"
    ],
    "regularityScore": 0.88
  }
]
```

### Erros

| Status | Descrição | `codeDescription` |
|---|---|---|
| `400` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `401` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `429` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
| `500` | Resposta de erro padrão. Aplica-se a 400 (requisição inválida), 401 (não autenticado), 429 (limite de taxa) e 500 (erro interno). | `INTERNAL_SERVER_ERROR` |
