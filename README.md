# malvo-api-docs

Documentação pública da API Malvo em Markdown, indexada pelo [Context7](https://context7.com).

A documentação completa, com guias e referência interativa, fica em https://docs.malvo.io.

## Conteúdo

- `docs/overview.md`: base URL, autenticação, paginação, erros, rate limit e webhooks.
- `docs/endpoints/<grupo>.md`: referência de cada endpoint, com requisição `curl` e resposta JSON. Gerado a partir de `openapi/`; não edite à mão.
- `openapi/*.json`: specs OpenAPI públicas da API.
- `context7.json`: configuração do Context7.

## Regerar a referência

Requer Python 3, sem dependências.

```bash
python3 scripts/generate_reference.py          # regrava docs/endpoints/
python3 scripts/generate_reference.py --check  # falha se docs/endpoints/ estiver desatualizado
```

Os dois comandos também falham se algum exemplo JSON (requisição ou resposta) violar o schema da operação: campos obrigatórios, tipos, enums, `const`, limites numéricos e `oneOf`/`anyOf`/`allOf`/`not`, com resolução dos `$ref` locais.

## Testes

```bash
python3 -m unittest discover -s tests
```
