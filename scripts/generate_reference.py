import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote


SPEC_DIR = 'openapi'
OUTPUT_DIR = 'docs/endpoints'
BASE_URL = 'https://api.malvo.io'
DOCS_URL = 'https://docs.malvo.io'
METHODS = ('get', 'put', 'post', 'patch', 'delete')
CREDENTIAL_PLACEHOLDERS = {'clientId': '<CLIENT_ID>', 'clientSecret': '<CLIENT_SECRET>'}
FORMAT_EXAMPLES = {
    'uuid': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'date-time': '2026-01-15T12:00:00.000Z',
    'date': '2026-01-15',
    'uri': 'https://your.app/callback',
    'url': 'https://your.app/callback',
    'email': 'user@example.com',
}
def load_specs(root):
    return [(path.stem, json.loads(path.read_text())) for path in sorted((Path(root) / SPEC_DIR).glob('*.json'))]


def iterate_operations(document):
    for path, item in document['paths'].items():
        for method, operation in item.items():
            if method in METHODS:
                yield method.upper(), path, item, operation


def operations(root):
    return [(name, method, path, operation) for name, document in load_specs(root) for method, path, _, operation in iterate_operations(document)]


def resolve(document, node):
    seen = set()
    while isinstance(node, dict) and '$ref' in node:
        reference = node['$ref']
        if reference in seen or not reference.startswith('#/'):
            raise ValueError(f'Unsupported reference: {reference}')
        seen.add(reference)
        node = document
        for part in reference[2:].split('/'):
            node = node[part.replace('~1', '/').replace('~0', '~')]
    return node


def schema_type(schema):
    kind = schema.get('type')
    if isinstance(kind, list):
        concrete = [value for value in kind if value != 'null']
        return concrete[0] if concrete else 'null'
    if kind:
        return kind
    if 'properties' in schema:
        return 'object'
    if 'items' in schema:
        return 'array'
    return None


def merge_examples(values):
    merged = {}
    for value in values:
        if not isinstance(value, dict):
            return value
        merged.update(value)
    return merged


def example_from_schema(document, schema, trail=()):
    if '$ref' in schema:
        if schema['$ref'] in trail:
            return {}
        return example_from_schema(document, resolve(document, schema), (*trail, schema['$ref']))
    if 'example' in schema:
        return schema['example']
    if isinstance(schema.get('examples'), list) and schema['examples']:
        return schema['examples'][0]
    if 'const' in schema:
        return schema['const']
    if schema.get('enum'):
        return schema['enum'][0]
    if 'default' in schema:
        return schema['default']
    if 'allOf' in schema:
        return merge_examples(example_from_schema(document, part, trail) for part in schema['allOf'])
    kind = schema_type(schema)
    if kind is None:
        for keyword in ('oneOf', 'anyOf'):
            if schema.get(keyword):
                return example_from_schema(document, schema[keyword][0], trail)
        return None
    if kind == 'object':
        properties = schema.get('properties', {})
        if properties:
            return {name: example_from_schema(document, value, trail) for name, value in properties.items()}
        if isinstance(schema.get('additionalProperties'), dict):
            return {'key': example_from_schema(document, schema['additionalProperties'], trail)}
        return {}
    if kind == 'array':
        return [example_from_schema(document, schema.get('items', {}), trail)]
    if kind == 'string':
        return FORMAT_EXAMPLES.get(schema.get('format'), 'string')
    if kind in ('integer', 'number'):
        return schema.get('minimum', 0)
    if kind == 'boolean':
        return True
    return None


def content_examples(document, content):
    if 'example' in content:
        return [(None, content['example'])]
    if content.get('examples'):
        return [(example.get('summary', name), example['value']) for name, example in ((name, resolve(document, value)) for name, value in content['examples'].items())]
    if 'schema' in content:
        return [(None, example_from_schema(document, content['schema']))]
    return []


def json_content(document, node):
    content = resolve(document, node).get('content', {})
    return content.get('application/json')


def type_label(document, schema):
    if '$ref' in schema:
        return schema['$ref'].rsplit('/', 1)[-1]
    kind = schema.get('type')
    if isinstance(kind, list):
        label = ' | '.join(kind)
    elif kind:
        label = kind
    elif schema.get('oneOf') or schema.get('anyOf'):
        label = ' | '.join(type_label(document, branch) for branch in schema.get('oneOf') or schema.get('anyOf'))
    elif schema.get('allOf'):
        label = ' & '.join(type_label(document, part) for part in schema['allOf'])
    else:
        label = schema_type(schema) or 'any'
    if schema_type(schema) == 'array' and 'items' in schema:
        label = label.replace('array', f'array<{type_label(document, schema["items"])}>')
    if schema.get('format'):
        label = f'{label} ({schema["format"]})'
    return label


