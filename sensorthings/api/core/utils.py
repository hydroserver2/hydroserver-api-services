import inspect
from pydantic import BaseModel


def whitespace_to_none(value: str) -> str:
    """
    Validation for whitespace values.

    Checks if string values are blank or only whitespace and converts them to NoneType.

    :param value: The input value.
    :return value: The output value.
    """

    if hasattr(value, 'isspace') and (value == '' or value.isspace()):
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
