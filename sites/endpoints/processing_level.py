from ninja import Router, Schema
from sites.models import ProcessingLevel, Unit
from sites.utils.authentication import jwt_auth
from django.db.models import Q
from django.http import JsonResponse
from sites.utils.processing_level import processing_level_to_dict

router = Router()


class ProcessingLevelInput(Schema):
    processing_level_code: str
    definition: str
    explanation: str


@router.post('', auth=jwt_auth)
def create_processing_level(request, data: ProcessingLevelInput):
    processing_level = ProcessingLevel.objects.create(
        person=request.authenticated_user,
        processing_level_code=data.processing_level_code,
        definition=data.definition,
        explanation=data.explanation,
    )

    return JsonResponse(processing_level_to_dict(processing_level))


@router.get('', auth=jwt_auth)
def get_processing_levels(request):
    processing_levels = ProcessingLevel.objects.filter(Q(person=request.authenticated_user) | Q(person__isnull=True))
    return JsonResponse([processing_level_to_dict(pl) for pl in processing_levels], safe=False)



@router.patch('/{processing_level_id}', auth=jwt_auth)
def update_processing_level(request, processing_level_id: str, data: ProcessingLevelInput):
    processing_level = ProcessingLevel.objects.get(id=processing_level_id)
    if request.authenticated_user != processing_level.person:
        return JsonResponse({'detail': 'You are not authorized to update this processing level.'}, status=403)

    if data.processing_level_code is not None:
        processing_level.processing_level_code = data.processing_level_code
    if data.definition is not None:
        processing_level.definition = data.definition
    if data.explanation is not None:
        processing_level.explanation = data.explanation

    processing_level.save()

    return JsonResponse(processing_level_to_dict(processing_level))


@router.delete('/{processing_level_id}', auth=jwt_auth)
def delete_processing_level(request, processing_level_id: str):
    try:
        pl = ProcessingLevel.objects.get(id=processing_level_id)
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'processing level not found.'}, status=404)

    if request.authenticated_user != pl.person:
        return JsonResponse({'detail': 'You are not authorized to delete this unit.'}, status=403)

    pl.delete()
    return {'detail': 'Processing level deleted successfully.'}