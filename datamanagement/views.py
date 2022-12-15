from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.contrib.admin.views.decorators import staff_member_required


api = NinjaAPI(
    title='HIS Server Data Management API',
    version='1.0.0',
    description='''
        The HIS Server Data Management API can be used to create and update monitoring site metadata, and post  
        results data to HIS Server data stores.
    ''',
    csrf=True,
    docs_decorator=staff_member_required
)


@api.post(
    '/{datastore_name}/result-values/',
    auth=django_auth,
    tags=['Result Values']
)
def result_values_post(request, datastore_name: str):
    """
    Endpoint for posting result values.

    This endpoint accepts a JSON object containing result values and will initiate a data loading task to load the data
    into an HIS Server data store.
    """

    return {}


@api.post(
    '/{datastore_name}/result-values-file/',
    auth=django_auth,
    tags=['Result Values']
)
def result_values_file_post(request, datastore_name: str, file: UploadedFile = File(...)):
    """
    Endpoint for posting result values files.

    This endpoint accepts a file containing result values and will initiate a bulk data loading task to load the data
    into an HIS Server data store.
    """

    file.read()

    return {}


@api.get(
    '/{datastore_name}/result-values-file/{task_id}/',
    auth=django_auth,
    tags=['Result Values']
)
def result_values_file_status(request, datastore_name: str, task_id: str):
    """
    Endpoint for getting result values file loading status.

    This endpoint accepts a task ID which will be used to check the status of a bulk data loading task.
    """

    return {}