def absolute_links(text):
    return re.sub(r'\]\((/[^)\s]*)\)', rf']({DOCS_URL}\1)', text)


def cell(text):
    return absolute_links(' '.join(str(text).split())).replace('|', '\\|') if text else ''


def describe_field(schema, description):
    parts = [description] if description else []
    if schema.get('enum'):
        parts.append('Valores: ' + ', '.join(f'`{value}`' for value in schema['enum']) + '.')
    if 'default' in schema:
        parts.append(f'Padrão: `{json.dumps(schema["default"], ensure_ascii=False)}`.')
    return cell(' '.join(parts))


def parameters(document, item, operation):
    merged = {}
    for parameter in [*item.get('parameters', []), *operation.get('parameters', [])]:
        parameter = resolve(document, parameter)
        merged[(parameter['name'], parameter['in'])] = parameter
    return list(merged.values())


def parameter_example(document, parameter):
    if 'example' in parameter:
        return parameter['example']
    if parameter.get('examples'):
        return resolve(document, next(iter(parameter['examples'].values())))['value']
    return example_from_schema(document, parameter.get('schema', {}))


def url_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def request_url(document, path, parameters_list):
    url = path
    query = []
    for parameter in parameters_list:
        value = url_value(parameter_example(document, parameter))
        if parameter['in'] == 'path':
            url = url.replace('{' + parameter['name'] + '}', quote(value, safe=''))
        elif parameter['in'] == 'query' and parameter.get('required'):
            query.append(f'{parameter["name"]}={quote(value, safe=",:")}')
    return BASE_URL + url + ('?' + '&'.join(query) if query else '')


def with_placeholders(value):
    if isinstance(value, dict):
        return {key: CREDENTIAL_PLACEHOLDERS[key] if key in CREDENTIAL_PLACEHOLDERS else with_placeholders(child) for key, child in value.items()}
    if isinstance(value, list):
        return [with_placeholders(child) for child in value]
    return value


def pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def curl(method, url, headers, body):
    lines = [f'curl -X {method} "{url}"']
    lines += [f'-H "{name}: {value}"' for name, value in headers]
    if body is not None:
        lines.append("-d '" + pretty(body).replace("'", "'\\''") + "'")
    return ' \\\n  '.join(lines)


def is_public(document, operation):
    return operation.get('security', document.get('security', [])) == []


def render_parameters(document, parameters_list):
    if not parameters_list:
        return []
    lines = ['### Parâmetros', '', '| Nome | Onde | Tipo | Obrigatório | Descrição |', '|---|---|---|---|---|']
    for parameter in parameters_list:
        schema = parameter.get('schema', {})
        required = 'sim' if parameter.get('required') else 'não'
        lines.append(f'| `{parameter["name"]}` | {parameter["in"]} | `{cell(type_label(document, schema))}` | {required} | {describe_field(resolve(document, schema), parameter.get("description"))} |')
    return lines + ['']


def object_fields(document, schema):
    schema = resolve(document, schema)
    properties = dict(schema.get('properties', {}))
    required = set(schema.get('required', []))
    for part in schema.get('allOf', []):
        nested_properties, nested_required = object_fields(document, part)
        properties.update(nested_properties)
        required |= nested_required
    return properties, required


def render_body(document, operation):
    body = resolve(document, operation['requestBody'])
    content = body.get('content', {}).get('application/json', {})
    lines = ['### Corpo da requisição', '']
    if body.get('description'):
        lines += [absolute_links(body['description']), '']
    properties, required = object_fields(document, content.get('schema', {}))
    if properties:
        lines += ['| Campo | Tipo | Obrigatório | Descrição |', '|---|---|---|---|']
        for name, schema in properties.items():
            flag = 'sim' if name in required else 'não'
            lines.append(f'| `{name}` | `{cell(type_label(document, schema))}` | {flag} | {describe_field(resolve(document, schema), resolve(document, schema).get("description") or schema.get("description"))} |')
        lines.append('')
    else:
        lines += [f'Schema: `{cell(type_label(document, content.get("schema", {})))}`. Veja o exemplo na requisição.', '']
    return lines


def render_request(document, method, path, item, operation):
    parameters_list = parameters(document, item, operation)
    url = request_url(document, path, parameters_list)
    headers = [] if is_public(document, operation) else [('X-API-KEY', '$MALVO_API_KEY')]
    headers += [(parameter['name'], url_value(parameter_example(document, parameter))) for parameter in parameters_list if parameter['in'] == 'header']
    bodies = [(None, None)]
    if 'requestBody' in operation:
        headers.append(('Content-Type', 'application/json'))
        bodies = content_examples(document, resolve(document, operation['requestBody']).get('content', {}).get('application/json', {}))
    lines = ['### Exemplo de requisição', '']
    for summary, body in bodies:
        if summary:
            lines += [f'**{summary}**', '']
        lines += ['```bash', curl(method, url, headers, with_placeholders(body) if body is not None else None), '```', '']
    return lines


