from copy import deepcopy
from sensorthings.core.utils import lookup_component


def build_api_extension(api, title, namespace, schemas):
    """
    Clones an existing Django Ninja API object and modifies the new APIs data schemas.

    :param api: A Django Ninja API object to extend.
    :param title: The title of the new API.
    :param namespace: The namespace of the new API. Must not overlap with any existing namespace.
    :param schemas: The schemas used to modify the existing API.
    :return: A new Django Ninja API object.
    """

    # TODO This solution is pretty janky, but it's the most straightforward way to get this functionality at the moment.

    new_api = deepcopy(api)

    for router in new_api._routers:
        try:
            component = router[1].tags[0].replace(' ', '')
        except TypeError:
            continue

        for path_op in router[1].path_operations.values():
            for op in path_op.operations:
                get_response_schema_name = f'{lookup_component(component, "camel_plural", "camel_singular")}GetResponse'

                if hasattr(schemas, get_response_schema_name):
                    get_response_schema = getattr(schemas, get_response_schema_name)
                    if 200 in op.response_models:
                        op.response_models[200] = get_response_schema

    new_api.urls_namespace = f'{namespace}-1.1'
    new_api.title = title

    return new_api
