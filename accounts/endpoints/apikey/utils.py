def build_api_key_response(api_key, api_key_value=None):
    return {
        'id': api_key.id,
        'name': api_key.name,
        'scope': api_key.scope,
        'permissions': api_key.permissions,
        **({'key': api_key_value} if api_key_value is not None else {})
    }