def response_codes(document, operation):
    return [(code, resolve(document, response)) for code, response in operation.get('responses', {}).items()]


def render_success(document, operation):
    lines = []
    for code, response in response_codes(document, operation):
        if not code.startswith('2'):
            continue
        lines += [f'### Resposta {code}', '']
        if response.get('description'):
            lines += [absolute_links(response['description']), '']
        content = json_content(document, response)
        if content is None:
            lines += ['Sem corpo de resposta.', '']
            continue
        for summary, example in content_examples(document, content):
            if summary:
                lines += [f'**{summary}**', '']
            lines += ['```json', pretty(example), '```', '']
    return lines


def error_codes(document, response):
    content = json_content(document, response)
    if content is None:
        return []
    found = []
    for _, example in content_examples(document, content):
        code = example.get('codeDescription') if isinstance(example, dict) else None
        if code and code not in found:
            found.append(code)
    return found


def render_errors(document, operation):
    rows = [(code, response) for code, response in response_codes(document, operation) if not code.startswith('2')]
    if not rows:
        return []
    lines = ['### Erros', '', '| Status | Descrição | `codeDescription` |', '|---|---|---|']
    for code, response in rows:
        codes = ', '.join(f'`{value}`' for value in error_codes(document, response))
        lines.append(f'| `{code}` | {cell(response.get("description"))} | {codes} |')
    return lines + ['']


def render_operation(document, method, path, item, operation):
    lines = [f'## {method} {path} — {operation.get("summary", operation.get("operationId", ""))}', '']
    if operation.get('deprecated'):
        lines += ['> **Depreciada.**', '']
    if operation.get('description'):
        lines += [absolute_links(operation['description']), '']
    if is_public(document, operation):
        lines += ['**Autenticação:** nenhuma. Esta rota não usa o header `X-API-KEY`.', '']
    else:
        lines += ['**Autenticação:** header `X-API-KEY` com a `apiKey` obtida em `POST /auth` (TTL de 2 horas).', '']
    lines += render_parameters(document, parameters(document, item, operation))
    if 'requestBody' in operation:
        lines += render_body(document, operation)
    lines += render_request(document, method, path, item, operation)
    lines += render_success(document, operation)
    lines += render_errors(document, operation)
    return lines


def render(name, document):
    info = document.get('info', {})
    entries = list(iterate_operations(document))
    lines = [
        f'# {info.get("title", name)}',
        '',
        f'> Gerado a partir de `{SPEC_DIR}/{name}.json` por `scripts/generate_reference.py`. Não edite à mão.',
        '',
    ]
    if info.get('description'):
        lines += [absolute_links(info['description']), '']
    lines += [
        f'- Base URL: `{BASE_URL}`',
        '- Autenticação: troque `clientId` e `clientSecret` por uma `apiKey` em `POST /auth` e envie-a no header `X-API-KEY` (TTL de 2 horas). Faça isso só no servidor.',
        '- Formato: JSON (`Content-Type: application/json`).',
        '- Erros: envelope `GlobalErrorResponse` (`code`, `message`, `codeDescription`). Veja [a visão geral](../overview.md).',
        '',
        '## Operações',
        '',
    ]
    lines += [f'- `{method} {path}` — {operation.get("summary", "")}' for method, path, _, operation in entries]
    lines.append('')
    for method, path, item, operation in entries:
        lines += render_operation(document, method, path, item, operation)
    return '\n'.join(lines).rstrip('\n') + '\n'


def render_all(root):
    return {f'{OUTPUT_DIR}/{name}.md': render(name, document) for name, document in load_specs(root)}


def section(markdown, method, path):
    match = re.search(rf'^## {method} {re.escape(path)} .*?(?=^## |\Z)', markdown, re.M | re.S)
    return match.group(0) if match else None


def has_success_example(document, operation):
    return any(code.startswith('2') and json_content(document, response) is not None for code, response in response_codes(document, operation))


def missing_operations(root, documents):
    missing = []
    for name, document in load_specs(root):
        markdown = documents.get(f'{OUTPUT_DIR}/{name}.md', '')
        for method, path, _, operation in iterate_operations(document):
            text = section(markdown, method, path)
            complete = text is not None and '```bash\ncurl -X ' + method + ' "' in text
            if complete and has_success_example(document, operation):
                complete = '```json\n' in text.split('### Erros')[0]
            if not complete:
                missing.append(f'{method} {path}')
    return missing


