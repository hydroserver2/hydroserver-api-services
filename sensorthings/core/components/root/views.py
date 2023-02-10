from ninja import Router
from ninja.security import django_auth
from django.conf import settings
from django.urls import reverse
from .schemas import ServerRootResponse


router = Router()


@router.get(
    '',
    # auth=django_auth,
    include_in_schema=False,
    by_alias=True,
    response=ServerRootResponse
)
def get_root(request):
    """
    Get SensorThings server capabilities.
    """

    host_url = request.get_host()
    response = {
        'server_settings': {
            'conformance': settings.ST_CONFORMANCE
        },
        'server_capabilities': [
            {
                'name': capability['NAME'],
                'url': host_url + reverse(f"api-{settings.ST_VERSION}:{capability['VIEW']}")
            } for capability in settings.ST_CAPABILITIES
        ]
    }

    return response
