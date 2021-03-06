import pytest
import yaml
from django.conf import settings

from django_swagger_tester.case.base import SchemaCaseTester
from django_swagger_tester.exceptions import CaseError
from django_swagger_tester.utils import replace_refs


def loader(path):
    with open(settings.BASE_DIR + path, 'r') as f:
        return replace_refs(yaml.load(f, Loader=yaml.FullLoader))


schema = loader('/tests/drf_yasg_reference.yaml')


def test_schema_case_tester_on_reference_schema():
    """
    Runs schema test class on reference schema.

    The iteration is done to test all paths, status codes, and responses.
    """
    with pytest.raises(CaseError, match='The property `date_created` is not properly camelCased'):
        for key in schema['paths'].keys():
            for method in schema['paths'][key].keys():
                if 'responses' not in schema['paths'][key][method]:
                    continue
                for status_code in schema['paths'][key][method]['responses'].keys():
                    if 'schema' not in schema['paths'][key][method]['responses'][status_code]:
                        continue
                    SchemaCaseTester(
                        schema=schema['paths'][key][method]['responses'][status_code]['schema'],
                        key=f'path: {key}\nmethod: {method}',
                    )


def test_ignore_case():
    with pytest.raises(CaseError, match='The property `read_only_nullable` is not properly camelCased'):
        for key in schema['paths'].keys():
            for method in schema['paths'][key].keys():
                if 'responses' not in schema['paths'][key][method]:
                    continue
                for status_code in schema['paths'][key][method]['responses'].keys():
                    if 'schema' not in schema['paths'][key][method]['responses'][status_code]:
                        continue
                    SchemaCaseTester(
                        schema=schema['paths'][key][method]['responses'][status_code]['schema'],
                        key=f'path: {key}\nmethod: {method}',
                        ignore_case=['date_created', 'date_modified'],
                    )


class MockSettings:
    CASE = 'snake_case'


def test_schema_using_snake_case(monkeypatch):
    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    with pytest.raises(CaseError, match='The property `ownerAsString` is not properly snake_cased'):
        for key in schema['paths'].keys():
            for method in schema['paths'][key].keys():
                if 'responses' not in schema['paths'][key][method]:
                    continue
                for status_code in schema['paths'][key][method]['responses'].keys():
                    if 'schema' not in schema['paths'][key][method]['responses'][status_code]:
                        continue
                    SchemaCaseTester(schema=schema['paths'][key][method]['responses'][status_code]['schema'])


def test_skipped_case_check(caplog):
    SchemaCaseTester(schema={'type': 'string'})
    assert 'Skipping case check' in [record.message for record in caplog.records]


def test_nested_list(caplog):
    """
    This doesn't happen in our test-response schema, so testing it individually.
    """
    SchemaCaseTester(schema={'type': 'array', 'items': {'type': 'array', 'items': {'type': 'integer', 'example': 5}}})
    assert 'list -> list' in [record.message for record in caplog.records]