def json_type_matches(kind, value):
    if kind == 'null':
        return value is None
    if kind == 'boolean':
        return isinstance(value, bool)
    if kind == 'integer':
        return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value).is_integer()
    if kind == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == 'string':
        return isinstance(value, str)
    if kind == 'array':
        return isinstance(value, list)
    if kind == 'object':
        return isinstance(value, dict)
    raise ValueError(f'Unsupported type: {kind}')


def same_value(left, right):
    return type(left) is type(right) and left == right or json_type_matches('number', left) and json_type_matches('number', right) and left == right


def schema_errors(document, schema, value, location='$'):
    if isinstance(schema, bool):
        return [] if schema else [f'{location}: valor proibido pelo schema']
    if '$ref' in schema:
        return schema_errors(document, resolve(document, schema), value, location)
    errors = []
    kinds = schema.get('type')
    if kinds is not None:
        kinds = kinds if isinstance(kinds, list) else [kinds]
        if not any(json_type_matches(kind, value) for kind in kinds):
            return [f'{location}: tipo esperado {" | ".join(kinds)}']
    if 'enum' in schema and not any(same_value(option, value) for option in schema['enum']):
        errors.append(f'{location}: valor fora do enum: {json.dumps(value, ensure_ascii=False)}')
    if 'const' in schema and not same_value(schema['const'], value):
        errors.append(f'{location}: valor diferente de const: {json.dumps(schema["const"], ensure_ascii=False)}')
    if json_type_matches('number', value):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{location}: valor menor que {schema["minimum"]}')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{location}: valor maior que {schema["maximum"]}')
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        errors += [f'{location}: campo obrigatório ausente: {name}' for name in schema.get('required', []) if name not in value]
        for name, child in value.items():
            if name in properties:
                errors += schema_errors(document, properties[name], child, f'{location}.{name}')
            elif schema.get('additionalProperties') is False:
                errors.append(f'{location}: propriedade não permitida: {name}')
            elif isinstance(schema.get('additionalProperties'), dict):
                errors += schema_errors(document, schema['additionalProperties'], child, f'{location}.{name}')
    if isinstance(value, list) and 'items' in schema:
        for index, child in enumerate(value):
            errors += schema_errors(document, schema['items'], child, f'{location}[{index}]')
    for part in schema.get('allOf', []):
        errors += schema_errors(document, part, value, location)
    if 'anyOf' in schema and not any(not schema_errors(document, part, value, location) for part in schema['anyOf']):
        errors.append(f'{location}: nenhuma alternativa de anyOf corresponde')
    if 'oneOf' in schema:
        matches = sum(1 for part in schema['oneOf'] if not schema_errors(document, part, value, location))
        if matches == 0:
            errors.append(f'{location}: nenhuma alternativa de oneOf corresponde')
        elif matches > 1:
            errors.append(f'{location}: mais de uma alternativa de oneOf corresponde')
    if 'not' in schema and not schema_errors(document, schema['not'], value, location):
        errors.append(f'{location}: valor proibido por not')
    return errors


def documented_examples(specs):
    for _, document in specs:
        for method, path, _, operation in iterate_operations(document):
            targets = []
            if 'requestBody' in operation:
                targets.append(('requisição', resolve(document, operation['requestBody']).get('content', {}).get('application/json')))
            targets += [(code, json_content(document, response)) for code, response in response_codes(document, operation)]
            for label, content in targets:
                if content is None or 'schema' not in content:
                    continue
                for summary, example in content_examples(document, content):
                    yield document, f'{method} {path} {label}' + (f' ({summary})' if summary else ''), content['schema'], example


def invalid_examples(specs):
    return [f'{name}: {error}' for document, name, schema, example in documented_examples(specs) for error in schema_errors(document, schema, example)]


def main():
    parser = argparse.ArgumentParser(description='Gera a referência Markdown dos endpoints a partir das specs OpenAPI.')
    parser.add_argument('--check', action='store_true', help='Falha se os arquivos gerados estiverem desatualizados.')
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    documents = render_all(root)
    output = root / OUTPUT_DIR
    stale = sorted(set(path.relative_to(root).as_posix() for path in output.glob('*.md')) - set(documents))
    changed = [name for name, content in documents.items() if not (root / name).exists() or (root / name).read_text() != content]
    invalid = invalid_examples(load_specs(root))
    for error in invalid:
        print(f'Exemplo incompatível com o schema: {error}', file=sys.stderr)
    if arguments.check:
        for name in changed + stale:
            print(f'Desatualizado: {name}', file=sys.stderr)
        return 1 if changed or stale or invalid else 0
    if invalid:
        return 1
    output.mkdir(parents=True, exist_ok=True)
    for name in stale:
        (root / name).unlink()
    for name in changed:
        (root / name).write_text(documents[name])
    return 0


if __name__ == '__main__':
    sys.exit(main())
