import importlib.util
import json
from pathlib import Path
import copy
import re
import unittest


ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('generate_reference', ROOT / 'scripts' / 'generate_reference.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CONTEXT7_FIELDS = {'$schema', 'projectTitle', 'description', 'branch', 'folders', 'excludeFolders', 'excludeFiles', 'rules', 'disallow', 'redirect', 'previousVersions', 'url', 'public_key'}
PUBLISHED_FILES = ['README.md', 'context7.json', *sorted(str(path.relative_to(ROOT)) for folder in ('docs', 'openapi') for path in (ROOT / folder).rglob('*') if path.is_file())]
ALLOWED_HOSTS = {'api.malvo.io', 'docs.malvo.io', 'malvo.io', 'context7.com', 'nubank.com.br', 'your.app', 'api.your-app.com', 'auth.example', 'files.example.com'}
SECRET_PATTERN = re.compile(r'sk_[A-Za-z0-9]|pk_[A-Za-z0-9]|whsec_[A-Za-z0-9]|Bearer ey|AKIA[0-9A-Z]{12}|-----BEGIN [A-Z ]*KEY-----')
INFRASTRUCTURE_PATTERN = re.compile(r'://localhost|localhost:\d|staging|amazonaws|\baws\b|\becs\b|pulumi|\bsqs\b|railway|infraestrutura|\bworker\b|mocks? locais|analysis api', re.I)
CPF_PATTERN = re.compile(r'(?<![\d/-])(?<!\d\.)(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?![\d/-]|\.\d)')
CNPJ_PATTERN = re.compile(r'(?<![\d/-])(?<!\d\.)(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})(?![\d/-]|\.\d)')


def check_digits(digits, weight_sets):
    numbers = [int(digit) for digit in digits]
    for weights in weight_sets:
        remainder = sum(number * weight for number, weight in zip(numbers, weights)) % 11
        numbers.append(0 if remainder < 2 else 11 - remainder)
    return numbers[-len(weight_sets):]


def is_valid_cpf(value):
    digits = re.sub(r'\D', '', value)
    weight_sets = (range(10, 1, -1), range(11, 1, -1))
    return len(set(digits)) > 1 and check_digits(digits[:9], weight_sets) == [int(digit) for digit in digits[9:]]


def is_valid_cnpj(value):
    digits = re.sub(r'\D', '', value)
    weight_sets = ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    return len(set(digits)) > 1 and check_digits(digits[:12], weight_sets) == [int(digit) for digit in digits[12:]]


def valid_documents(text):
    cnpjs = [match.group(0) for match in CNPJ_PATTERN.finditer(text) if is_valid_cnpj(match.group(0))]
    cpfs = [match.group(0) for match in CPF_PATTERN.finditer(text) if is_valid_cpf(match.group(0))]
    return cnpjs + cpfs


def committed_documents():
    return {path.relative_to(ROOT).as_posix(): path.read_text() for path in sorted((ROOT / module.OUTPUT_DIR).glob('*.md'))}


def remove_section(markdown, method, path):
    pattern = re.compile(rf'^## {method} {re.escape(path)} .*?(?=^## |\Z)', re.M | re.S)
    result, count = pattern.subn('', markdown)
    if count != 1:
        raise AssertionError(f'Section {method} {path} not found')
    return result


def spec_documents():
    return copy.deepcopy(module.load_specs(ROOT))


def success_example(documents, name, path, method):
    document = dict(documents)[name]
    return document['paths'][path][method]['responses']['200']['content']['application/json']['example']


class GeneratedReferenceTests(unittest.TestCase):
    def test_specs_declare_47_operations(self):
        self.assertEqual(len(module.operations(ROOT)), 47)

    def test_committed_files_match_the_generator(self):
        self.assertEqual(committed_documents(), module.render_all(ROOT))

    def test_every_operation_has_a_section_with_curl_and_success_example(self):
        self.assertEqual(module.missing_operations(ROOT, committed_documents()), [])

    def test_removed_section_is_reported(self):
        documents = committed_documents()
        name = f'{module.OUTPUT_DIR}/accounts.md'
        documents[name] = remove_section(documents[name], 'GET', '/accounts/{id}/balance')
        self.assertEqual(module.missing_operations(ROOT, documents), ['GET /accounts/{id}/balance'])

    def test_section_without_curl_is_reported(self):
        documents = committed_documents()
        name = f'{module.OUTPUT_DIR}/webhooks.md'
        documents[name] = documents[name].replace('curl -X POST "https://api.malvo.io/webhooks"', 'POST https://api.malvo.io/webhooks')
        self.assertEqual(module.missing_operations(ROOT, documents), ['POST /webhooks'])

    def test_public_route_has_no_api_key(self):
        section = module.section(committed_documents()[f'{module.OUTPUT_DIR}/auth.md'], 'POST', '/auth')
        self.assertNotIn('X-API-KEY: $MALVO_API_KEY', section)
        self.assertIn('"clientSecret": "<CLIENT_SECRET>"', section)

    def test_protected_route_sends_api_key_placeholder(self):
        section = module.section(committed_documents()[f'{module.OUTPUT_DIR}/items.md'], 'GET', '/items/{id}')
        self.assertIn('-H "X-API-KEY: $MALVO_API_KEY"', section)

    def test_every_spec_uses_only_the_public_server(self):
        for name, document in module.load_specs(ROOT):
            with self.subTest(spec=name):
                self.assertEqual([server['url'] for server in document.get('servers', [])], [module.BASE_URL])


class ExampleSchemaTests(unittest.TestCase):
    def test_every_documented_example_matches_its_schema(self):
        self.assertEqual(module.invalid_examples(module.load_specs(ROOT)), [])

    def test_counts_every_request_and_response_example(self):
        self.assertEqual(len(list(module.documented_examples(module.load_specs(ROOT)))), 186)

    def test_example_without_required_field_is_reported(self):
        documents = spec_documents()
        del success_example(documents, 'accounts', '/accounts/{id}', 'get')['createdAt']
        self.assertEqual(module.invalid_examples(documents), ['GET /accounts/{id} 200: $: campo obrigatório ausente: createdAt'])

    def test_nested_example_without_required_field_is_reported(self):
        documents = spec_documents()
        del success_example(documents, 'accounts', '/bills', 'get')['results'][0]['financeCharges'][0]['creditCardBillId']
        self.assertEqual(module.invalid_examples(documents), ['GET /bills 200: $.results[0].financeCharges[0]: campo obrigatório ausente: creditCardBillId'])

    def test_example_outside_enum_is_reported(self):
        documents = spec_documents()
        success_example(documents, 'investments-loans-identity', '/loans', 'get')['results'][0]['installments']['typeNumberOfInstallments'] = 'UNKNOWN'
        self.assertEqual(module.invalid_examples(documents), ['GET /loans 200: $.results[0].installments.typeNumberOfInstallments: valor fora do enum: "UNKNOWN"'])

    def test_loan_installment_units_accept_pt_and_en_in_their_own_field(self):
        documents = spec_documents()
        installments = success_example(documents, 'investments-loans-identity', '/loans', 'get')['results'][0]['installments']
        accepted = {
            'typeNumberOfInstallments': ['DAY', 'WEEK', 'MONTH', 'YEAR', 'WITHOUT_TOTAL_PERIOD', 'DIA', 'SEMANA', 'MES', 'ANO', 'SEM_PRAZO_TOTAL'],
            'typeContractRemaining': ['DAY', 'WEEK', 'MONTH', 'YEAR', 'WITHOUT_REMAINING_PERIOD', 'WITHOUT_TOTAL_PERIOD', 'DIA', 'SEMANA', 'MES', 'ANO', 'SEM_PRAZO_REMANESCENTE'],
        }
        for field, values in accepted.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    installments[field] = value
                    self.assertEqual(module.invalid_examples(documents), [])
            installments[field] = 'MONTH'

    def test_loan_installment_sentinel_from_the_other_field_is_reported(self):
        cases = [('typeNumberOfInstallments', 'SEM_PRAZO_REMANESCENTE'), ('typeNumberOfInstallments', 'WITHOUT_REMAINING_PERIOD'), ('typeContractRemaining', 'SEM_PRAZO_TOTAL')]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                documents = spec_documents()
                success_example(documents, 'investments-loans-identity', '/loans', 'get')['results'][0]['installments'][field] = value
                self.assertEqual(module.invalid_examples(documents), [f'GET /loans 200: $.results[0].installments.{field}: valor fora do enum: "{value}"'])

    def test_loan_detail_documents_canonical_and_legacy_installment_units(self):
        reference = (ROOT / 'docs' / 'endpoints' / 'investments-loans-identity.md').read_text()
        detail = module.section(reference, 'GET', '/loans/{id}')
        self.assertIn('Operação gravada ou atualizada após a transição (inglês)', detail)
        self.assertIn('Registro legado ainda não atualizado (português, descontinuado)', detail)
        self.assertIn('"typeNumberOfInstallments": "MONTH"', detail)
        self.assertIn('"typeNumberOfInstallments": "MES"', detail)
        self.assertIn('Aceite os dois valores na leitura', detail)

    def test_example_with_wrong_type_is_reported(self):
        documents = spec_documents()
        success_example(documents, 'transactions', '/transactions/{id}', 'get')['amount'] = '-212.45'
        self.assertEqual(module.invalid_examples(documents), ['GET /transactions/{id} 200: $.amount: tipo esperado number'])

    def test_invalid_request_example_is_reported(self):
        documents = spec_documents()
        dict(documents)['transactions']['paths']['/transactions/{id}']['patch']['requestBody']['content']['application/json']['example'] = {'categoryId': 7010000}
        self.assertEqual(module.invalid_examples(documents), ['PATCH /transactions/{id} requisição: $.categoryId: tipo esperado string'])


class SchemaValidatorTests(unittest.TestCase):
    def errors(self, schema, value, components=None):
        return module.schema_errors({'components': {'schemas': components or {}}}, schema, value)

    def test_accepts_nullable_type_list(self):
        self.assertEqual(self.errors({'type': ['string', 'null']}, None), [])

    def test_distinguishes_integer_number_and_boolean(self):
        self.assertEqual(self.errors({'type': 'integer'}, 1.5), ['$: tipo esperado integer'])
        self.assertEqual(self.errors({'type': 'number'}, True), ['$: tipo esperado number'])
        self.assertEqual(self.errors({'type': 'integer'}, 2.0), [])

    def test_resolves_local_references(self):
        components = {'Item': {'type': 'object', 'required': ['id'], 'properties': {'id': {'type': 'string'}}}}
        self.assertEqual(self.errors({'type': 'array', 'items': {'$ref': '#/components/schemas/Item'}}, [{'id': 'a'}, {}], components), ['$[1]: campo obrigatório ausente: id'])

    def test_rejects_additional_properties_when_forbidden(self):
        self.assertEqual(self.errors({'type': 'object', 'properties': {'a': {}}, 'additionalProperties': False}, {'a': 1, 'b': 2}), ['$: propriedade não permitida: b'])

    def test_one_of_requires_exactly_one_match(self):
        schema = {'oneOf': [{'type': 'string'}, {'type': 'string', 'enum': ['x']}]}
        self.assertEqual(self.errors(schema, 1), ['$: nenhuma alternativa de oneOf corresponde'])
        self.assertEqual(self.errors(schema, 'x'), ['$: mais de uma alternativa de oneOf corresponde'])
        self.assertEqual(self.errors(schema, 'y'), [])

    def test_checks_all_of_any_of_not_const_and_bounds(self):
        self.assertEqual(self.errors({'allOf': [{'required': ['a']}, {'required': ['b']}]}, {'a': 1}), ['$: campo obrigatório ausente: b'])
        self.assertEqual(self.errors({'anyOf': [{'type': 'string'}, {'type': 'null'}]}, 1), ['$: nenhuma alternativa de anyOf corresponde'])
        self.assertEqual(self.errors({'not': {'type': 'null'}}, None), ['$: valor proibido por not'])
        self.assertEqual(self.errors({'const': 'a'}, 'b'), ['$: valor diferente de const: "a"'])
        self.assertEqual(self.errors({'minimum': 1, 'maximum': 3}, 0), ['$: valor menor que 1'])
        self.assertEqual(self.errors({'minimum': 1, 'maximum': 3}, 4), ['$: valor maior que 3'])


class DocumentValidatorTests(unittest.TestCase):
    def test_detects_valid_cpf_and_cnpj_in_both_formats(self):
        self.assertEqual(valid_documents('CPF 529.982.247-25 e CNPJ 11.222.333/0001-81'), ['11.222.333/0001-81', '529.982.247-25'])
        self.assertEqual(valid_documents('52998224725,11222333000181'), ['11222333000181', '52998224725'])

    def test_ignores_invalid_documents_and_other_numbers(self):
        self.assertEqual(valid_documents('cpf 12345678900, cnpj 11222333000180, valor 1700000000, conta 0001234567890, 11111111111'), [])


class PublishedContentTests(unittest.TestCase):
    def test_published_files_have_no_secret(self):
        for name in PUBLISHED_FILES:
            with self.subTest(file=name):
                self.assertIsNone(SECRET_PATTERN.search((ROOT / name).read_text()))

    def test_published_files_have_no_valid_cpf_or_cnpj(self):
        for name in PUBLISHED_FILES:
            with self.subTest(file=name):
                self.assertEqual(valid_documents((ROOT / name).read_text()), [])

    def test_published_files_use_only_reserved_email_domains(self):
        for name in PUBLISHED_FILES:
            with self.subTest(file=name):
                for domain in re.findall(r'[\w.+-]+@([\w-]+(?:\.[\w-]+)+)', (ROOT / name).read_text()):
                    self.assertEqual(domain, 'example.com')

    def test_published_files_link_only_to_public_hosts(self):
        for name in PUBLISHED_FILES:
            with self.subTest(file=name):
                hosts = set(re.findall(r'https?://([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*)', (ROOT / name).read_text()))
                self.assertLessEqual(hosts, ALLOWED_HOSTS)

    def test_published_files_do_not_describe_infrastructure(self):
        for name in PUBLISHED_FILES:
            with self.subTest(file=name):
                self.assertIsNone(INFRASTRUCTURE_PATTERN.search((ROOT / name).read_text()))


class Context7ConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'context7.json').read_text())

    def test_uses_only_schema_fields_within_limits(self):
        self.assertLessEqual(set(self.config), CONTEXT7_FIELDS)
        self.assertEqual(self.config['$schema'], 'https://context7.com/schema/context7.json')
        self.assertEqual(self.config['projectTitle'], 'Malvo API')
        self.assertEqual(self.config['branch'], 'main')
        self.assertTrue(10 <= len(self.config['description']) <= 500)
        for field, limit in (('folders', 50), ('excludeFolders', 50), ('excludeFiles', 100), ('rules', 50)):
            values = self.config[field]
            self.assertLessEqual(len(values), limit)
            self.assertEqual(len(values), len(set(values)))
            self.assertTrue(all(1 <= len(value) <= 255 for value in values))

    def test_indexes_the_markdown_and_excludes_tooling(self):
        self.assertEqual(self.config['folders'], ['docs'])
        self.assertTrue((ROOT / 'docs' / 'overview.md').exists())
        self.assertLessEqual({'tests', 'scripts'}, set(self.config['excludeFolders']))


if __name__ == '__main__':
    unittest.main()
