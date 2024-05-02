import json


def build_api_key_response(api_key, api_key_value=None):
    return {
        'id': api_key.id,
        'name': api_key.name,
        'scope': api_key.scope,
        'permissions': json.loads(api_key.permissions),
        'last_used': api_key.last_used,
        'enabled': api_key.enabled,
        **({'key': api_key_value} if api_key_value is not None else {})
    }
