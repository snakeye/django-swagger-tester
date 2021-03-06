"""
This file should contain a collection of schema-parsing utility functions.

While this package should never become an OpenAPI schema parser,
it is useful for us to apply the rules of the schema specification
in case we're ever dealt with an incorrect schema.

Instead of raising unhandled errors, it is useful for us to raise appropriate exceptions.
"""
import logging
from typing import List

from django_swagger_tester.exceptions import OpenAPISchemaError, SwaggerDocumentationError

logger = logging.getLogger('django_swagger_tester')


def read_items(array: dict) -> dict:
    """
    Accesses the `items` attribute of an array.

    Rule: `items – must be present if type is array. The item schema must be an OpenAPI schema and not a standard JSON`
    https://swagger.io/docs/specification/data-models/keywords/

    :param array: schema array
    :return: array items
    :raises: django_swagger_tester.exceptions.OpenAPISchemaError
    """
    if 'items' not in array:
        raise OpenAPISchemaError(f'Array is missing an `items` attribute.\n\nArray schema: {array}')
    return array['items']


def list_types() -> List[str]:
    """
    Returns supported item types.
    """
    return ['string', 'boolean', 'integer', 'number', 'file', 'object', 'array']


def read_type(item: dict) -> str:
    """
    Accesses the `items` attribute of a schema item.

    Rule: `type – the value must be a single type and not an array of types.
            null is not supported as a type, use the`nullable: true keyword instead.`

    :param item: schema item
    :return: schema item type
    :raises: django_swagger_tester.exceptions.OpenAPISchemaError
    """
    if (
        item is None
        or not isinstance(item, dict)
        or 'type' not in item
        or not item['type']
        or not isinstance(item['type'], str)
    ):
        raise OpenAPISchemaError(
            f'Schema item has an invalid `type` attribute. The type should be a single string.\n\nSchema item: {item}'
        )
    if not item['type'] in list_types():
        raise OpenAPISchemaError(
            f'Schema item has an invalid `type` attribute. '
            f'The type `{item["type"]}` is not supported.\n\nSchema item: {item}'
        )
    return item['type']


def read_additional_properties(schema_object: dict) -> dict:
    """
    Accesses the `additionalProperties` attribute of a schema object.

    :param schema_object: schema object (dict)
    :return: schema object additional properties
    :raises: django_swagger_tester.exceptions.OpenAPISchemaError
    """
    if 'additionalProperties' not in schema_object:
        raise OpenAPISchemaError(
            f'Object is missing a `additionalProperties` attribute.\n\nObject schema: {schema_object}'
        )
    return schema_object['additionalProperties']


def read_properties(schema_object: dict) -> dict:
    """
    Accesses the `properties` attribute of a schema object.

    :param schema_object: schema object (dict)
    :return: schema object properties
    :raises: django_swagger_tester.exceptions.OpenAPISchemaError
    """
    if 'properties' not in schema_object:
        if 'additionalProperties' in schema_object:
            # We return this with an empty key, so we can still iterate over the results .items(), as we would with
            # normal properties
            return {'': read_additional_properties(schema_object)}
        raise OpenAPISchemaError(f'Object is missing a `properties` attribute.\n\nObject schema: {schema_object}')
    return schema_object['properties']


def is_nullable(schema_item: dict) -> bool:
    """
    Checks if the item is nullable.

    OpenAPI does not have a null type, like a JSON schema,
    but in OpenAPI 3.0 they added `nullable: true` to specify that the value may be null.
    Note that null is different from an empty string "".

    This feature was back-ported to the Swagger 2 parser as a vendored extension `x-nullable`. This is what drf_yasg generates.

    OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
    Swagger 2 ref: https://help.apiary.io/api_101/swagger-extensions/

    :param schema_item: schema item
    :return: whether or not the item can be None
    """
    openapi_schema_3_nullable = 'nullable'
    swagger_2_nullable = 'x-nullable'
    for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]:
        if schema_item and isinstance(schema_item, dict):
            if nullable_key in schema_item:
                if isinstance(schema_item[nullable_key], str):
                    if schema_item[nullable_key] == 'true':
                        return True
    return False


def index_schema(schema: dict, variable: str, error_addon: str = None) -> dict:
    """
    Indexes schema by string variable.

    :param schema: Schema to index
    :param variable: Variable to index by
    :param error_addon: Additional error info
    :return: Indexed schema
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
    """
    if error_addon is None:
        error_addon = ''
    try:
        logger.debug('Indexing schema by `%s`', variable)
        return schema[f'{variable}']
    except KeyError:
        raise SwaggerDocumentationError(
            f'Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `{variable}`.'
            + error_addon
        )
