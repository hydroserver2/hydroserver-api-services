import inspect
import inflection
import sensorthings.core.schemas as core_schemas
import sensorthings.core.components as core_components
from typing import Literal
from pydantic import BaseModel
from django.conf import settings


def nested_entities_check(value, field):
    """
    Validation for nested components.

    Runs validation on nested components in request bodies to avoid circular relationships in the API documentation.

    :param value: The input value.
    :param field: The field being validated.
    :return value: The output value.
    """

    nested_class_name = field.field_info.extra.get('nested_class')

    if nested_class_name:
        nested_class = getattr(core_components, nested_class_name)

        if isinstance(value, list):
            value = [
                nested_class(**sub_value.dict()) if isinstance(sub_value, core_schemas.NestedEntity) else sub_value
                for sub_value in value
            ]

        elif isinstance(value, core_schemas.NestedEntity):
            value = nested_class(**value.dict())

    return value


def whitespace_to_none(value):
    """
    Validation for whitespace values.

    Checks if string values are blank or only whitespace and converts them to NoneType.

    :param value: The input value.
    :return value: The output value.
    """

    if isinstance(value, str) and (value == '' or value.isspace()):
        return None

    return value


def allow_partial(*fields):
    """
    Declares fields of a Pydantic model as optional.

    This decorator can be used to update required fields of a Pydantic model to be optional. This can be used in
    conjunction with exclude_unset to allow for missing fields, but still adhere to not_null requirements, such as when
    partially updating a datastore.

    :param fields: All fields which should be made optional. If none are passed, all fields will be made optional.
    :return dec: The optional class decorator.
    """

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)

    return dec


def lookup_component(
        input_value: str,
        input_type: Literal['snake_singular', 'snake_plural', 'camel_singular', 'camel_plural'],
        output_type: Literal['snake_singular', 'snake_plural', 'camel_singular', 'camel_plural']
) -> str:
    """
    Accepts a component value and type and attempts to return an alternate form of the component name.

    :param input_value: The name of the component to lookup.
    :param input_type: The type of the component to lookup.
    :param output_type: The type of the component to return.
    :return output_value: The matching component name.
    """

    st_components = [
        {
            'snake_singular': inflection.underscore(capability['SINGULAR_NAME']),
            'snake_plural': inflection.underscore(capability['NAME']),
            'camel_singular': capability['SINGULAR_NAME'],
            'camel_plural': capability['NAME']
        } for capability in settings.ST_CAPABILITIES
    ]

    return next((c[output_type] for c in st_components if c[input_type] == input_value))


def list_response_codes(response_schema):
    """"""

    return {
        200: response_schema
    }


def get_response_codes(response_schema):
    """"""

    return {
        200: response_schema,
        404: core_schemas.EntityNotFound
    }


def entity_or_404(response, entity_id):
    """"""

    if response:
        return 200, response
    else:
        return 404, {'message': f'Record with ID {entity_id} does not exist.'}
