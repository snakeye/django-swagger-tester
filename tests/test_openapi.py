import pytest

from django_swagger_tester.exceptions import OpenAPISchemaError
from django_swagger_tester.openapi import (
    read_items,
    list_types,
    read_type,
    read_properties,
    is_nullable,
    read_additional_properties,
)


def test_read_items():
    """
    Ensure this helper function works as it's designed to.
    """
    assert read_items({'items': 'test'}) == 'test'
    with pytest.raises(OpenAPISchemaError, match='Array is missing an `items` attribute'):
        read_items({'no-items': 'woops'})


def test_list_types():
    """
    Ensure this helper function works as it's designed to.
    """
    assert [i in list_types() for i in ['string', 'boolean', 'integer', 'number', 'file', 'object', 'array']]
    assert len(list_types()) == 7


def test_read_type():
    """
    Ensure this helper function works as it's designed to.
    """
    e = 'Schema item has an invalid `type` attribute. The type should be a single string'
    with pytest.raises(OpenAPISchemaError, match=e):
        read_type('test')

    e = 'Schema item has an invalid `type` attribute. The type `bad type` is not supported.'
    with pytest.raises(OpenAPISchemaError, match=e):
        read_type({'type': 'bad type'})

    assert read_type({'type': 'string'}) == 'string'


example = {
    'title': 'Other stuff',
    'description': 'the decorator should determine the serializer class for this',
    'required': ['foo'],
    'type': 'object',
    'properties': {'foo': {'title': 'Foo', 'type': 'string', 'minLength': 1}},
}

additional_example = {
    'title': 'Other stuff',
    'description': 'the decorator should determine the serializer class for this',
    'required': ['foo'],
    'type': 'object',
    'additionalProperties': {'title': 'Foo', 'type': 'string', 'minLength': 1},
}


def test_read_read_properties():
    """
    This function is a bit funny, and I'm not sure it will work in practice. Essentially, we're trying to handle
    the edge case of getting `additionalProperties`, by making it look like a `properties` object.
    This way we can apply the same testing logic on both objects.
    """
    assert read_properties(example) == {'foo': {'title': 'Foo', 'type': 'string', 'minLength': 1}}
    assert read_properties(additional_example) == {'': {'title': 'Foo', 'type': 'string', 'minLength': 1}}
    with pytest.raises(OpenAPISchemaError):
        read_properties({})


def test_additional_properties_validation():
    with pytest.raises(OpenAPISchemaError):
        read_additional_properties({})


nullable_example = {
    'properties': {
        'id': {'title': 'ID', 'type': 'integer', 'readOnly': 'true', 'x-nullable': 'true',},
        'first_name': {
            'title': 'First name',
            'type': 'string',
            'maxLength': '30',
            'minLength': '1',
            'nullable': 'true',
        },
    }
}

nullable_example_data = {'id': None, 'first_name': None}


def test_is_nullable():
    """
    Ensure this helper function works as it's designed to.
    """
    assert is_nullable(nullable_example['properties']['id']) == True
    assert is_nullable(nullable_example['properties']['first_name']) == True
    for item in [2, '', None, -1, {'nullable': 'false'}]:
        assert is_nullable(item) == False
