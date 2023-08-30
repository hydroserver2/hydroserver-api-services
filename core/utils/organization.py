def organization_to_dict(organization):
    return {
        "id": organization.id,
        "code": organization.code,
        "name": organization.name,
        "description": organization.description,
        "type": organization.type,
        "link": organization.link,
    }
