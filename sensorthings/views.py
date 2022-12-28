from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.contrib.admin.views.decorators import staff_member_required


api = NinjaAPI(
    title='HydroServer SensorThings API',
    version='1.1',
    description='''
        The HydroServer API can be used to create and update monitoring site metadata, and post  
        results data to HydroServer data stores.
    ''',
    csrf=True,
    docs_decorator=staff_member_required
)


@api.get(
    '/Things({thing_id})/',
    auth=django_auth,
    tags=['Things']
)
def get_thing(request, thing_id: str):
    """"""

    return {}
